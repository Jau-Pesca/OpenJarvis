"""Real Kokoro interruption check without playing audio or using microphone."""
import importlib.util
from pathlib import Path
import sys
import threading
import time

root = Path.home()/'OpenJarvis-local'
sys.path.insert(0, str(root))
spec = importlib.util.spec_from_file_location('installed_call', root/'chamada_continua.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
received = threading.Event()
played = []

def report(*args, **kwargs):
    if args and args[0] == 'error':
        print('VOICE_ERROR',kwargs.get('error'),flush=True)

started = time.monotonic()
player = module.SpeechOutput(report,lambda text:text,lambda:True, None)
assert player.neural is not None, 'Use OJ_TTS_BACKEND=kokoro'
print('VOICE_READY_SECONDS',round(time.monotonic()-started,2),flush=True)

def capture(audio, rate, version):
    assert audio[:4] == b'RIFF' and rate > 0
    played.append((len(audio),rate,version))
    received.set()

player._play = capture
try:
    player.speak('Esta resposta será interrompida antes de terminar. ' * 40)
    deadline = time.monotonic()+5
    while not player.rendering and time.monotonic()<deadline:
        time.sleep(.01)
    assert player.rendering, 'Síntese não iniciou'
    started = time.monotonic()
    player.interrupt()
    player.speak('Certo. Vou abrir para você.')
    assert received.wait(60), 'Nova resposta bloqueada após interrupção'
    assert player.wait_idle(5)
    print('NEW_RESPONSE_SECONDS',round(time.monotonic()-started,2),flush=True)
    print('AUDIO_EVIDENCE',played,flush=True)
    assert len(played)==1 and played[0][2]==1, played
    print('PASS: nova síntese real após interrupção; sem playback/microfone.',flush=True)
finally:
    player.close()
