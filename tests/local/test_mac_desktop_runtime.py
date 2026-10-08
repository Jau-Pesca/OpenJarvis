import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from openjarvis.tools.mac_desktop import ComputerStepTool, DesktopSessions
from openjarvis.tools.spreadsheet_local import SpreadsheetCreateTool
from openjarvis.agents.task_runtime import TaskManager
from openjarvis.agents._stubs import AgentResult


class MainAgent:
    """Deterministic conversation decisions with a cancellable task worker."""

    _model = 'local'
    agent_id = 'business'

    def __init__(self):
        self.decision = {'action': 'reply', 'reply': 'Resposta escolhida pela IA'}
        self.release = threading.Event()

    def chat(self, text, context=None, model=None):
        return AgentResult(content=self.decision['reply'], metadata={'decision': dict(self.decision)})

    def run(self, text, context=None, **kwargs):
        self.release.wait(3)
        context.metadata['task_control'].check()
        return AgentResult(content='Resultado ' + text)


class Engine:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.calls = []
    def generate(self, messages, **options):
        self.calls.append((messages, options))
        return {'content': json.dumps(next(self.replies))}


class Desktop:
    def __init__(self):
        self.actions = []
    def observe(self, session):
        return {'url': 'https://example.com', 'nodes': [{'role': 'AXButton', 'text': 'Produtos', 'x': 123, 'y': 234}]}
    def act(self, session, action, params):
        self.actions.append((session, action, params))
        return {'ok': True}


class TempTests(unittest.TestCase):
    def test_each_executor_receives_fresh_context_and_one_action(self):
        engine = Engine([{'action': 'navigate', 'url': 'https://example.org'}, {'action': 'click', 'x': 123, 'y': 234}])
        desktop = Desktop()
        tool = ComputerStepTool(engine, 'local', desktop, 'voice')
        self.assertTrue(tool.execute(instruction='Navegue para https://example.org').success)
        self.assertTrue(tool.execute(instruction='Clique no botão Produtos').success)
        self.assertEqual(len(engine.calls[1][0]), 2)
        self.assertNotIn('Navegue', engine.calls[1][0][1].content)
        self.assertEqual(engine.calls[1][1]['num_ctx'], 4096)
        self.assertEqual([a[1] for a in desktop.actions], ['navigate', 'click'])

    def test_invalid_compound_action_cannot_execute(self):
        desktop = Desktop()
        tool = ComputerStepTool(Engine([{'action': 'navigate', 'url': 'https://example.org', 'text': 'send'}]), 'local', desktop, 'voice')
        self.assertFalse(tool.execute(instruction='Abra a página').success)
        self.assertEqual(desktop.actions, [])

    def test_existing_browser_is_acquired_for_explicit_delegated_work(self):
        sessions = DesktopSessions()
        def acquire(session, mode):
            sessions.leases[session] = {'pid': 123, 'window_id': 77, 'mode': mode}
        with patch.object(sessions, 'status', return_value={'accessibility': True, 'screen_recording': True, 'browser_running': True}), patch.object(sessions, '_acquire', side_effect=acquire) as call, patch('openjarvis.tools.mac_desktop.chrome'):
            self.assertEqual(sessions.ensure('voice')['window_id'], 77)
            call.assert_called_once_with('voice', 'existing')

    def test_navigation_uses_new_tab_and_real_keyboard(self):
        sessions = DesktopSessions()
        with patch.object(sessions, 'ensure', return_value={'pid': 123, 'window_id': 77}), patch('openjarvis.tools.mac_desktop.native', return_value={'ok': True, 'nodes': [{'role': 'AXButton', 'text': 'Nova guia', 'x': 300, 'y': 50}, {'role': 'AXTextField', 'text': 'Barra de endereço', 'x': 400, 'y': 80}]}) as events, patch('openjarvis.tools.mac_desktop.chrome', return_value='https://www.mercadolivre.com.br/'), patch('openjarvis.security.ssrf.check_ssrf', return_value=None):
            result = sessions.act('voice', 'navigate', {'url': 'https://www.mercadolivre.com.br/'})
            self.assertEqual(result['input'], 'real_mouse_keyboard')
            self.assertEqual([c.args[0] for c in events.call_args_list], ['observe', 'click', 'observe', 'click', 'key', 'type', 'key'])
            self.assertEqual(events.call_args_list[1].kwargs['x'], 300)
            self.assertEqual(events.call_args_list[3].kwargs['x'], 400)
            self.assertEqual(events.call_args_list[4].kwargs['key'], 'cmd+a')
            self.assertEqual(events.call_args_list[5].kwargs['text'], 'https://www.mercadolivre.com.br/ ')
            self.assertEqual(events.call_args_list[6].kwargs['key'], 'enter')

    def test_missing_address_bar_stops_without_guessing_coordinates(self):
        sessions = DesktopSessions()
        with patch.object(sessions, 'ensure', return_value={'pid': 123, 'window_id': 77}), patch('openjarvis.tools.mac_desktop.native', return_value={'nodes': []}) as events, patch('openjarvis.security.ssrf.check_ssrf', return_value=None):
            with self.assertRaisesRegex(RuntimeError, 'barra de endereço'):
                sessions.act('voice', 'navigate', {'url': 'https://www.mercadolivre.com.br/'})
            self.assertNotIn('click', [c.args[0] for c in events.call_args_list])

    def test_screen_image_is_sent_to_local_model_without_base64_in_text(self):
        desktop = Desktop()
        view = {'image': 'encoded-screen', 'window_bounds': {'x': 0, 'y': 0, 'width': 800, 'height': 600}, 'nodes': []}
        desktop.observe = lambda session: view
        engine = Engine([{'action': 'click', 'x': 100, 'y': 200}])
        tool = ComputerStepTool(engine, 'local', desktop, 'voice')
        self.assertTrue(tool.execute(instruction='Clique no elemento visível na tela').success)
        user = engine.calls[0][0][1]
        self.assertEqual(user.images, ['encoded-screen'])
        self.assertNotIn('encoded-screen', user.content)
        self.assertNotIn('image', ComputerStepTool.compact(view))
        self.assertFalse(ComputerStepTool.in_window(900, 100, view['window_bounds']))

    def test_closed_window_never_retargets_another_window(self):
        sessions = DesktopSessions()
        sessions.leases['voice'] = {'pid': 123, 'window_id': 77, 'mode': 'existing'}
        with patch('openjarvis.tools.mac_desktop.chrome', side_effect=RuntimeError('window not found')):
            with self.assertRaises(RuntimeError):
                sessions.ensure('voice')


