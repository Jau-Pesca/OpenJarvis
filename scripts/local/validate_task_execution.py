"""Explicit real browser-task probe with sanitized phase/timing output."""
import json
import time
import uuid
from pathlib import Path
import httpx

state = json.loads((Path.home()/'OpenJarvis-local/interface.json').read_text())
base = f"http://127.0.0.1:{state['api_port']}"
started = time.monotonic()
session = 'diagnostics-'+uuid.uuid4().hex
with httpx.Client(base_url=base, timeout=15, trust_env=False) as client:
    status = client.get('/v1/business-tasks/status').json()
    assert not any(t['state'] in {'running','queued','redirecting'} for t in status['tasks'])
    assert not client.get('/v1/local-call/status').json()['active']
    response = client.post('/v1/business-tasks/submit', json={'text': 'Abra o Mercado Livre em uma nova guia do Chrome. Verifique que chegou ao site.', 'session':session, 'model':'qwen3.5:4b'})
    response.raise_for_status()
    message_id = response.json()['message_id']
    task = None
    last = None
    for _ in range(360):
        data = client.get('/v1/business-tasks/status', params={'session':session}).json()
        message = next(m for m in data['messages'] if m['id']==message_id)
        tasks = data['tasks']
        if tasks: task = tasks[-1]
        stage = task['stage'] if task else message.get('stage',message['state'])
        if stage != last:
            print(json.dumps({'seconds':round(time.monotonic()-started,1),'stage':stage},ensure_ascii=False),flush=True)
            last=stage
        if task and task['state'] in {'error','done','cancelled'}:
            print(json.dumps({'result':task['state'],'elapsed_seconds':task['elapsed_seconds'], 'failure_stage':task.get('failure_stage'), 'model_calls':sum(e['kind']=='model' and e.get('status')=='started' for e in task.get('events',[])), 'tool_attempts':sum(e['kind']=='tool' and e.get('status')=='started' for e in task.get('events',[])), 'phase_durations':[{'stage':e['stage'],'seconds':round(e['duration_ms']/1000,2)} for e in task.get('events',[]) if e['kind']=='stage' and e.get('duration_ms',0)>0], 'recovered_failures':[e.get('error_code') for e in task.get('events',[]) if e['kind']=='tool' and e.get('status')=='error'], 'usage':task['usage']},ensure_ascii=False),flush=True)
            assert task['state']=='done', 'Task failed: '+task.get('error','')
            assert any(e.get('tool')=='computer_step' and e.get('status')=='done' for e in task['events']), 'No successful desktop tool'
            break
        if message['state']=='error':raise RuntimeError('Principal failed: '+message['error'])
        if message['state']=='done' and not tasks:raise RuntimeError('Principal did not delegate requested execution')
        time.sleep(1)
    else:raise TimeoutError('Task still running after six minutes; inspect status/events')
