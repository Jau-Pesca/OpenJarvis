"""Exercise the model picker in an isolated browser, without account or mic access.

Requires the local UI launcher and an installed Chrome. Downloads are not started.
"""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from playwright.sync_api import sync_playwright


state = json.loads((Path.home()/'OpenJarvis-local/interface.json').read_text())
base = f"http://127.0.0.1:{state['frontend_port']}"
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel='chrome', headless=True)
    try:
        context = browser.new_context()
        # Reproduce a persisted localhost port that differs from the launcher.
        context.add_init_script("""if(!localStorage.getItem('openjarvis-settings')) localStorage.setItem('openjarvis-settings',
            JSON.stringify({apiUrl:'http://localhost:1',defaultModel:'qwen3.5:9b'}));
            localStorage.setItem('openjarvis-optin-seen','true');""")
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(base, wait_until='domcontentloaded')
        page.locator('textarea').first.wait_for()
        models_response = context.request.get(base+'/v1/models')
        assert models_response.ok, 'Model listing unavailable'
        models = models_response.json()['data']
        ids = [model['id'] for model in models]
        assert len(ids) >= 2, 'Expected the installed main and executor models'
        page.keyboard.press('Control+k')
        dialog = page.get_by_role('dialog', name='Selecionar modelo')
        dialog.wait_for()
        assert dialog.get_attribute('translate') == 'no'
        for model_id in ids:
            dialog.get_by_text(model_id, exact=True).wait_for()
        # Translation-style mutation, honoring the same no-translate boundary.
        modified = dialog.evaluate("""root => {
            const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
            const texts = [];
            while(walker.nextNode()) {
                const text = walker.currentNode;
                if(text.textContent.trim() && !text.parentElement.closest('[translate="no"],.notranslate')) texts.push(text);
            }
            for(const text of texts) {
                const wrapper=document.createElement('font'); wrapper.textContent=text.textContent;
                text.replaceWith(wrapper);
            }
            return texts.length;
        }""")
        assert modified == 0, 'Translator can reach picker text'
        for _ in range(3):
            dialog.get_by_role('button', name='Downloads', exact=True).click()
            dialog.get_by_placeholder('Ex.: codellama:7b').wait_for()
            dialog.get_by_role('button', name='Modelos de nuvem', exact=True).click()
            dialog.get_by_text('Configure as chaves dos provedores no servidor para usar modelos de nuvem.', exact=True).wait_for()
            dialog.get_by_role('button', name=f'Modelos instalados ({len(ids)})', exact=True).click()
        search = dialog.get_by_placeholder('Pesquisar modelos instalados…')
        search.fill('qwen3.5:4b')
        search.fill('')
        assert 'Não consegui consultar os modelos' not in dialog.inner_text()
        target = 'qwen3.5:4b' if 'qwen3.5:4b' in ids else ids[-1]
        with page.expect_response(lambda response: '/v1/models/select' in response.url, timeout=130000) as loading:
            dialog.get_by_role('button', name=target, exact=True).click()
        assert loading.value.ok, 'Backend model selection failed'
        dialog.wait_for(state='hidden', timeout=5000)
        assert page.evaluate("JSON.parse(localStorage.getItem('openjarvis-settings')).defaultModel") == target
        page.reload(wait_until='domcontentloaded')
        page.locator('textarea').first.wait_for()
        page.keyboard.press('Control+k')
        dialog.wait_for()
        dialog.get_by_role('button', name=target+' Ativo', exact=True).wait_for()
        page.keyboard.press('Escape')
        dialog.wait_for(state='hidden')
        # A chat must propagate the selection. Stub generation only, not listing/selection.
        sent = []
        def completion(route):
            sent.append(route.request.post_data_json.get('model'))
            route.fulfill(status=200, content_type='text/event-stream', body=
                'data: {"choices":[{"delta":{"content":"Olá."}}]}\n\n'
                'data: [DONE]\n\n')
        page.route('**/v1/chat/completions', completion)
        textarea = page.locator('textarea').first
        textarea.fill('Olá')
        textarea.press('Enter')
        page.get_by_text('Olá.', exact=True).first.wait_for(timeout=10000)
        assert sent == [target], f'Chat did not use the selected model: {sent}'
        call_status = context.request.get(base+'/v1/local-call/status')
        assert call_status.ok, 'Call status endpoint unavailable'
        assert call_status.json()['available'], 'Local call runtime unavailable'
        assert not errors, errors
        print(json.dumps({'installed_models': ids, 'selected_model': target,
            'tabs': 'PASS', 'translation_boundary': 'PASS simulated mutation',
            'selection_without_preload': 'PASS real', 'chat_selection': 'PASS stubbed generation',
            'stale_loopback_setting': 'PASS', 'call_status': 'PASS without microphone'}, ensure_ascii=False))
    finally:
        browser.close()

# Verify the agent actually generates with the selected model, using a temporary
# graph instead of the account's personal memory. No browser work is delegated.
from openjarvis.agents.business import BusinessAgent
from openjarvis.engine.ollama import OllamaEngine


class TrackingEngine(OllamaEngine):
    def __init__(self):
        super().__init__(host='http://127.0.0.1:11434', timeout=180)
        self.used_models = []

    def generate(self, messages, *, model, **kwargs):
        self.used_models.append(model)
        return super().generate(messages, model=model, **kwargs)


with tempfile.TemporaryDirectory(prefix='jarvis-model-choice-') as folder, patch.dict(os.environ, {
    'OJ_MAIN_MODEL': 'qwen3.5:9b', 'OJ_TEMP_MODEL': 'qwen3.5:4b',
}):
    engine = TrackingEngine()
    agent = BusinessAgent(engine, 'qwen3.5:9b', graph_path=Path(folder)/'graph.db')
    answer = agent.chat('Olá. Apenas me cumprimente brevemente.', model=target)
    assert engine.used_models and all(model == target for model in engine.used_models)
    assert answer.metadata['decision']['action'] == 'reply', 'Greeting unexpectedly delegated work'
    print(json.dumps({'principal_inference': 'PASS real', 'models_used': engine.used_models,
        'temporary_model': agent._temp_model, 'memory': 'temporary'}, ensure_ascii=False))
