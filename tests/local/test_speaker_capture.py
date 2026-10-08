import importlib.util
from pathlib import Path
import time
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from test_continuous_call import runtime, bare_player

spec = importlib.util.spec_from_file_location('audio_reviewable', Path(__file__).resolve().parents[2]/'scripts/local/audio_continuo.py')
audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio)


class SpeakerTests(unittest.TestCase):
    def test_playback_and_echo_tail_block_but_synthesis_does_not(self):
        player = bare_player()
        try:
            player.rendering = True
            self.assertFalse(player.capture_blocked())
            player.stream = object()
            self.assertTrue(player.capture_blocked())
            player.stream = None
            player._capture_resume_at = time.monotonic()+.5
            self.assertTrue(player.capture_blocked())
            player._capture_resume_at = time.monotonic()-1
            self.assertFalse(player.capture_blocked())
            player.say = object()
            self.assertTrue(player.capture_blocked())
        finally:
            player.synthesis.shutdown(wait=False)

    def test_reset_discards_playback_utterance_before_transcription(self):
        detector = audio.VoiceActivity()
        for _ in range(3): detector.feed(b'echo', 1900)
        self.assertTrue(detector.active)
        detector.reset()
        for _ in range(20):
            began, frames = detector.feed(b'quiet', 0)
            self.assertFalse(began)
            self.assertIsNone(frames)
        self.assertFalse(detector.active)


    def test_gate_precedes_stream_start_and_outlives_close(self):
        import numpy as np
        player = bare_player()
        class Stream:
            active = False
            def __enter__(self):
                assert player.capture_blocked(), 'audio started before capture gate'
                return self
            def __exit__(self, *args):
                assert player.capture_blocked(), 'gate released before stream closed'
        try:
            with patch.dict(sys.modules, {'sounddevice': SimpleNamespace(OutputStream=lambda **kw: Stream()),
                                          'soundfile': SimpleNamespace(read=lambda *a, **kw: (np.zeros(16), 16000))}):
                runtime.SpeechOutput._play(player, b'fixture', 16000, 0)
            self.assertTrue(player.capture_blocked())
        finally:
            player.synthesis.shutdown(wait=False)
