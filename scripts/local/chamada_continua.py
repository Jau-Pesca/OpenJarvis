"""Listen while a task mailbox works and interrupt only assistant playback."""
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import io
import json
import os
import queue
import re
import subprocess
import threading
import time
from urllib.parse import urlparse
import uuid

from audio_continuo import EchoReference, VoiceActivity, wav_bytes


def spoken_result(item, conversation=False):
    """Technical failures remain in the transcript; voice uses a short message."""
    if item.get("state") == "done":
        return item.get("voice_message") or item.get("result", "")
    message = item.get("voice_message")
    if isinstance(message, str) and message.strip():
        return message.strip()[:240]
    return "Não consegui responder. Veja os detalhes na interface." if conversation else "Não consegui concluir a tarefa. Veja os detalhes na interface."


class TaskClient:
    def __init__(self, config, api_url=None):
        self.model = os.environ.get("OJ_CALL_MODEL") or config.intelligence.default_model
        self.session = os.environ.get("OJ_TASK_SESSION") or "voice-" + (os.environ.get("OJ_INTERFACE_TOKEN") or uuid.uuid4().hex)
        self.manager = self.http = None
        self.api_url = api_url
        self.messages = []
        if api_url:
            if urlparse(api_url).hostname not in {"127.0.0.1", "localhost", "::1"}:
                raise ValueError("A chamada deve usar um servidor local.")
            import httpx
            self.http = httpx.Client(base_url=api_url, timeout=5, trust_env=False)
        else:
            from openjarvis.agents.business import BusinessAgent
            from openjarvis.agents.task_runtime import TaskManager
            from openjarvis.engine.ollama import OllamaEngine
            engine = OllamaEngine(host="http://127.0.0.1:11434", timeout=120)
            self.manager = TaskManager(BusinessAgent(engine, self.model, max_turns=config.agent.max_turns))

    def _request(self, method, path, **kwargs):
        response = self.http.request(method, "/v1/business-tasks/" + path, **kwargs)
        if not response.is_success:
            try:
                message = response.json().get("detail", "Falha na tarefa.")
            except ValueError:
                message = "O servidor não respondeu corretamente."
            raise RuntimeError(str(message))
        return response.json()

    def submit(self, text, history):
        if self.manager:
            return self.manager.message(text, self.session, history[-12:], model=self.model)
        return self._request("POST", "submit", json={"text": text, "session": self.session, "history": history[-12:], "model": self.model})

    def snapshot(self):
        if self.manager:
            self.messages = self.manager.dialogue_snapshot(self.session)
            return self.manager.snapshot(self.session)
        response = self._request("GET", "status", params={"session": self.session})
        self.messages = response.get("messages", [])
        return response["tasks"]

    def cancel(self, task_id):
        if self.manager:
            self.manager.cancel(task_id, self.session)
        else:
            self._request("POST", "cancel", json={"task_id": task_id, "session": self.session})

    def close(self):
        if self.http:
            self.http.close()
        if self.manager:
            self.manager.close()


