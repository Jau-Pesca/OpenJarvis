"""Execution failures must stop physical work and preserve truthful results."""
import json
import time
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

from openjarvis.agents._stubs import AgentContext, AgentResult
from openjarvis.agents.business import BusinessAgent
from openjarvis.agents.task_runtime import TaskManager
from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec


class Engine:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.calls = 0

    def generate(self, messages, **kwargs):
        self.calls += 1
        reply = next(self.replies)
        return reply if 'tool_calls' in reply else {'content': json.dumps(reply)}


class DesktopTool(BaseTool):
    tool_id = 'computer_step'

    def __init__(self, result):
        self.result, self.calls = result, 0

    @property
    def spec(self):
        return ToolSpec(name=self.tool_id, description='Desktop test', parameters={'type': 'object', 'properties': {}})

    def execute(self, **kwargs):
        self.calls += 1
        return self.result


def agent_for(tmp_path, monkeypatch, tool, replies):
    engine = Engine([{'notes': []}, {'tasks': [{'role': 'operacoes', 'task': 'Execute'}]}, *replies])
    agent = BusinessAgent(engine, 'test', graph_path=tmp_path / 'graph.db')
    monkeypatch.setattr(agent, '_tools', lambda: [tool])
    return agent, engine


def test_permission_failure_stops_batch_and_next_model_turn(tmp_path, monkeypatch):
    details = 'Native permission diagnostic ' * 80
    message = 'Preciso que você libere a Acessibilidade do JarvisMacControl.'
    tool = DesktopTool(ToolResult(tool_name='computer_step', content=details, success=False,
                       metadata={'retryable': False, 'error_code': 'accessibility_permission_required', 'user_message': message}))
    call = {'name': 'computer_step', 'arguments': '{}'}
    agent, engine = agent_for(tmp_path, monkeypatch, tool, [{'tool_calls': [call, call]}, {'tool_calls': [call]}])
    outcome = agent._run('Execute', AgentContext(metadata={'requires_execution': True}))
    assert tool.calls == 1
    assert engine.calls == 3
    assert outcome.content == message
    assert outcome.metadata['error'] is True
    assert outcome.metadata['error_details'] == details
    assert outcome.tool_results[0].success is False


def test_successful_step_with_failed_review_is_not_completed_task(tmp_path, monkeypatch):
    tool = DesktopTool(ToolResult(tool_name='computer_step', content='Cursor moved, target not reached', success=True, metadata={'action': 'move'}))
    agent, _ = agent_for(tmp_path, monkeypatch, tool, [
        {'tool_calls': [{'name': 'computer_step', 'arguments': '{}'}]}, {'content': 'Moved'},
        {'ok': False, 'issues': ['Requested page was not observed'], 'retry_task': ''}, {'content': 'Tried opening'},
    ])
    outcome = agent._run('Execute', AgentContext(metadata={'requires_execution': True}))
    assert outcome.metadata['error'] is True
    assert outcome.metadata['execution_status'] == 'attempted'


def test_runtime_keeps_short_failure_and_full_diagnostics(monkeypatch):
    monkeypatch.delenv('OJ_DESKTOP_CONTROL', raising=False)
    details = 'Technical evidence ' * 100
    agent = SimpleNamespace(run=lambda *args, **kwargs: AgentResult(content='Permissão necessária.', metadata={'error': True, 'error_details': details}))
    manager = TaskManager(agent)
    try:
        manager.submit('Execute', 'voice')
        deadline = time.monotonic() + 2
        while manager.snapshot()[0]['state'] != 'error' and time.monotonic() < deadline:
            time.sleep(.01)
        task = manager.snapshot()[0]
        assert task['error'] == 'Permissão necessária.'
        assert task['error_details'] == details
        assert task['result'] == ''
    finally:
        manager.close()
        manager.worker.join(2)


