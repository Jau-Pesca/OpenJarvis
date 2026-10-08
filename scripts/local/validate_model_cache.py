"""Explicit two-request cache probe; never run as part of startup."""
import json
import time
from datetime import datetime, timezone

import httpx
from openjarvis.core.types import Message, Role
from openjarvis.engine.ollama import OllamaEngine

engine = OllamaEngine(host='http://127.0.0.1:11434')
model = 'qwen3.5:4b'
measurements = []
try:
    for turn in range(2):
        if turn:
            time.sleep(2)
        engine.generate([Message(role=Role.USER, content='Responda somente: OK.')],
                        model=model, max_tokens=8, num_ctx=8192, temperature=0)
        response = engine._client.get('/api/ps')
        response.raise_for_status()
        resident = next(m for m in response.json()['models'] if m['name'] == model)
        expiry = datetime.fromisoformat(resident['expires_at'].replace('Z', '+00:00'))
        seconds = (expiry - datetime.now(timezone.utc)).total_seconds()
        assert 270 < seconds <= 310, f'Unexpected idle timeout: {seconds}'
        measurements.append({'turn': turn + 1, 'model': model,
                             'idle_seconds_remaining': round(seconds, 1),
                             'expires_at': expiry.isoformat()})
    assert measurements[1]['expires_at'] > measurements[0]['expires_at'], 'Idle deadline was not renewed'
    print(json.dumps({'cache_probe': measurements, 'result': 'PASS',
                      'note': 'Model left resident for normal idle expiration; no forced unload.'}))
finally:
    engine._client.close()
