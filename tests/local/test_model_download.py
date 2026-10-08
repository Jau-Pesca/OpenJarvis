import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import httpx
from fastapi import HTTPException
from openjarvis.server.routes import pull_model


class DownloadTests(unittest.TestCase):
    def run_pull(self, result, installed=(), name='gpt-oss:20b', inventory=None):
        engine = SimpleNamespace(engine_id='ollama', _host='http://localhost:11434')
        request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(engine=engine)), json=AsyncMock(return_value={'model': name}))
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.post.return_value = httpx.Response(200, json=result, request=httpx.Request('POST', 'http://local/api/pull'))
        client.get.return_value = httpx.Response(200, json=inventory if inventory is not None else {'models': [{'name': name} for name in installed]}, request=httpx.Request('GET', 'http://local/api/tags'))
        with patch('httpx.AsyncClient', return_value=client):
            return asyncio.run(pull_model(request))

    def test_error_inside_http_200_is_not_success(self):
        with self.assertRaises(HTTPException) as error:
            self.run_pull({'error': 'model manifest not found'})
        self.assertEqual(error.exception.status_code, 502)
        self.assertEqual(error.exception.detail, 'model manifest not found')

    def test_missing_completion_is_not_success(self):
        with self.assertRaises(HTTPException):
            self.run_pull({'status': 'downloading'})

    def test_finished_but_missing_install_is_not_success(self):
        with self.assertRaises(HTTPException):
            self.run_pull({'status': 'success'})

    def test_success_requires_installed_model_and_supports_default_tag(self):
        self.assertEqual(self.run_pull({'status': 'success'}, ['gpt-oss:20b'])['status'], 'ok')
        self.assertEqual(self.run_pull({'status': 'success'}, ['gemma3:latest'], name='gemma3')['status'], 'ok')

    def test_malformed_inventory_is_a_readable_backend_error(self):
        for inventory in ([], {'models': 'invalid'}):
            with self.subTest(inventory=inventory), self.assertRaises(HTTPException) as error:
                self.run_pull({'status': 'success'}, inventory=inventory)
            self.assertEqual(error.exception.status_code, 502)