class SpeechOutput:
    def __init__(self, report, clean, ready, echo):
        self.report, self.clean, self.ready, self.echo = report, clean, ready, echo
        self.lock = threading.Condition(threading.RLock())
        self.messages = deque()
        self.closed = False
        self.version = 0
        self.stream = self.say = None
        self.neural = None
        self.neural_factory = None
        self.rendering = False
        self.restart_neural = False
        self.busy = False
        self.cache = {}
        self.synthesis = ThreadPoolExecutor(max_workers=1, thread_name_prefix="call-synthesis")
        self.voice = os.environ.get("OJ_VOICE", "Eddy (Português (Brasil))")
        if os.environ.get("OJ_TTS_BACKEND", "macos") == "kokoro":
            from voz_neural_client import NeuralVoice
            self.neural_factory = NeuralVoice
            self.neural = self.neural_factory()
            self.voice = "Kokoro / " + os.environ.get("OJ_NEURAL_VOICE", "pf_dora")
        self.worker = threading.Thread(target=self._work, name="call-playback", daemon=True)
        self.worker.start()

    def speak(self, text):
        text = self.clean(text)
        if not text:
            return
        with self.lock:
            if self.closed:
                return
            self.messages.append((self.version, text))
            self.lock.notify_all()

    def interrupt(self):
        with self.lock:
            self.version += 1
            self.messages.clear()
            if self.say and self.say.poll() is None:
                self.say.terminate()
            stream = self.stream
            # A running Future cannot be cancelled. Stop the serial Kokoro
            # worker so stale synthesis cannot block the next response.
            if getattr(self, "rendering", False) and self.neural:
                self.restart_neural = True
                try:
                    self.neural.process.kill()
                except ProcessLookupError:
                    pass
            self.lock.notify_all()
        if stream:
            try:
                stream.abort()
            except Exception:
                pass
        self.report("listening")

    def wait_idle(self, timeout=15):
        with self.lock:
            return self.lock.wait_for(lambda: not self.messages and not self.busy, timeout=timeout)

    def _valid(self, version):
        with self.lock:
            return not self.closed and version == self.version

    def capture_blocked(self):
        """Speaker mode excludes playback and its acoustic tail, not synthesis."""
        with self.lock:
            playing = self.stream is not None or self.say is not None
            return playing or time.monotonic() < getattr(self, '_capture_resume_at', 0)

    def _play(self, audio, rate, version):
        import numpy as np
        import sounddevice as sd
        import soundfile as sf
        samples, source_rate = sf.read(io.BytesIO(audio), dtype="float32")
        if samples.ndim > 1:
            samples = samples.mean(axis=1)
        if source_rate != 16000:
            samples = np.interp(np.arange(round(len(samples) * 16000 / source_rate)) * source_rate / 16000, np.arange(len(samples)), samples).astype(np.float32)
        offset = 0
        def output(outdata, frames, timing, status):
            nonlocal offset
            outdata.fill(0)
            if not self._valid(version):
                raise sd.CallbackStop()
            length = min(frames, len(samples) - offset)
            outdata[:length, 0] = samples[offset:offset + length]
            self.echo.push(outdata[:, 0])
            offset += length
            if offset >= len(samples):
                raise sd.CallbackStop()
        if not self._valid(version):
            return
        stream = sd.OutputStream(samplerate=16000, channels=1, dtype="float32", blocksize=1024, callback=output)
        # Publish the capture gate before __enter__ starts PortAudio playback.
        with self.lock:
            self.stream = stream
        try:
            with stream:
                self.report("speaking")
                while stream.active and self._valid(version):
                    time.sleep(0.02)
        finally:
            with self.lock:
                self.stream = None
                self._capture_resume_at = time.monotonic() + 0.5

    def _work(self):
        while True:
            with self.lock:
                self.lock.wait_for(lambda: self.closed or self.messages)
                if self.closed:
                    return
                version, text = self.messages.popleft()
                self.busy = True
            try:
                while self._valid(version) and not self.ready():
                    time.sleep(0.03)
                if not self._valid(version):
                    continue
                chunks = [text] if text in self.cache else re.findall(r".{1,280}(?:\s+|$)|.{1,280}", text, re.S)
                for chunk in chunks:
                    if not self._valid(version):
                        break
                    if self.neural:
                        rendered = self.cache.get(chunk)
                        if rendered is None:
                            if getattr(self, "restart_neural", False):
                                self.neural.close()
                                self.neural = self.neural_factory()
                                self.restart_neural = False
                            with self.lock:
                                if not self._valid(version):
                                    break
                                self.rendering = True
                                pending = self.synthesis.submit(self.neural.render, chunk)
                            while self._valid(version) and not pending.done():
                                time.sleep(0.03)
                            with self.lock:
                                self.rendering = False
                            if not self._valid(version):
                                pending.cancel()
                                break
                            rendered = pending.result()
                        if self._valid(version):
                            self._play(*rendered, version)
                    else:
                        with self.lock:
                            if not self._valid(version):
                                break
                            self.say = subprocess.Popen(["/usr/bin/say", "-v", self.voice, "-r", "180", chunk])
                            self.report("speaking")
                        self.say.wait()
                        with self.lock:
                            self.say = None
                            self._capture_resume_at = time.monotonic() + 0.5
                while os.environ.get("OJ_VOICE_BARGE_IN") != "1" and self._valid(version) and self.capture_blocked():
                    time.sleep(0.02)
                if self._valid(version):
                    self.report("listening")
            except Exception as exc:
                if self._valid(version):
                    self.report("error", error=f"Falha na reprodução: {exc}")
            finally:
                with self.lock:
                    self.busy = False
                    self.rendering = False
                    self.lock.notify_all()

    def close(self):
        with self.lock:
            self.closed = True
            self.lock.notify_all()
        self.interrupt()
        self.worker.join(timeout=3)
        if self.neural:
            self.neural.close()
        self.synthesis.shutdown(wait=False, cancel_futures=True)
        self.worker.join(timeout=1)


