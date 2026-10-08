"""Render task diagnostics and audio choices in an isolated Chrome context."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
state=json.loads((Path.home()/'OpenJarvis-local/interface.json').read_text())
base=f"http://127.0.0.1:{state['frontend_port']}"
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    try:
        page=browser.new_page()
        page.add_init_script("localStorage.setItem('openjarvis-optin-seen','true');localStorage.setItem('openjarvis-settings',JSON.stringify({defaultModel:'qwen3.5:4b',voiceOutputEnabled:false}));")
        page.route('**/v1/models/select',lambda r:r.fulfill(json={'status':'ok','model':'qwen3.5:4b'}))
        page.route('**/v1/local-call/status*',lambda r:r.fulfill(json={'active':False,'available':True,'status':'idle','transcript':[],'voice':'','model':'','error':None,'call_id':None}))
        page.route('**/v1/business-tasks/status*',lambda r:r.fulfill(json={'messages':[],'tasks':[{'id':'test','session':'test','query':'Abra o site','state':'error','stage':'Não foi possível concluir','result':'','error':'Falha de teste','model':'qwen3.5:4b','elapsed_seconds':12,'failure_stage':'Localizando janela e observando tela','events':[{'sequence':1,'revision':1,'timestamp':1,'kind':'tool','stage':'Ferramenta terminou','tool':'computer_step','status':'error','duration_ms':2400}]}]}))
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(base,wait_until='domcontentloaded')
        page.get_by_text('Falhou durante:',exact=False).wait_for()
        assert page.get_by_text('Etapas e tempos de execução',exact=True).is_visible()
        assert page.get_by_text('Localizando janela e observando tela',exact=True).is_visible()
        checkbox=page.get_by_role('checkbox',name='Estou usando fones: permitir interrupção por voz')
        assert checkbox.is_visible() and not checkbox.is_checked()
        checkbox.check()
        assert checkbox.is_checked()
        assert not errors,errors
        print('PASS: Chrome mostra fase da falha, timeline, duração e opção de fones; sem microfone/playback.')
    finally:browser.close()