class PermissionTests(unittest.TestCase):
    def test_question_creates_no_job_and_approval_resumes_saved_objective(self):
        agent = MainAgent()
        manager = TaskManager(agent)
        desktop = DesktopSessions()
        manager.desktop = desktop
        def send(text):
            result = manager.message(text, 'voice')
            for _ in range(100):
                d = next(x for x in manager.dialogue_snapshot() if x['id'] == result['message_id'])
                if d['state'] != 'pending':
                    return d
                time.sleep(.01)
            self.fail('No decision')
        try:
            with patch.object(desktop, 'status', return_value={'available': True, 'browser_running': True}), patch.object(desktop, '_acquire'):
                agent.decision = {'action': 'request_browser', 'reply': 'Posso usar a janela aberta?', 'target': 'existing', 'task': 'Abra o Mercado Livre'}
                self.assertEqual(send('Abra o Mercado Livre')['state'], 'done')
                self.assertEqual(manager.snapshot(), [])
                agent.decision = {'action': 'approve_browser', 'reply': 'Vou abrir na janela autorizada.'}
                self.assertEqual(send('Pode usar')['state'], 'done')
                self.assertEqual(manager.snapshot()[0]['query'], 'Abra o Mercado Livre')
                self.assertEqual(desktop.requests, {})
        finally:
            manager.close()
            agent.release.set()
            manager.worker.join(2)


class SpreadsheetTests(unittest.TestCase):
    def test_real_xlsx_has_headers_ten_rows_and_numeric_costs(self):
        with tempfile.TemporaryDirectory() as folder, patch('openjarvis.tools.spreadsheet_local.Path.home', return_value=Path(folder)):
            tool = SpreadsheetCreateTool()
            result = tool.execute(name='produtos.xlsx', columns=['SKU', 'PRODUTO', 'CUSTO'], rows=[[f'SKU{i:03}', f'Produto {i}', float(i + 10)] for i in range(10)], open=False)
            self.assertTrue(result.success, result.content)
            with ZipFile(result.metadata['path']) as archive:
                for name in archive.namelist():
                    ET.fromstring(archive.read(name))
                sheet = ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
            ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            self.assertEqual(len(sheet.findall('s:sheetData/s:row', ns)), 11)
            self.assertEqual([t.text for t in sheet.findall('s:sheetData/s:row[1]/s:c/s:is/s:t', ns)], ['SKU', 'PRODUTO', 'CUSTO'])
            self.assertEqual(sheet.find('s:sheetData/s:row[2]/s:c[@r="C2"]/s:v', ns).text, '10.0')
            original = Path(result.metadata['path']).read_bytes()
            self.assertFalse(tool.execute(name='produtos.xlsx', columns=['A'], rows=[[1]], open=False).success)
            self.assertEqual(Path(result.metadata['path']).read_bytes(), original)

    def test_path_escape_is_rejected(self):
        result = SpreadsheetCreateTool().execute(name='../outside.xlsx', columns=['A'], rows=[], open=False)
        self.assertFalse(result.success)


if __name__ == '__main__':
    unittest.main()
