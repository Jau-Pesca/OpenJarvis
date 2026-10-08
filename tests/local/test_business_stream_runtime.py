import asyncio
import threading
import unittest
import json
from unittest.mock import patch
from openjarvis.agents._stubs import AgentResult
from openjarvis.server.models import ChatCompletionRequest
from openjarvis.server.routes import _handle_agent_stream
from openjarvis.agents.task_runtime import TaskManager


class StreamTests(unittest.TestCase):
    def test_delegation_finishes_stream_and_allows_conversation_while_work_runs(self):
        entered, release = threading.Event(), threading.Event()
        class Agent:
            agent_id = 'business'
            _model = 'local'

            def chat(self, text, context=None, model=None):
                action = 'reply' if text == 'Converse comigo' else 'delegate'
                reply = 'Estou aqui.' if action == 'reply' else 'Vou investigar.'
                return AgentResult(content=reply, metadata={'decision': {'action': action, 'task': text, 'reply': reply}})

            def run(self, text, context=None, **kwargs):
                entered.set()
                release.wait(5)
                return AgentResult(content='Resultado posterior')
        manager = TaskManager(Agent())

        async def collect(text):
            request = ChatCompletionRequest(model='local', stream=True, session_id='chat-stream', messages=[{'role': 'user', 'content': text}])
            response = await _handle_agent_stream(manager.agent, 'local', request, task_manager=manager)
            chunks = [chunk async for chunk in response.body_iterator]
            self.assertEqual(chunks[-1], 'data: [DONE]\n\n')
            return ''.join(json.loads(c.removeprefix('data: '))['choices'][0]['delta'].get('content', '') or '' for c in chunks[:-1])

        async def scenario():
            with patch('openjarvis.server.routes._record_completed_exchange') as record:
                acknowledgement = await asyncio.wait_for(collect('Investigue produtos'), .8)
                self.assertEqual(acknowledgement, 'Vou investigar.')
                self.assertTrue(await asyncio.to_thread(entered.wait, 1))
                self.assertEqual(manager.snapshot('chat-stream')[0]['state'], 'running')
                record.assert_called_once()
                self.assertEqual(record.call_args.args[1:3], ('Investigue produtos', 'Vou investigar.'))
                answer = await asyncio.wait_for(collect('Converse comigo'), .8)
                self.assertEqual(answer, 'Estou aqui.')
                self.assertEqual(manager.snapshot('chat-stream')[0]['state'], 'running')
                self.assertEqual(record.call_count, 2)
        try:
            asyncio.run(scenario())
        finally:
            release.set()
            manager.close()
            manager.worker.join(2)

    def test_model_confirmation_precedes_work_and_disconnect_keeps_task(self):
        entered, release = threading.Event(), threading.Event()
        class Agent:
            agent_id = 'business'
            _model = 'local'

            def chat(self, text, context=None, model=None):
                return AgentResult(content='Vou investigar com um especialista.', metadata={'decision': {'action': 'delegate', 'task': text, 'reply': 'Vou investigar com um especialista.'}})

            def run(self, text, context=None, **kwargs):
                entered.set()
                release.wait(3)
                context.metadata['task_control'].check()
                return AgentResult(content='Resultado: ' + text)
        manager = TaskManager(Agent())
        async def scenario():
            request = ChatCompletionRequest(model='local', stream=True, session_id='chat-123', messages=[{'role': 'user', 'content': 'Investigue produtos'}])
            response = await _handle_agent_stream(manager.agent, 'local', request, task_manager=manager)
            iterator = response.body_iterator
            await anext(iterator)
            ack = await asyncio.wait_for(anext(iterator), 1)
            self.assertIn('Vou investigar com um especialista', ack)
            self.assertTrue(await asyncio.to_thread(entered.wait, 1))
            await iterator.aclose()
            task = manager.snapshot('chat-123')[0]
            self.assertEqual(task['state'], 'running')
            manager.submit('Somente nacionais', 'chat-123', mode='context', target=task['id'], expected_revision=1)
            release.set()
            for _ in range(100):
                if manager.snapshot('chat-123')[0]['state'] == 'done':
                    break
                await asyncio.sleep(.01)
            self.assertIn('nacionais', manager.snapshot('chat-123')[0]['result'])
        try:
            asyncio.run(scenario())
        finally:
            release.set()
            manager.close()
            manager.worker.join(2)


if __name__ == '__main__':
    unittest.main()
