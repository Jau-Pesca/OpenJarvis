import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from openjarvis.agents.business import BusinessAgent
from openjarvis.server.routes import list_models


class Engine:
    engine_id = 'ollama'
    _host = 'http://127.0.0.1:11434'

    def __init__(self):
        self.models_used = []

    def list_models(self):
        return ['qwen3.5:9b', 'qwen3.5:4b', 'another:8b', 'nomic-embed-text']

    def generate(self, messages, *, model, **kwargs):
        self.models_used.append(model)
        return {'content': json.dumps({'action': 'reply', 'reply': 'Olá.', 'requires_execution': False})}


class SelectionTests(unittest.TestCase):
    def test_installed_models_not_restricted_to_default_role(self):
        state = SimpleNamespace(engine=Engine(), agent=SimpleNamespace(agent_id='business'))
        request = SimpleNamespace(app=SimpleNamespace(state=state))
        with patch.dict(os.environ, {'OJ_MAIN_MODEL': 'qwen3.5:9b'}):
            result = asyncio.run(list_models(request))
        self.assertEqual([m.id for m in result.data], ['qwen3.5:9b', 'qwen3.5:4b', 'another:8b'])

    def test_explicit_chat_selection_wins_and_temp_remains_independent(self):
        engine = Engine()
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {
            'OJ_MAIN_MODEL': 'qwen3.5:9b', 'OJ_TEMP_MODEL': 'qwen3.5:4b',
        }):
            agent = BusinessAgent(engine, 'qwen3.5:9b', graph_path=Path(folder)/'graph.db')
            answer = agent.chat('Olá', model='another:8b')
            self.assertEqual(answer.content, 'Olá.')
            self.assertEqual(engine.models_used, ['another:8b'])
            explicit = BusinessAgent(engine, 'another:8b', graph_path=Path(folder)/'graph.db')
            self.assertEqual(explicit._model, 'another:8b')
            self.assertEqual(explicit._temp_model, 'qwen3.5:4b')
            default = BusinessAgent(engine, None, graph_path=Path(folder)/'graph.db')
            self.assertEqual(default._model, 'qwen3.5:9b')

    def test_preload_uses_configured_ollama_host_without_browser_cors(self):
        from openjarvis.server.routes import preload_model
        state = SimpleNamespace(engine=Engine())
        request = SimpleNamespace(app=SimpleNamespace(state=state), json=AsyncMock(return_value={'model': 'qwen3.5:4b'}))
        import httpx
        response = httpx.Response(200, json={'done': True}, request=httpx.Request('POST', 'http://127.0.0.1:11434/api/generate'))
        client = Mock()
        client.__enter__ = Mock(return_value=client)
        client.__exit__ = Mock(return_value=False)
        client.post.return_value = response
        with patch('httpx.Client', return_value=client) as constructor:
            self.assertEqual(asyncio.run(preload_model(request))['model'], 'qwen3.5:4b')
        self.assertEqual(constructor.call_args.kwargs['base_url'], Engine._host)
        self.assertEqual(client.post.call_args.args, ('/api/generate',))
        self.assertEqual(client.post.call_args.kwargs['json'], {
            'model': 'qwen3.5:4b', 'prompt': '', 'keep_alive': '5m', 'stream': False,
        })

    def test_task_clone_uses_selected_model_without_changing_shared_default(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {
            'OJ_MAIN_MODEL': 'qwen3.5:9b', 'OJ_TEMP_MODEL': 'qwen3.5:4b',
        }):
            agent = BusinessAgent(Engine(), 'qwen3.5:9b', graph_path=Path(folder)/'graph.db')
            def observe_runner(runner, text, context):
                return runner._model, runner._temp_model
            with patch.object(BusinessAgent, '_run_controlled', observe_runner):
                outcome = agent.run_task('Teste', model_override='another:8b')
            self.assertEqual(outcome, ('another:8b', 'qwen3.5:4b'))
            self.assertEqual(agent._model, 'qwen3.5:9b')
