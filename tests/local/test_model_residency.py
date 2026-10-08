import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from openjarvis.server.model_residency import select_business_model, preload_and_select


class ResidencyTests(unittest.TestCase):
    def state(self, tasks=(), messages=(), active=False):
        manager = SimpleNamespace(lock=threading.RLock(), model='qwen3.5:9b',
            snapshot=lambda: list(tasks), dialogue_snapshot=lambda: list(messages))
        call = SimpleNamespace(lock=threading.RLock(), snapshot=lambda: {'active': active})
        return SimpleNamespace(model='qwen3.5:9b', business_tasks=manager, local_call=call,
            agent=SimpleNamespace(agent_id='business', _model='qwen3.5:9b', _temp_model='qwen3.5:4b'))

    def test_idle_selection_retains_previous_and_updates_future_default(self):
        state = self.state()
        client = Mock()
        client.get.return_value.json.return_value = {'models': [{'name': 'qwen3.5:9b'}]}
        client.__enter__ = Mock(return_value=client)
        client.__exit__ = Mock(return_value=False)
        with patch('openjarvis.server.model_residency.httpx.Client', return_value=client):
            result = select_business_model(state, SimpleNamespace(_host='http://local'), 'qwen3.5:4b')
        self.assertEqual(result['unloaded'], [])
        client.post.assert_not_called()
        self.assertEqual(state.business_tasks.model, 'qwen3.5:4b')
        self.assertEqual(state.agent._temp_model, 'qwen3.5:4b')

    def test_each_active_state_retains_old_model_without_unload(self):
        cases = [self.state(tasks=[{'state': s}]) for s in ('queued', 'running', 'redirecting')]
        cases += [self.state(messages=[{'state': 'pending'}]), self.state(active=True)]
        for state in cases:
            with self.subTest(state=state), patch('openjarvis.server.model_residency.httpx.Client') as client:
                result = select_business_model(state, SimpleNamespace(_host='http://local'), 'qwen3.5:4b')
                self.assertEqual(result['retained'], ['qwen3.5:9b'])
                client.assert_not_called()

    def test_temp_model_is_never_unloaded(self):
        state = self.state()
        state.agent._temp_model = 'qwen3.5:9b'
        with patch('openjarvis.server.model_residency.httpx.Client') as client:
            self.assertEqual(select_business_model(state, SimpleNamespace(_host='http://local'), 'qwen3.5:4b')['unloaded'], [])
            client.assert_not_called()

    def test_later_selection_never_forces_old_model_out_of_cache(self):
        state = self.state(active=True)
        select_business_model(state, SimpleNamespace(_host='http://local'), 'qwen3.5:4b')
        state.local_call.snapshot = lambda: {'active': False}
        client = Mock()
        client.get.return_value.json.return_value = {'models': [{'name': 'qwen3.5:9b'}]}
        client.__enter__ = Mock(return_value=client)
        client.__exit__ = Mock(return_value=False)
        with patch('openjarvis.server.model_residency.httpx.Client', return_value=client):
            result = select_business_model(state, SimpleNamespace(_host='http://local'), 'qwen3.5:4b')
        self.assertEqual(result['unloaded'], [])
        client.post.assert_not_called()

    def test_nonstream_inference_finishes_before_unload_and_default_is_not_restored(self):
        from openjarvis.agents._stubs import AgentResult
        from openjarvis.server.models import ChatCompletionRequest
        from openjarvis.server.routes import _get_agent_model_lock, _handle_agent
        entered, release, http_started = threading.Event(), threading.Event(), threading.Event()
        state = self.state()
        def generate(*args, **kwargs):
            entered.set()
            if not release.wait(3):
                raise TimeoutError('test generation was not released')
            return AgentResult(content='Olá')
        state.agent.run = generate
        request = ChatCompletionRequest(model='qwen3.5:9b', messages=[{'role': 'user', 'content': 'Olá'}])
        inference = threading.Thread(target=_handle_agent, args=(state.agent, 'qwen3.5:9b', request))
        client = Mock()
        client.get.return_value.json.return_value = {'models': [{'name': 'qwen3.5:9b'}]}
        client.__enter__ = Mock(return_value=client)
        client.__exit__ = Mock(return_value=False)
        client.post.side_effect = lambda *a, **kw: (http_started.set() or Mock())
        switch = threading.Thread(target=preload_and_select, args=(state, SimpleNamespace(_host='http://local'), 'qwen3.5:4b', _get_agent_model_lock(state.agent)))
        with patch('openjarvis.server.model_residency.httpx.Client', return_value=client):
            inference.start()
            try:
                self.assertTrue(entered.wait(1))
                switch.start()
                self.assertFalse(http_started.wait(.1), 'Model switch ran during inference')
            finally:
                release.set()
                inference.join(2)
                if switch.ident is not None:
                    switch.join(2)
        self.assertFalse(switch.is_alive())
        self.assertEqual(state.agent._model, 'qwen3.5:4b')
