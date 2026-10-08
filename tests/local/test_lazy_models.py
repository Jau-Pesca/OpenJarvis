import asyncio
import importlib.util
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, AsyncMock, patch
from openjarvis.server.model_residency import select_without_loading
from openjarvis.server.routes import select_model
from openjarvis.server.cloud_router import is_cloud_model


class LazyTests(unittest.TestCase):
    def test_startup_only_queries_health_and_inventory_even_if_models_missing(self):
        path = Path(__file__).resolve().parents[2]/'scripts/local/preparar_modelos.py'
        spec = importlib.util.spec_from_file_location('lazy_startup', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        engine = Mock()
        engine.health.return_value = True
        engine.list_models.return_value = []
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder)/'config.toml').write_text('[intelligence]\ndefault_model="qwen3.5:9b"\n')
            module.prepare(Path(folder), engine)
        self.assertEqual([call[0] for call in engine.method_calls], ['health', 'list_models'])

    def test_selecting_from_cold_state_never_sends_generate(self):
        manager = SimpleNamespace(lock=threading.RLock(), model='qwen3.5:9b', snapshot=lambda: [], dialogue_snapshot=lambda: [])
        state = SimpleNamespace(business_tasks=manager, model='qwen3.5:9b', agent=SimpleNamespace(agent_id='business', _model='qwen3.5:9b', _temp_model='qwen3.5:4b'))
        client = Mock()
        client.__enter__ = Mock(return_value=client)
        client.__exit__ = Mock(return_value=False)
        client.get.return_value.json.return_value = {'models': []}
        with patch('openjarvis.server.model_residency.httpx.Client', return_value=client):
            result = select_without_loading(state, SimpleNamespace(_host='http://local'), 'qwen3.5:4b', threading.Lock())
        client.post.assert_not_called()
        self.assertEqual(result['unloaded'], [])
        self.assertEqual(manager.model, 'qwen3.5:4b')

    def test_select_endpoint_checks_installation_without_loading(self):
        engine = Mock()
        engine.engine_id = 'ollama'
        engine._host = 'http://local'
        engine.list_models.return_value = ['gpt-oss:20b']
        request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(engine=engine)), json=AsyncMock(return_value={'model': 'gpt-oss:20b'}))
        self.assertEqual(asyncio.run(select_model(request))['model'], 'gpt-oss:20b')
        engine.generate.assert_not_called()
        self.assertFalse(is_cloud_model('gpt-oss:20b'))
