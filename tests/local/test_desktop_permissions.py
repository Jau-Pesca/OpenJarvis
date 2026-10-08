import unittest
from unittest.mock import Mock, patch
from openjarvis.tools.mac_desktop import ComputerStepTool, DesktopSessions, chrome, DesktopPermissionError


class DesktopPermissionTests(unittest.TestCase):
    def test_window_movement_refreshes_observation_once_without_any_click(self):
        desktop = DesktopSessions()
        desktop.focused_window_supported = True
        view = {'title': 'Nova guia - Google Chrome', 'window_bounds': {'x':0,'y':34,'width':800,'height':600}}
        with patch('openjarvis.tools.mac_desktop.chrome', side_effect=['Nova guia','10, 34, 810, 634','Nova guia','0, 34, 800, 634']), patch('openjarvis.tools.mac_desktop.native', side_effect=[view,view]) as native:
            self.assertEqual(desktop.chrome_view({'pid':123,'window_id':7}), view)
        self.assertEqual([c.args[0] for c in native.call_args_list], ['observe','observe'])
        self.assertNotIn('expected_bounds', native.call_args.kwargs)

    def test_chrome_ax_title_suffix_is_checked_without_losing_action_guard(self):
        desktop = DesktopSessions()
        desktop.focused_window_supported = True
        view = {'title': 'Nova guia - Google Chrome: Perfil', 'window_bounds': {'x':0,'y':34,'width':800,'height':600}}
        with patch('openjarvis.tools.mac_desktop.chrome', side_effect=['Nova guia','0, 34, 800, 634']), patch('openjarvis.tools.mac_desktop.native', return_value=view) as native:
            self.assertEqual(desktop.chrome_view({'pid':123,'window_id':7}), view)
        self.assertNotIn('expected_bounds', native.call_args.kwargs)
        with patch('openjarvis.tools.mac_desktop.chrome', side_effect=['Outra janela','0, 34, 800, 634'] * 3), patch('openjarvis.tools.mac_desktop.native', return_value=view):
            with self.assertRaisesRegex(RuntimeError, 'não corresponde'):
                desktop.chrome_view({'pid':123,'window_id':7})

    def test_running_chrome_without_windows_reopens_once(self):
        desktop = DesktopSessions()
        state = {'available': True, 'accessibility': True, 'screen_recording': True,
                 'browser_running': True, 'apps': [{'pid':123, 'bundle':'com.google.Chrome'}]}
        with patch.object(desktop, 'status', return_value=state), patch('openjarvis.tools.mac_desktop.chrome', side_effect=[RuntimeError('Índice inválido (-1719)'), '77']), patch('openjarvis.tools.mac_desktop.native') as native, patch('openjarvis.tools.mac_desktop.time.sleep'):
            desktop._acquire('test', 'existing')
        native.assert_called_once_with('launch_chrome')
        self.assertEqual(desktop.leases['test']['window_id'], 77)

    def test_automation_denied_is_terminal_permission(self):
        with patch('openjarvis.tools.mac_desktop.subprocess.run', return_value=Mock(returncode=1, stderr='Not authorized (-1743)')):
            with self.assertRaises(DesktopPermissionError) as failure:
                chrome('fixed script')
        self.assertEqual(failure.exception.error_code, 'automation_permission_required')

    def test_action_carries_observed_window_identity(self):
        desktop = DesktopSessions()
        desktop.focused_window_supported = True
        lease = {'pid': 123, 'window_id': 7}
        view = {'title': 'Requested window', 'window_bounds': {'x': 10, 'y': 20, 'width': 100, 'height': 100}}
        with patch('openjarvis.tools.mac_desktop.native', side_effect=RuntimeError('A janela mudou')) as native:
            with self.assertRaisesRegex(RuntimeError, 'janela mudou'):
                desktop.chrome_action(lease, 'click', {'x': 30, 'y': 40}, view)
        self.assertEqual(native.call_args.kwargs['expected_title'], view['title'])
        self.assertEqual(native.call_args.kwargs['expected_bounds'], view['window_bounds'])

    def test_missing_accessibility_stops_before_chrome_and_model(self):
        desktop = DesktopSessions()
        engine = Mock()
        tool = ComputerStepTool(engine, 'local', desktop, 'test')
        with patch.object(desktop, 'status', return_value={'accessibility': False, 'screen_recording': True, 'browser_running': True}), patch('openjarvis.tools.mac_desktop.chrome') as chrome:
            result = tool.execute(instruction='Abra o site solicitado')
        self.assertFalse(result.success)
        self.assertEqual(result.metadata.get('error_code'), 'accessibility_permission_required')
        self.assertIs(result.metadata.get('retryable'), False)
        engine.generate.assert_not_called()
        chrome.assert_not_called()

    def test_missing_screen_permission_stops_before_chrome(self):
        desktop = DesktopSessions()
        with patch.object(desktop, 'status', return_value={'accessibility': True, 'screen_recording': False, 'browser_running': True}), patch('openjarvis.tools.mac_desktop.chrome') as chrome:
            result = ComputerStepTool(Mock(), 'local', desktop, 'test').execute(instruction='Veja a página')
        self.assertEqual(result.metadata.get('error_code'), 'screen_recording_permission_required')
        chrome.assert_not_called()

    def test_observation_does_not_hide_accessibility_error(self):
        desktop = DesktopSessions()
        with patch.object(desktop, 'ensure', return_value={'pid': 123, 'window_id': 1}), patch('openjarvis.tools.mac_desktop.chrome', return_value='https://example.org'), patch('openjarvis.tools.mac_desktop.native', side_effect=RuntimeError('AX error')) as native:
            with self.assertRaisesRegex(RuntimeError, 'AX error'):
                desktop.observe('test')
        self.assertEqual([c.args[0] for c in native.call_args_list], ['observe'])


if __name__ == '__main__':
    unittest.main()