class TerminalFailureTests(unittest.TestCase):
    def test_permission_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            test_permission_failure_stops_batch_and_next_model_turn(Path(directory), SimpleNamespace(setattr=setattr))

    def test_unverified_step(self):
        with tempfile.TemporaryDirectory() as directory:
            test_successful_step_with_failed_review_is_not_completed_task(Path(directory), SimpleNamespace(setattr=setattr))

    def test_runtime_diagnostic(self):
        with patch.dict('os.environ'):
            test_runtime_keeps_short_failure_and_full_diagnostics(SimpleNamespace(delenv=lambda key, raising=False: __import__('os').environ.pop(key, None)))

    def test_permission_failure_on_last_turn(self):
        with tempfile.TemporaryDirectory() as directory:
            tool = DesktopTool(ToolResult(tool_name='computer_step', content='Blocked', success=False,
                               metadata={'retryable': False, 'user_message': 'Libere a permissão.'}))
            agent, _ = agent_for(Path(directory), SimpleNamespace(setattr=setattr), tool,
                                 [{'tool_calls': [{'name': 'computer_step', 'arguments': '{}'}]}])
            agent._turn_budget = 1
            outcome = agent._run('Execute', AgentContext(metadata={'requires_execution': True}))
            self.assertTrue(outcome.metadata['error'])
            self.assertEqual(tool.calls, 1)

    def test_transient_failure_allows_model_to_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            tool = DesktopTool(ToolResult(tool_name='computer_step', content='Transient error', success=False))
            agent, engine = agent_for(Path(directory), SimpleNamespace(setattr=setattr), tool, [
                {'tool_calls': [{'name': 'computer_step', 'arguments': '{}'}]},
                {'tool_calls': [{'name': 'computer_step', 'arguments': '{}'}]}, {'content': 'Failed'},
            ])
            outcome = agent._run('Execute', AgentContext(metadata={'requires_execution': True}))
            self.assertEqual(tool.calls, 2)
            self.assertEqual(engine.calls, 5)
            self.assertTrue(outcome.metadata['error'])

    def test_permission_failure_during_repair_is_terminal(self):
        with tempfile.TemporaryDirectory() as directory:
            tool = DesktopTool(ToolResult(tool_name='computer_step', content='Permission evidence', success=False,
                               metadata={'retryable': False, 'user_message': 'Libere a permissão.'}))
            agent, engine = agent_for(Path(directory), SimpleNamespace(setattr=setattr), tool, [
                {'content': 'No evidence'},
                {'ok': False, 'issues': ['Missing evidence'], 'retry_task': 'Try one step'},
                {'tool_calls': [{'name': 'computer_step', 'arguments': '{}'}]},
            ])
            outcome = agent._run('Execute', AgentContext())
            self.assertEqual(outcome.content, 'Libere a permissão.')
            self.assertEqual(outcome.metadata['error_details'], 'Permission evidence')
            self.assertEqual(tool.calls, 1)
            self.assertEqual(engine.calls, 5)

    def test_delegation_preserves_original_request_and_execution_guard(self):
        captured = []
        agent = SimpleNamespace(chat=lambda *args, **kwargs: AgentResult(content='Vou abrir.', metadata={
            'decision': {'action': 'delegate', 'reply': 'Vou abrir.', 'task': 'abrir_site'}}),
            run=lambda text, context=None, **kwargs: captured.append((text, context.metadata)) or AgentResult(content='Falha', metadata={'error': True}))
        with patch.dict('os.environ'):
            __import__('os').environ.pop('OJ_DESKTOP_CONTROL', None)
            manager = TaskManager(agent)
            try:
                manager.message('Abra o Mercado Livre.', 'voice')
                deadline = time.monotonic() + 2
                while not captured and time.monotonic() < deadline:
                    time.sleep(.01)
                self.assertTrue(captured)
                self.assertIn('Abra o Mercado Livre.', captured[0][0])
                self.assertIn('abrir_site', captured[0][0])
                self.assertTrue(captured[0][1]['requires_execution'])
                self.assertEqual(manager.snapshot()[0]['query'], 'Abra o Mercado Livre.')
            finally:
                manager.close()
                manager.worker.join(2)

    def test_synchronous_delegation_keeps_original_and_summary_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            agent = BusinessAgent(Engine([]), 'test', graph_path=Path(directory) / 'graph.db')
            decision = {'action': 'delegate', 'task': 'abrir_site'}
            with patch.object(agent, 'chat', return_value=AgentResult(content='Vou abrir.', metadata={'decision': decision})), patch.object(agent, 'run_task', return_value=AgentResult(content='Simulated')) as execute:
                agent.run('Abra o Mercado Livre.')
            args = execute.call_args.args
            self.assertEqual(args[0], 'Abra o Mercado Livre.')
            self.assertEqual(args[1].metadata['delegated_goal'], 'abrir_site')
            self.assertIs(args[1].metadata['requires_execution'], True)