def run(config, text_mode, report, clean):
    call_started = time.time()
    stop = threading.Event()
    recording = threading.Event()
    interpreting = threading.Event()
    utterances = queue.Queue(maxsize=8)
    echo = EchoReference()
    history = json.loads(os.environ.get("OJ_TASK_HISTORY", "[]"))
    history = [m for m in history[-12:] if isinstance(m, dict) and m.get("role") in {"user", "assistant"} and isinstance(m.get("content"), str)] if isinstance(history, list) else []
    history_lock = threading.Lock()
    tasks_lock = threading.Lock()
    last_tasks = []
    last_answer = [""]
    client = TaskClient(config, os.environ.get("OJ_API_URL"))
    player = speech = None
    threads = []
    try:
        if not text_mode:
            os.environ["HF_HUB_OFFLINE"] = "1"
            from openjarvis.speech.faster_whisper import FasterWhisperBackend
            speech = FasterWhisperBackend(model_size="small", device="cpu", compute_type="int8")
            if not speech.health():
                raise RuntimeError(f"Whisper indisponível: {speech.last_error()}")
        player = SpeechOutput(report, clean, lambda: not recording.is_set() and not interpreting.is_set(), echo)
        report("starting", model=client.model, voice=player.voice)
        print("Voz carregada. Preparando a conversa contínua…", flush=True)
        print("O agente principal decide quando conversar ou pedir ajuda. Fones ajudam a evitar eco.", flush=True)

        def accept(text):
            text = text.strip()
            if not text:
                return
            print(f"Você: {text}", flush=True)
            report(role="user", text=text)
            with history_lock:
                submitted = client.submit(text, list(history))
                history.append({"role": "user", "content": text})
                del history[:-12]
            answer = submitted["acknowledgement"]
            if submitted["action"] == "chat_pending":
                report("thinking")
                return
            print(f"OpenJarvis: {answer}", flush=True)
            report(role="assistant", text=answer)
            # A completed result may have arrived while the user was speaking.
            # Their acknowledgement takes precedence; full results remain in
            # the transcript/task panel and can be repeated on request.
            player.interrupt()
            player.speak(answer)

        def interpret():
            while not stop.is_set():
                try:
                    audio = utterances.get(timeout=0.2)
                except queue.Empty:
                    continue
                try:
                    report("transcribing")
                    text = speech.transcribe(audio, format="wav", language="pt").text.strip()
                    if not stop.is_set():
                        accept(text)
                except Exception as exc:
                    report("error", error=f"Não consegui entender ou enviar o pedido: {exc}")
                finally:
                    if utterances.empty():
                        interpreting.clear()

        def poll():
            delivered = set()
            failures = 0
            while not stop.wait(0.5):
                try:
                    snapshot = client.snapshot()
                    if stop.is_set():
                        break
                    failures = 0
                    with tasks_lock:
                        last_tasks[:] = snapshot
                    report(tasks=[{k: t[k] for k in ("id", "query", "revision", "state", "stage")} for t in snapshot[-12:]])
                    for message in client.messages:
                        key = (message["id"], "conversation")
                        if message["state"] not in {"done", "error"} or key in delivered:
                            continue
                        delivered.add(key)
                        if message.get("finished_at", 0) < call_started:
                            continue
                        answer = message["result"] if message["state"] == "done" else "Ocorreu um erro ao processar sua mensagem: " + message.get("error", "Erro sem detalhes.")
                        with history_lock:
                            history.append({"role": "assistant", "content": answer})
                            del history[:-12]
                        last_answer[0] = answer
                        print(f"OpenJarvis: {answer}", flush=True)
                        report(role="assistant", text=answer)
                        player.speak(spoken_result(message, conversation=True))
                        if message.get("action") == "end_call":
                            player.wait_idle()
                            stop.set()
                            return
                    for task in snapshot:
                        key = (task["id"], task["revision"])
                        if task["state"] not in {"done", "error"} or key in delivered:
                            continue
                        delivered.add(key)
                        if task.get("finished_at", 0) < call_started:
                            continue
                        answer = task["result"] if task["state"] == "done" else "Não consegui concluir a tarefa: " + task["error"]
                        last_answer[0] = answer
                        with history_lock:
                            history.append({"role": "assistant", "content": answer})
                            del history[:-12]
                        print(f"OpenJarvis: {answer}", flush=True)
                        report(role="assistant", text=answer)
                        player.speak(spoken_result(task))
                except Exception as exc:
                    failures += 1
                    if failures in {1, 10}:
                        report("error", error=f"Não consegui consultar as tarefas: {exc}")

        threads.append(threading.Thread(target=poll, name="call-results", daemon=True))
        if not text_mode:
            threads.append(threading.Thread(target=interpret, name="call-whisper", daemon=True))
        for thread in threads:
            thread.start()
        if text_mode:
            report("listening")
            while not stop.is_set():
                text = input("Você: ")
                player.interrupt()
                try:
                    accept(text)
                except Exception as exc:
                    report("error", error=str(exc))
                    print(f"Falha: {exc}", flush=True)
        else:
            import sounddevice as sd
            vad = VoiceActivity(threshold=int(os.environ.get("OJ_MIC_THRESHOLD", "900")), silence_seconds=float(os.environ.get("OJ_MIC_SILENCE_SECONDS", "0.8")))
            with sd.RawInputStream(samplerate=16000, channels=1, dtype="int16", blocksize=1024) as stream:
                report("listening")
                barge_in = os.environ.get("OJ_VOICE_BARGE_IN") == "1"
                print("Modo fones: interrupção por voz habilitada." if barge_in else "Modo alto-falante: fale após a resposta para evitar autoescuta.", flush=True)
                while not stop.is_set():
                    raw, overflow = stream.read(1024)
                    raw = bytes(raw)
                    if not barge_in and player.capture_blocked():
                        vad.reset()
                        recording.clear()
                        continue
                    cleaned, amplitude = echo.filter(raw)
                    began, frames = vad.feed(cleaned, amplitude)
                    if began:
                        recording.set()
                        player.interrupt()
                    if frames:
                        interpreting.set()
                        try:
                            utterances.put_nowait(wav_bytes(frames))
                        except queue.Full:
                            report("error", error="Há muitas falas aguardando transcrição. Aguarde um instante.")
                        recording.clear()
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        stop.set()
        if player:
            player.close()
        for thread in threads:
            thread.join(timeout=1)
        client.close()
        message = "Chamada encerrada. As tarefas do servidor permanecem disponíveis na interface." if client.http else "Chamada encerrada. As tarefas desta sessão local foram interrompidas."
        print(message, flush=True)
        report("idle")
