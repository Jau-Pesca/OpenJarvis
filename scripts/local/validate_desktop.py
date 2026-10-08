"""Physical desktop checks; reports evidence without images/personal AX text."""
import argparse
import json
import base64
from pathlib import Path
from openjarvis.tools.mac_desktop import DesktopSessions, native

parser = argparse.ArgumentParser()
parser.add_argument('--navigate', action='store_true', help='Move the real cursor and open Mercado Livre in a new Chrome tab')
parser.add_argument('--next-step', action='store_true', help='Use the real temporary model to click the search box on the opened home page')
parser.add_argument('--screenshot', action='store_true', help='Save a temporary screen image for inspection')
args = parser.parse_args()
state = native('status')
print(json.dumps({key: state.get(key) for key in ('accessibility','screen_recording','posting_events','bundle_id','request_file_supported','focused_window_supported')},ensure_ascii=False), flush=True)
if args.navigate or args.next_step or args.screenshot:
    desktop = DesktopSessions()
    try:
        outcome = desktop.act('physical-validation', 'navigate', {'url':'https://www.mercadolivre.com.br/'}) if args.navigate else None
        after = desktop.observe('physical-validation')
        print(json.dumps({'execution':outcome,'after': {'url':after.get('url'),'window_bounds':after.get('window_bounds'),'frontmost_pid':after.get('frontmost_pid'),'pid':after.get('pid')}},ensure_ascii=False),flush=True)
        if args.navigate:
            assert outcome['ok'] and after['url'] == 'https://www.mercadolivre.com.br/'
            print('PASS: página inicial correta, sem caminho preenchido pelo autocomplete.',flush=True)
        if args.screenshot:
            Path('/private/tmp/jarvis-current-screen.jpg').write_bytes(base64.b64decode(after['image']))
            print('SCREEN_TEMP /private/tmp/jarvis-current-screen.jpg',flush=True)
        if args.next_step:
            from openjarvis.tools.mac_desktop import ComputerStepTool
            from openjarvis.engine.ollama import OllamaEngine
            tool = ComputerStepTool(OllamaEngine(host='http://127.0.0.1:11434',timeout=180), 'qwen3.5:4b', desktop, 'physical-validation')
            result = tool.execute(instruction='Clique uma única vez na caixa de busca de produtos do Mercado Livre. Não digite nem envie pesquisa. Não clique na barra de endereço do Chrome.')
            print('TEMP_RESULT',json.dumps({'success':result.success,'metadata':result.metadata,'error':result.content if not result.success else None},ensure_ascii=False),flush=True)
            assert result.success and result.metadata.get('action') == 'click', 'Modelo não confirmou clique físico solicitado'
    finally:
        desktop.release('physical-validation')
