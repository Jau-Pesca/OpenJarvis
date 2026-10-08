"""Regression checks for the reviewable local voice runtime (no audio device)."""
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import importlib.util
from pathlib import Path
import sys
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch


def load_runtime():
    path = Path(__file__).resolve().parents[2] / "scripts/local/chamada_continua.py"
    spec = importlib.util.spec_from_file_location("reviewable_continuous_call", path)
    module = importlib.util.module_from_spec(spec)
    # Device-independent checks don't use these capture implementations.
    audio = SimpleNamespace(EchoReference=Mock, VoiceActivity=Mock, wav_bytes=Mock())
    with patch.dict(sys.modules, {"audio_continuo": audio}):
        spec.loader.exec_module(module)
    return module


runtime = load_runtime()


class SelectedVoiceModelTests(unittest.TestCase):
    def test_selected_model_is_sent_to_remote_task_server(self):
        config = SimpleNamespace(intelligence=SimpleNamespace(default_model='qwen3.5:9b'))
        with patch.dict(runtime.os.environ, {'OJ_CALL_MODEL': 'qwen3.5:4b'}):
            client = runtime.TaskClient(config, 'http://127.0.0.1:8000')
        try:
            with patch.object(client, '_request', return_value={}) as request:
                client.submit('Olá', [])
                self.assertEqual(request.call_args.kwargs['json']['model'], 'qwen3.5:4b')
        finally:
            client.http.close()


def bare_player():
    player = runtime.SpeechOutput.__new__(runtime.SpeechOutput)
    player.lock = threading.Condition(threading.RLock())
    player.messages = deque()
    player.closed = False
    player.version = 0
    player.busy = player.rendering = player.restart_neural = False
    player.stream = player.say = None
    player.report = Mock()
    player.clean = lambda text: text
    player.ready = lambda: True
    player.cache = {}
    player.synthesis = ThreadPoolExecutor(max_workers=1)
    player._play = Mock()
    return player


def test_interruption_restarts_busy_serial_synthesis_for_uncached_response():
    player = bare_player()
    entered, killed = threading.Event(), threading.Event()
    old = Mock()

    def render_old(text):
        entered.set()
        assert killed.wait(2), "Stale synthesis was not stopped"
        raise RuntimeError("Worker terminated")

    old.render.side_effect = render_old
    old.process.kill.side_effect = killed.set
    replacement = Mock()
    replacement.render.return_value = (b"fresh", 16000)
    player.neural = old
    player.neural_factory = Mock(return_value=replacement)
    worker = threading.Thread(target=player._work, daemon=True)
    worker.start()
    try:
        player.speak("Resposta antiga")
        assert entered.wait(1)
        assert not any(call.args[0] == "speaking" for call in player.report.call_args_list)
        player.interrupt()
        player.speak("Nova confirmação sem cache")
        assert player.wait_idle(2)
        old.process.kill.assert_called_once()
        old.close.assert_called_once()
        replacement.render.assert_called_once_with("Nova confirmação sem cache")
        player._play.assert_called_once_with(b"fresh", 16000, 1)
        assert not any(call.args[0] == "error" for call in player.report.call_args_list)
    finally:
        with player.lock:
            player.closed = True
            player.lock.notify_all()
        worker.join(2)
        player.synthesis.shutdown(wait=True)


def test_failure_voice_is_short_and_does_not_disclose_technical_error():
    task = {"state": "error", "error": "computer_step stack trace " * 100}
    answer = runtime.spoken_result(task)
    assert len(answer) < 100
    assert "stack trace" not in answer
    assert "interface" in answer
    task["voice_message"] = "Preciso da permissão de Acessibilidade. Veja a interface."
    assert runtime.spoken_result(task) == task["voice_message"]
    assert task["error"].startswith("computer_step")


def test_end_phrase_is_submitted_to_ai_instead_of_local_routing():
    client = Mock(messages=[])
    client.submit.return_value = {"action": "chat_pending", "acknowledgement": ""}
    client.snapshot.return_value = []
    player = Mock(voice="teste")
    config = SimpleNamespace(intelligence=SimpleNamespace(default_model="test"))
    with patch.object(runtime, "TaskClient", return_value=client), patch.object(runtime, "SpeechOutput", return_value=player), patch("builtins.input", side_effect=["encerrar chamada", EOFError]):
        runtime.run(config, True, Mock(), lambda text: text)
    client.submit.assert_called_once()
    assert client.submit.call_args.args[0] == "encerrar chamada"


def test_farewell_drains_before_call_cleanup():
    client = Mock()
    client.snapshot.return_value = []
    client.messages = [{"id": "bye", "state": "done", "result": "Até mais!", "action": "end_call", "finished_at": time.time() + 60}]
    player = Mock(voice="teste")
    drained = threading.Event()
    player.wait_idle.side_effect = drained.set
    config = SimpleNamespace(intelligence=SimpleNamespace(default_model="test"))

    def input_until_farewell(prompt):
        assert drained.wait(2)
        raise EOFError

    with patch.object(runtime, "TaskClient", return_value=client), patch.object(runtime, "SpeechOutput", return_value=player), patch("builtins.input", side_effect=input_until_farewell):
        runtime.run(config, True, Mock(), lambda text: text)
    names = [call[0] for call in player.mock_calls]
    assert names.index("speak") < names.index("wait_idle") < names.index("close")


class ContinuousCallTests(unittest.TestCase):
    test_interrupt = staticmethod(test_interruption_restarts_busy_serial_synthesis_for_uncached_response)
    test_failure = staticmethod(test_failure_voice_is_short_and_does_not_disclose_technical_error)
    test_routing = staticmethod(test_end_phrase_is_submitted_to_ai_instead_of_local_routing)
    test_farewell = staticmethod(test_farewell_drains_before_call_cleanup)


if __name__ == "__main__":
    unittest.main()
