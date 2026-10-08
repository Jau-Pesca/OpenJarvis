import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from openjarvis.agents._stubs import AgentResult, AgentContext
from openjarvis.agents.business import BusinessAgent
from openjarvis.agents.task_runtime import TaskManager, ControlledEngine, TaskInterrupted


class PlanTests(unittest.TestCase):
    def test_schema_repair_and_no_duplicate_memory_lookup(self):
        with tempfile.TemporaryDirectory() as folder:
            agent = BusinessAgent(Mock(), 'test', tools=[], graph_path=str(Path(folder)/'graph.db'))
            agent._extract = Mock()
            agent._ask = Mock(side_effect=['{"action":"delegate"}', '{"tasks":[{"role":"operacoes","task":"Abra o site"}]}', '{"ok":true,"issues":[],"retry_task":""}', 'Concluído'])
            with patch('openjarvis.agents.business.OrchestratorAgent') as specialist:
                specialist.return_value.run.return_value = AgentResult(content='Observado')
                agent._run('Abra o site', AgentContext(metadata={'notes_processed': True}))
            agent._extract.assert_not_called()
            schema = agent._ask.call_args_list[0].kwargs['structured']['json_schema']['schema']
            self.assertEqual(schema['properties']['tasks']['minItems'], 1)
            self.assertIn('correcao_de_formato', agent._ask.call_args_list[1].args[1])
            specialist.assert_called_once()

    def test_invalid_plan_stops_after_one_repair_without_tools(self):
        with tempfile.TemporaryDirectory() as folder:
            agent = BusinessAgent(Mock(), 'test', tools=[], graph_path=str(Path(folder)/'graph.db'))
            agent._extract = Mock()
            agent._ask = Mock(return_value='{"tasks":[{"role":{},"task":"bad"}]}')
            with patch('openjarvis.agents.business.OrchestratorAgent') as specialist:
                result = agent._run('Abra o site', AgentContext())
            agent._extract.assert_called_once()
            self.assertEqual(agent._ask.call_count, 2)
            self.assertEqual(result.metadata['error_code'], 'invalid_plan')
            specialist.assert_not_called()

    def test_approved_review_summary_does_not_call_rewriter(self):
        with tempfile.TemporaryDirectory() as folder:
            agent = BusinessAgent(Mock(), 'test', tools=[], graph_path=str(Path(folder)/'graph.db'))
            agent._extract = Mock()
            agent._ask = Mock(side_effect=['{"tasks":[{"role":"operacoes","task":"Veja o resultado"}]}', '{"ok":true,"issues":[],"retry_task":"","summary":"Resultado conferido."}'])
            with patch('openjarvis.agents.business.OrchestratorAgent') as specialist:
                specialist.return_value.run.return_value = AgentResult(content='Resultado observado')
                result = agent._run('Veja o resultado', AgentContext(metadata={'notes_processed': True}))
            self.assertEqual(result.content, 'Resultado conferido.')
            self.assertEqual(agent._ask.call_count, 2)


class TraceTests(unittest.TestCase):
    def test_blocked_inference_failure_stage_and_persistent_sanitized_events(self):
        entered, release = threading.Event(), threading.Event()
        with tempfile.TemporaryDirectory() as folder:
            def run(query, context=None, **kwargs):
                context.metadata['task_control'].progress('Planejando')
                def generate(*args, **kwargs):
                    entered.set(); release.wait(2)
                    raise ValueError('SECRET OUTPUT')
                ControlledEngine(SimpleNamespace(generate=generate), context.metadata['task_control']).generate('SECRET PROMPT', model='test')
            agent = SimpleNamespace(run=run, graph=SimpleNamespace(path=Path(folder)/'graph.db'), _model='test')
            manager = TaskManager(agent)
            try:
                submitted = manager.submit('SECRET USER')
                self.assertTrue(entered.wait(1))
                current = manager.snapshot()[0]
                self.assertEqual(current['events'][-1]['status'], 'started')
                self.assertEqual(current['events'][-1]['model'], 'test')
                release.set()
                for _ in range(100):
                    task = manager.snapshot()[0]
                    if task['state'] == 'error': break
                    time.sleep(.01)
                self.assertEqual(task['failure_stage'], 'Planejando')
                self.assertTrue(any(e.get('duration_ms') is not None for e in task['events']))
                self.assertNotIn('SECRET', json.dumps(task['events']))
                saved = manager.trace_path.read_text()
                self.assertNotIn('SECRET', saved)
                events = list(task['events'])
            finally:
                release.set(); manager.close(); manager.worker.join(2)
            other = TaskManager(SimpleNamespace(run=Mock(), graph=agent.graph))
            try:
                self.assertEqual(other.read_events(submitted['task_id']), events)
            finally:
                other.close(); other.worker.join(2)

    def test_cancel_rejects_late_progress(self):
        entered, release = threading.Event(), threading.Event()
        def run(query, context=None):
            control = context.metadata['task_control']
            entered.set(); release.wait(2)
            control.progress('LATE')
            return AgentResult(content='obsolete')
        manager = TaskManager(SimpleNamespace(run=run))
        try:
            task = manager.submit('test')
            self.assertTrue(entered.wait(1))
            manager.cancel(task['task_id'], 'chat'); release.set()
            time.sleep(.02)
            snapshot = manager.snapshot()[0]
            self.assertEqual(snapshot['state'], 'cancelled')
            self.assertNotIn('LATE', json.dumps(snapshot['events']))
        finally:
            release.set(); manager.close(); manager.worker.join(2)


class TraceCorruptionTests(unittest.TestCase):
    def test_non_object_and_invalid_lines_are_skipped(self):
        with tempfile.TemporaryDirectory() as folder:
            manager = TaskManager(SimpleNamespace(run=Mock(), graph=SimpleNamespace(path=Path(folder)/'graph.db')))
            try:
                manager.trace_path.parent.mkdir()
                manager.trace_path.write_text('[]\nnull\nINVALID\n'+json.dumps({'task_id':'test','stage':'Planejando'})+'\n')
                self.assertEqual(manager.read_events('test'), [{'task_id':'test','stage':'Planejando'}])
                manager.trace_path.write_bytes(b'\xff')
                with self.assertRaisesRegex(ValueError, 'histórico'):
                    manager.read_events('test')
            finally:
                manager.close(); manager.worker.join(2)
