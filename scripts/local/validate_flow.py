"""Real principal -> mailbox -> specialist -> desktop -> reviewer validation.

Uses temporary personal memory and prints only stages and execution receipts.
"""
import json
import tempfile
import time
from pathlib import Path
from openjarvis.agents.business import BusinessAgent
from openjarvis.agents.task_runtime import TaskManager
from openjarvis.engine.ollama import OllamaEngine

session = 'real-flow-validation'
with tempfile.TemporaryDirectory(prefix='jarvis-real-flow-') as folder:
    agent = BusinessAgent(OllamaEngine(host='http://127.0.0.1:11434', timeout=180), 'qwen3.5:9b', graph_path=Path(folder)/'memory.db', max_turns=6)
    manager = TaskManager(agent)
    task_id = None
    try:
        started = time.monotonic()
        request = manager.message('Abra o Mercado Livre.',session)
        deadline = started+240
        prior = None
        while time.monotonic()<deadline:
            messages = manager.dialogue_snapshot(session)
            if messages:
                message = messages[-1]
                if message['state'] == 'error':
                    raise RuntimeError(message['error'])
                if message['state'] == 'done' and task_id is None:
                    task_id = message.get('task_id')
                    print('PRINCIPAL',json.dumps({'reply':message['result'],'seconds':round(time.monotonic()-started,2),'delegated':bool(task_id)},ensure_ascii=False),flush=True)
                    assert task_id, 'O principal não delegou'
            tasks = manager.snapshot(session)
            if tasks:
                task = tasks[-1]
                status=(task['state'],task['stage'])
                if status != prior:
                    print('TASK_STAGE',json.dumps(status,ensure_ascii=False),flush=True)
                    prior=status
                if task['state'] in {'done','error','cancelled'}:
                    print('TASK_RESULT',json.dumps({k:task.get(k) for k in ('state','result','error','error_details')},ensure_ascii=False),flush=True)
                    assert task['state']=='done', 'A tarefa não comprovou conclusão'
                    print('FLOW_SECONDS',round(time.monotonic()-started,2),flush=True)
                    break
            time.sleep(.25)
        else:
            raise TimeoutError('Fluxo real excedeu240 segundos; cancelando a tarefa')
        from openjarvis.tools.mac_desktop import chrome
        url=chrome('tell application "Google Chrome"\nreturn URL of active tab of front window\nend tell')
        assert url=='https://www.mercadolivre.com.br/', 'A guia final diverge da página inicial'
        print('PASS: fluxo completo real e URL final correta; memória pessoal temporária.',flush=True)
    finally:
        if task_id:
            task = next((t for t in manager.snapshot(session) if t['id']==task_id),None)
            if task and task['state'] in {'queued','running','redirecting'}:
                manager.cancel(task_id,session)
        manager.close()
        manager.worker.join(10)
