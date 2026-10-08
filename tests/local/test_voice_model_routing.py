import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from openjarvis.server.local_call import LocalCall, create_local_call_router
from openjarvis.server.business_tasks import create_business_task_router


class VoiceRoutingTests(unittest.TestCase):
    def test_start_passes_selection_only_to_child_environment(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder)/'iniciar-chamada-interface.sh').write_text('# test fixture')
            manager = LocalCall(Path(folder))
            process = Mock()
            process.poll.return_value = None
            with patch('openjarvis.server.local_call.subprocess.Popen', return_value=process) as spawn, patch('openjarvis.server.local_call.threading.Thread'):
                manager.start('test-session', [], 'qwen3.5:4b', True)
            self.assertEqual(spawn.call_args.kwargs['env']['OJ_CALL_MODEL'], 'qwen3.5:4b')
            self.assertEqual(spawn.call_args.kwargs['env']['OJ_VOICE_BARGE_IN'], '1')
            self.assertNotEqual(os.environ.get('OJ_CALL_MODEL'), 'qwen3.5:4b')

    def test_voice_http_routes_preserve_selected_model(self):
        app = FastAPI()
        call, tasks = Mock(), Mock()
        call.start.return_value = {'active': True}
        tasks.message.return_value = {'action': 'chat_pending'}
        app.include_router(create_local_call_router(call))
        app.include_router(create_business_task_router(tasks))
        client = TestClient(app)
        self.assertEqual(client.post('/v1/local-call/start', json={'model': 'qwen3.5:4b', 'session': 'test-session'}).status_code, 200)
        call.start.assert_called_once_with('test-session', [], 'qwen3.5:4b', False)
        self.assertEqual(client.post('/v1/business-tasks/submit', json={'model': 'qwen3.5:4b', 'session': 'test-session', 'text': 'Olá'}).status_code, 200)
        self.assertEqual(tasks.message.call_args.kwargs['model'], 'qwen3.5:4b')
