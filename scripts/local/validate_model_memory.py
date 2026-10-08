"""Inspect local work/residency, optionally select an already-installed model."""
import argparse
import json
from pathlib import Path
import httpx

parser = argparse.ArgumentParser()
parser.add_argument('--select', help='Select an installed model without loading it via the UI API')
args = parser.parse_args()
state = json.loads((Path.home()/'OpenJarvis-local/interface.json').read_text())
with httpx.Client(base_url=f"http://127.0.0.1:{state['api_port']}", timeout=180, trust_env=False) as api:
    tasks = api.get('/v1/business-tasks/status')
    tasks.raise_for_status()
    call = api.get('/v1/local-call/status')
    call.raise_for_status()
    data = tasks.json()
    active_tasks = [t for t in data['tasks'] if t['state'] in {'queued', 'running', 'redirecting'}]
    pending = [m for m in data['messages'] if m['state'] == 'pending']
    print(json.dumps({'active_tasks': len(active_tasks), 'pending_dialogues': len(pending),
        'call_active': call.json()['active'], 'call_model': call.json()['model']}, ensure_ascii=False), flush=True)
    if args.select:
        available = api.get('/v1/models')
        available.raise_for_status()
        assert args.select in [m['id'] for m in available.json()['data']], 'Model must already be installed'
        response = api.post('/v1/models/select', json={'model': args.select})
        response.raise_for_status()
        print(json.dumps({'selection': response.json()}, ensure_ascii=False), flush=True)
with httpx.Client(base_url='http://127.0.0.1:11434', timeout=10, trust_env=False) as ollama:
    response = ollama.get('/api/ps')
    response.raise_for_status()
    models = response.json()['models']
    print(json.dumps({'resident_models': [{'name': m['name'], 'GiB': round(m['size']/1024**3, 2)} for m in models],
        'total_GiB': round(sum(m['size'] for m in models)/1024**3, 2)}, ensure_ascii=False), flush=True)
