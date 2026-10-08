"""Validate custom-download feedback in Chrome with fully simulated transfers."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

state = json.loads((Path.home()/'OpenJarvis-local/interface.json').read_text())
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel='chrome', headless=True)
    try:
        page = browser.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.add_init_script("""
            localStorage.setItem('openjarvis-optin-seen','true');
            localStorage.setItem('openjarvis-settings',JSON.stringify({defaultModel:'qwen3.5:4b'}));
            const fetchOriginal = window.fetch.bind(window);
            window.pullRequests = 0;
            window.fetch = (url, options) => {
                if (String(url).endsWith('/v1/models/pull')) {
                    window.pullRequests++;
                    return new Promise(resolve => window.finishPull = error => resolve(new Response(
                        JSON.stringify(error ? {detail:error} : {status:'ok'}),
                        {status:error ? 502:200,headers:{'Content-Type':'application/json'}})));
                }
                if (String(url).endsWith('/v1/models/select')) {
                    const model = JSON.parse(options.body).model;
                    if(model === 'test-download:no-weights') return new Promise(resolve => window.finishLoad = () => resolve(new Response('{}',{status:200})));
                    return Promise.resolve(new Response('{}',{status:200}));
                }
                return fetchOriginal(url,options);
            };
        """)
        page.goto(f"http://127.0.0.1:{state['frontend_port']}", wait_until='domcontentloaded')
        page.locator('textarea').first.wait_for()
        page.keyboard.press('Control+k')
        dialog = page.get_by_role('dialog', name='Selecionar modelo')
        dialog.wait_for()
        dialog.get_by_role('button', name='Downloads', exact=True).click()
        field = dialog.get_by_placeholder('Ex.: codellama:7b')
        field.fill('test-download:no-weights')
        custom = field.locator('..').locator('button')
        custom.click()
        dialog.get_by_text('Baixando test-download:no-weights… Isso pode levar alguns minutos. Aguardando a confirmação do Ollama.', exact=True).wait_for()
        assert custom.inner_text() == 'Baixando…'
        assert field.is_disabled()
        assert page.evaluate('window.pullRequests') == 1
        page.evaluate("window.finishPull('Modelo de teste não encontrado')")
        field.wait_for(state='visible')
        dialog.get_by_role('alert').get_by_text('Modelo de teste não encontrado', exact=True).last.wait_for()
        assert field.input_value() == 'test-download:no-weights'
        assert not field.is_disabled()
        custom.click()
        page.evaluate('window.finishPull(null)')
        dialog.get_by_text('Download de test-download:no-weights concluído. Selecionando modelo; ele será carregado no primeiro envio.', exact=True).wait_for()
        assert custom.inner_text() == 'Selecionando…'
        page.evaluate('window.finishLoad()')
        dialog.wait_for(state='hidden')
        assert page.evaluate("JSON.parse(localStorage.getItem('openjarvis-settings')).defaultModel") == 'test-download:no-weights'
        assert not errors, errors
        print('PASS: feedback de download/seleção sem aquecimento, nome preservado após erro, nova tentativa e sucesso; nenhuma transferência real.')
    finally:
        browser.close()
