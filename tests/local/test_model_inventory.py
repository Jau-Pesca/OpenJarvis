"""Regression for Ollama compatibility children leaking into the picker."""
import unittest
import httpx
from openjarvis.engine.ollama import OllamaEngine


class InventoryTests(unittest.TestCase):
    def listing(self, models):
        engine = OllamaEngine(host='http://local')
        engine._client.close()
        engine._client = httpx.Client(base_url='http://local', transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={'models': models})))
        try:
            return engine.list_models()
        finally:
            engine._client.close()

    def test_migrated_duplicate_and_linked_internal_alias_are_hidden(self):
        digest = 'a' * 64
        self.assertEqual(self.listing([
            {'name': 'gpt-oss:20b', 'digest': 'old'},
            {'name': 'gpt-oss:20b', 'digest': digest},
            {'name': 'llamacpp:'+digest, 'digest': digest},
            {'name': 'qwen3.5:4b', 'digest': 'qwen'},
        ]), ['gpt-oss:20b', 'qwen3.5:4b'])

    def test_standalone_or_mismatched_alias_is_preserved(self):
        digest = 'b' * 64
        self.assertEqual(self.listing([
            {'name': 'llamacpp:'+digest, 'digest': digest},
            {'name': 'custom:latest', 'digest': 'other'},
        ]), ['llamacpp:'+digest, 'custom:latest'])

    def test_regular_duplicate_names_without_digest_are_deduplicated(self):
        self.assertEqual(self.listing([{'name':'test'}, {'name':'test'}]), ['test'])
