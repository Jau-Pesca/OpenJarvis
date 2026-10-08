"""Cold-start validation; only --prepare-cold releases idle Jarvis Qwen models."""
import argparse
import json
from pathlib import Path
import httpx
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--prepare-cold', action='store_true')
args = parser.parse_args()
state = json.loads((Path.home()/'OpenJarvis-local/interface.json').read_text())
api_base = f"http://127.0.0.1:{state['api_port']}"
ui_base = f"http://127.0.0.1:{state['frontend_port']}"
with httpx.Client(timeout=180, trust_env=False) as client:
    def residents():
        response = client.get('http://127.0.0.1:11434/api/ps')
        response.raise_for_status()
        return {m['name'] for m in response.json()['models']}
    if args.prepare_cold:
        work = client.get(api_base+'/v1/business-tasks/status').json()
        call = client.get(api_base+'/v1/local-call/status').json()
        assert not call['active'] and not any(t['state'] in {'queued','running','redirecting'} for t in work['tasks']) and not any(m['state']=='pending' for m in work['messages']), 'Work is active; no models released'
        for model in residents() & {'qwen3.5:9b','qwen3.5:4b'}:
            response = client.post('http://127.0.0.1:11434/api/generate', json={'model':model,'prompt':'','keep_alive':0,'stream':False})
            response.raise_for_status()
        print(json.dumps({'cold_baseline': sorted(residents())}), flush=True)
    else:
        assert not residents(), 'Requires cold baseline; unrelated models are never released'
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel='chrome', headless=True)
            try:
                page = browser.new_page()
                page.add_init_script("localStorage.setItem('openjarvis-optin-seen','true'); localStorage.setItem('openjarvis-settings',JSON.stringify({defaultModel:'qwen3.5:4b',voiceOutputEnabled:false}));")
                page.goto(ui_base, wait_until='domcontentloaded')
                page.locator('textarea').first.wait_for()
                assert not residents(), 'Opening the UI loaded a model'
                for model in ('qwen3.5:9b','qwen3.5:4b'):
                    page.keyboard.press('Control+k')
                    dialog = page.get_by_role('dialog', name='Selecionar modelo')
                    dialog.wait_for()
                    with page.expect_response(lambda r: '/v1/models/select' in r.url) as selected:
                        dialog.get_by_role('button', name=model, exact=True).click()
                    assert selected.value.ok
                    dialog.wait_for(state='hidden')
                    assert not residents(), 'Selecting a model loaded it'
                print('PASS: abertura e seleção9b/4b mantiveram zero modelos residentes.', flush=True)
                field = page.locator('textarea').first
                field.fill('Olá. Cumprimente-me em uma frase.')
                with page.expect_response(lambda r: '/v1/chat/completions' in r.url, timeout=180000) as answer:
                    field.press('Enter')
                assert answer.value.ok
                assert b'[DONE]' in answer.value.body(), 'First message did not finish'
                assert residents() == {'qwen3.5:4b'}, residents()
                print('PASS: primeiro envio real carregou somente4b;9b e TEMP separado não aquecidos.', flush=True)
            finally:
                browser.close()
