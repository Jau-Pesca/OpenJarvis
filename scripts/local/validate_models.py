"""Real local-model decisions; no desktop action or personal-memory write."""
import json
import tempfile
import time
import threading
from types import SimpleNamespace
from pathlib import Path
from openjarvis.agents.business import BusinessAgent
from openjarvis.agents._stubs import AgentContext, AgentResult
from openjarvis.agents.task_runtime import TaskManager
from openjarvis.engine.ollama import OllamaEngine

with tempfile.TemporaryDirectory(prefix='jarvis-model-check-') as folder:
    agent = BusinessAgent(OllamaEngine(host='http://127.0.0.1:11434'), 'qwen3.5:9b', graph_path=Path(folder)/'test.db')
    for text, action in [('Bom dia!', 'reply'), ('Abra o Mercado Livre.', 'delegate')]:
        started = time.monotonic()
        answer = agent.chat(text, context=AgentContext(metadata={'computer': {'available': True, 'browser_running': True}}))
        decision = answer.metadata['decision']
        print(json.dumps({'request': text, 'decision': decision, 'seconds': round(time.monotonic()-started,2)}, ensure_ascii=False), flush=True)
        assert decision['action'] == action, decision
        assert type(decision.get('requires_execution')) is bool, decision
        if action == 'delegate':
            assert decision['requires_execution'] is True, decision
            received, event = [], threading.Event()
            def simulated_worker(query, context=None, **kwargs):
                received.append((query, context.metadata))
                event.set()
                return AgentResult(content='Execução simulada apenas para conferir o protocolo.', metadata={'error': True})
            manager = TaskManager(SimpleNamespace(chat=lambda *args, **kwargs: answer,
                                  run=simulated_worker, _model=agent._model))
            manager.desktop = None
            try:
                manager.message(text, 'model-validation')
                assert event.wait(3), 'Tarefa não chegou ao executor simulado'
                assert text in received[0][0], received[0][0]
                assert received[0][1]['requires_execution'] is True
                print('PASS: pedido original preservado na fila simulada.', flush=True)
            finally:
                manager.close()
                manager.worker.join(3)
print('PASS: decisões reais; nenhuma tarefa executada.')
