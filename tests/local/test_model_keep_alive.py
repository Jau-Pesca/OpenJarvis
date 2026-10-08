"""Exercise real HTTP serialization for all three inference entry points."""
import asyncio
import json
import unittest

import httpx
from openjarvis.core.types import Message, Role
from openjarvis.engine.ollama import OllamaEngine


class KeepAliveTests(unittest.TestCase):
    def test_all_inference_paths_request_idle_cache_and_preserve_overrides(self):
        async def run():
            requests = []
            def handler(request):
                payload = json.loads(request.content)
                requests.append(payload)
                data = {'message': {'role': 'assistant', 'content': 'Olá'}, 'done': True}
                if payload['stream']:
                    return httpx.Response(200, content=json.dumps(data)+'\n')
                return httpx.Response(200, json=data)
            engine = OllamaEngine(host='http://local')
            engine._client.close()
            engine._client = httpx.Client(base_url='http://local', transport=httpx.MockTransport(handler))
            async_client = httpx.AsyncClient(base_url='http://local', transport=httpx.MockTransport(handler))
            engine._get_async_client = lambda: async_client
            messages = [Message(role=Role.USER, content='Olá')]
            try:
                for overrides, expected in (({}, '5m'), ({'keep_alive': '10m'}, '10m'), ({'keep_alive': 0}, 0)):
                    engine.generate(messages, model='test', **overrides)
                    self.assertEqual(''.join([part async for part in engine.stream(messages, model='test', **overrides)]), 'Olá')
                    self.assertTrue([part async for part in engine.stream_full(messages, model='test', **overrides)])
                    for payload in requests[-3:]:
                        self.assertEqual(payload['keep_alive'], expected)
                        self.assertNotIn('keep_alive', payload['options'])
            finally:
                engine._client.close()
                await async_client.aclose()
        asyncio.run(run())
