"""Manage the Mac's local voice session from the browser UI."""
from __future__ import annotations

import asyncio
from collections import deque
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
import time
from urllib.parse import urlparse
import uuid

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field


class LocalCall:
    def __init__(self, root: Path | None = None):
        self.root = root or Path.home() / "OpenJarvis-local"
        self.lock = threading.RLock()
        self.process = None
        self.call_id = None
        self.status = "idle"
        self.error = None
        self.model = ""
        self.voice = ""
        self.allow_interruptions = False
        self.transcript = deque(maxlen=20)
        self.heartbeat = 0.0
        self.tasks = []

    def snapshot(self, call_id=None):
        with self.lock:
            active = self.process is not None and self.process.poll() is None
            if active and call_id == self.call_id:
                self.heartbeat = time.monotonic()
            return {"active": active, "call_id": self.call_id, "status": self.status,
                    "instance_id": os.environ.get("OJ_INTERFACE_INSTANCE", ""),
                    "error": self.error, "voice": self.voice, "model": self.model, "allow_interruptions": self.allow_interruptions,
                    "transcript": list(self.transcript),
                    "tasks": list(self.tasks),
                    "available": (self.root / "iniciar-chamada-interface.sh").is_file()}

    def start(self, session=None, history=None, model=None, allow_interruptions=False):
        with self.lock:
            if self.process is not None and self.process.poll() is None:
                return self.snapshot()
            script = self.root / "iniciar-chamada-interface.sh"
            if not script.is_file():
                raise HTTPException(503, "A chamada local ainda não está configurada neste Mac.")
            self.allow_interruptions = allow_interruptions
            token = uuid.uuid4().hex
            process = subprocess.Popen(
                ["/bin/bash", "--noprofile", "--norc", str(script)],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, start_new_session=True,
                env={k: v for k, v in {**os.environ, "OJ_INTERFACE_TOKEN": token,
                     "OJ_TASK_SESSION": session or "voice-" + token,
                     "OJ_CALL_MODEL": model or "",
                     "OJ_VOICE_BARGE_IN": "1" if allow_interruptions else "0",
                     "OJ_TASK_HISTORY": json.dumps(history or [], ensure_ascii=False)}.items() if k != "BASH_ENV"},
            )
            self.process = process
            self.call_id = token
            self.status = "starting"
            self.error = None
            self.transcript.clear()
            self.tasks = []
            self.heartbeat = time.monotonic()
            threading.Thread(target=self._watch, args=(process, token), daemon=True).start()
            threading.Thread(target=self._lease, args=(process, token), daemon=True).start()
            return self.snapshot()

    def _watch(self, process, token):
        prefix = f"OJ_EVENT_{token}:"
        try:
            for line in process.stdout:
                if not line.startswith(prefix):
                    continue
                try:
                    event = json.loads(line[len(prefix):])
                except (ValueError, TypeError):
                    continue
                with self.lock:
                    if self.call_id != token:
                        continue
                    if event.get("status") in {"starting", "listening", "transcribing", "thinking", "speaking", "idle", "error"}:
                        self.status = event["status"]
                    for field in ("voice", "model", "error"):
                        if isinstance(event.get(field), str):
                            setattr(self, field, event[field][:1000])
                    if isinstance(event.get("tasks"), list):
                        self.tasks = [{"id": str(t.get("id", ""))[:100], "query": str(t.get("query", ""))[:500],
                                       "state": str(t.get("state", ""))[:40], "stage": str(t.get("stage", ""))[:100]}
                                      for t in event["tasks"][-12:] if isinstance(t, dict)]
                    if event.get("role") in {"user", "assistant"} and isinstance(event.get("text"), str):
                        self.transcript.append({"role": event["role"], "text": event["text"][:6000]})
                        self.error = None
            code = process.wait()
            with self.lock:
                if self.call_id == token:
                    if code not in (0, -signal.SIGINT, -signal.SIGTERM) and self.status != "stopping":
                        self.status = "error"
                        self.error = self.error or "Não consegui iniciar a chamada. Confira a instalação e a permissão do microfone no macOS."
                    elif self.status != "error":
                        self.status = "idle"
        finally:
            process.stdout.close()

    def _lease(self, process, token):
        # A closed or disconnected browser must not leave the microphone open.
        while process.poll() is None:
            time.sleep(1)
            with self.lock:
                expired = self.call_id == token and time.monotonic() - self.heartbeat > 30
            if expired:
                self.stop(token)
                return

    def stop(self, call_id):
        with self.lock:
            if call_id != self.call_id:
                raise HTTPException(409, "Esta chamada já foi encerrada ou substituída.")
            process = self.process
            if process is None or process.poll() is not None:
                return self.snapshot()
            self.status = "stopping"
        try:
            os.killpg(process.pid, signal.SIGINT)
            try:
                process.wait(timeout=4)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=2)
        except ProcessLookupError:
            pass
        with self.lock:
            if self.call_id == call_id:
                self.status = "idle"
            return self.snapshot()


class StopCall(BaseModel):
    call_id: str


class StartCall(BaseModel):
    allow_interruptions: bool = False
    model: str | None = Field(default=None, min_length=1, max_length=200)
    session: str | None = Field(default=None, max_length=100)
    history: list[dict[str, str]] = Field(default_factory=list, max_length=12)


def _local_request(request):
    host = request.client.host if request.client else ""
    if host not in {"127.0.0.1", "::1", "localhost", "testclient"}:
        raise HTTPException(403, "A chamada só pode ser iniciada neste Mac.")
    origin = request.headers.get("origin")
    if origin and urlparse(origin).hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise HTTPException(403, "Origem não autorizada para controlar o microfone.")


def create_local_call_router(manager):
    router = APIRouter(prefix="/v1/local-call", tags=["local-call"])

    @router.get("/status")
    async def status(request: Request, call_id: str | None = None):
        _local_request(request)
        return manager.snapshot(call_id)

    @router.post("/start")
    async def start(request: Request, body: StartCall | None = None):
        _local_request(request)
        return await asyncio.to_thread(manager.start, body.session if body else None, body.history[-12:] if body else None, body.model if body else None, body.allow_interruptions if body else False)

    @router.post("/stop")
    async def stop(body: StopCall, request: Request):
        _local_request(request)
        return await asyncio.to_thread(manager.stop, body.call_id)

    return router
