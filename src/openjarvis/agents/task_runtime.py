"""Responsive task mailbox with FIFO work and cooperative redirection."""
from __future__ import annotations

from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import threading
import os
import time
import unicodedata
import uuid
import json
from pathlib import Path

from openjarvis.agents._stubs import AgentContext
from openjarvis.core.types import Conversation, Message, Role


def normalized(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))


class TaskInterrupted(Exception):
    """Stop at the next model/tool boundary; never publish an obsolete answer."""


class TaskControl:
    def __init__(self, progress=None, trace=None):
        self.event = threading.Event()
        self._progress = progress or (lambda stage: None)
        self._trace = trace or (lambda **event: None)

    def check(self):
        if self.event.is_set():
            raise TaskInterrupted()

    def progress(self, stage):
        self.check()
        self._progress(stage)
        self.trace("stage", stage)

    def trace(self, kind, stage, **details):
        self.check()
        self._trace(kind=kind, stage=stage, **details)


class ControlledEngine:
    def __init__(self, engine, control):
        self.inner, self.control = engine, control

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def generate(self, *args, **kwargs):
        self.control.check()
        started = time.monotonic()
        self.control.trace('model', 'Consultando IA', status='started', model=kwargs.get('model', ''))
        try:
            result = self.inner.generate(*args, **kwargs)
        except Exception:
            self.control.trace('model', 'Consulta à IA falhou', status='error', model=kwargs.get('model', ''), duration_ms=round((time.monotonic()-started)*1000))
            raise
        self.control.check()
        self.control.trace('model', 'IA respondeu', status='done', model=kwargs.get('model', ''), duration_ms=round((time.monotonic()-started)*1000), tokens=int(result.get('usage', {}).get('total_tokens', 0) or 0))
        return result


@dataclass
class Task:
    id: str
    session: str
    query: str
    history: list = field(default_factory=list)
    amendments: list = field(default_factory=list)
    user_statements: list = field(default_factory=list)
    revision: int = 1
    state: str = "queued"
    stage: str = "Na fila"
    result: str = ""
    error: str = ""
    error_details: str = ""
    control: TaskControl | None = None
    created_at: float = field(default_factory=time.time)
    finished_at: float = 0.0
    model: str | None = None
    usage: dict = field(default_factory=dict)
    requires_execution: bool = False
    delegated_goal: str = ""
    notes_processed: bool = False
    events: list = field(default_factory=list)
    failure_stage: str = ""
    stage_started_at: float = field(default_factory=time.time)
    stage_started_monotonic: float = field(default_factory=time.monotonic)
    trace_error: bool = False


class TaskManager:
    def __init__(self, agent):
        self.agent = agent
        self.model = getattr(agent, "_model", None)
        self.lock = threading.Condition(threading.RLock())
        self.tasks = {}
        self.queue = deque()
        self.closed = False
        self.dialogues = {}
        graph_path = getattr(getattr(agent, "graph", None), "path", None)
        self.trace_path = Path(graph_path).parent / "logs/task-events.jsonl" if graph_path else None
        self.desktop = None
        if os.environ.get("OJ_DESKTOP_CONTROL") == "1":
            from openjarvis.tools.mac_desktop import DesktopSessions
            self.desktop = DesktopSessions()
        self.conversation_worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="main-conversation")
        self.worker = threading.Thread(target=self._work, name="business-mailbox", daemon=True)
        self.worker.start()

    def message(self, text, session="chat", history=None, mode="auto", target=None, model=None):
        """Let the main agent converse; delegate only a work request."""
        text = text.strip()
        if not text or len(text) > 12000:
            raise ValueError("Informe uma mensagem de até 12000 caracteres.")
        if mode != "auto" or target:
            return self.submit(text, session, history, mode, target, model)
        with self.lock:
            if self.closed:
                raise ValueError("O servidor está encerrando.")
            for dialogue in self.dialogues.values():
                if dialogue["session"] == session and dialogue["state"] == "pending":
                    dialogue["control"].event.set()
                    dialogue["state"] = "cancelled"
        message_id = uuid.uuid4().hex
        def trace_dialogue(**event):
            with self.lock:
                current = self.dialogues.get(message_id)
                if current and current['state'] == 'pending':
                    current['stage'] = event['stage']
        control = TaskControl(trace=trace_dialogue)
        with self.lock:
            self.dialogues[message_id] = {"id": message_id, "session": session, "state": "pending", "result": "", "error": "", "control": control, "finished_at": 0.0, "created_at": time.time(), "model": model or self.model, "stage": "Verificando navegador"}
            finished = [key for key, d in self.dialogues.items() if d["state"] != "pending"]
            for key in finished[:-50]:
                self.dialogues.pop(key, None)
        self.conversation_worker.submit(self._converse, message_id, text, history or [], model)
        return {"action": "chat_pending", "task_id": None, "message_id": message_id, "acknowledgement": ""}

    def _converse(self, message_id, text, history, model):
        with self.lock:
            dialogue = self.dialogues[message_id]
            control = dialogue["control"]
        try:
            control.check()
            computer = None
            if self.desktop:
                try:
                    computer = self.desktop.status(dialogue["session"])
                except Exception as exc:
                    computer = {"available": False, "error": str(exc)}
            context = AgentContext(conversation=Conversation(messages=[Message(role=Role(m["role"]), content=m["content"]) for m in history[-12:] if m.get("role") in {"user", "assistant"}]), metadata={"task_control": control, "tasks": self.snapshot(dialogue["session"])[-20:], "computer": computer})
            answer = self.agent.chat(text, context=context, model=model or self.model)
            control.check()
            decision = answer.metadata.get("decision")
            if not isinstance(decision, dict):
                raise ValueError("O agente principal não informou sua decisão.")
            approved_goal = None
            if decision.get("action") == "approve_browser":
                if not self.desktop:
                    raise ValueError("O controle nativo não está habilitado.")
                approved_goal = self.desktop.grant(dialogue["session"])
                try:
                    control.check()
                except TaskInterrupted:
                    self.desktop.release(dialogue["session"])
                    raise
            # Validate/execute under one lock so a newer turn cannot invalidate
            # this decision between its control check and scheduling work.
            with self.lock:
                control.check()
                action = decision.get("action")
                execution = None
                if action == "delegate":
                    execution = self.submit(decision["task"], dialogue["session"], history, "new", model=model, user_text=text)
                elif action == "redirect":
                    execution = self.submit(decision["task"], dialogue["session"], history, "context", decision["target"], model, expected_revision=decision["revision"], user_text=text)
                elif action == "cancel":
                    self.cancel(decision["target"], dialogue["session"])
                elif action == "request_browser":
                    if not self.desktop:
                        raise ValueError("O controle nativo não está habilitado.")
                    self.desktop.request(dialogue["session"], decision["target"], decision["task"])
                elif action == "approve_browser":
                    if not self.desktop:
                        raise ValueError("O controle nativo não está habilitado.")
                    execution = self.submit(approved_goal, dialogue["session"], history, "new", model=model, user_text=approved_goal)
                elif action == "deny_browser":
                    if self.desktop:
                        self.desktop.release(dialogue["session"])
                elif action not in {"reply", "end_call"}:
                    raise ValueError("Decisão desconhecida do agente principal.")
                if execution:
                    current = self.tasks[execution["task_id"]]
                    required = decision.get("requires_execution", action == "delegate")
                    current.notes_processed = True
                    current.requires_execution = current.requires_execution or action == "approve_browser" or required is True
                import logging
                logging.getLogger(__name__).info("Principal action=%s; scheduled=%s; model=%s", action, bool(execution), model or self.model)
                dialogue.update(state="done", result=answer.content, action=action, task_id=execution["task_id"] if execution else None, finished_at=time.time())
        except TaskInterrupted:
            with self.lock:
                dialogue["state"] = "cancelled"
        except Exception as exc:
            import logging
            logging.getLogger(__name__).exception("Principal conversation failed (message_id=%s)", message_id)
            with self.lock:
                dialogue.update(state="error", error=str(exc)[:1000], finished_at=time.time())

    def dialogue_snapshot(self, session=None):
        with self.lock:
            return [{**{k: v for k, v in d.items() if k != "control"}, "elapsed_seconds": round((d["finished_at"] or time.time()) - d["created_at"], 1)} for d in self.dialogues.values() if session is None or d["session"] == session]

    def submit(self, text, session="chat", history=None, mode="auto", target=None, model=None, expected_revision=None, user_text=None):
        text = text.strip()
        if not text or len(text) > 12000:
            raise ValueError("Informe um pedido de até 12000 caracteres.")
        with self.lock:
            if self.closed:
                raise ValueError("O servidor está encerrando.")
            task = self.tasks.get(target) if target else None
            if target and task is None:
                raise ValueError("Tarefa não encontrada.")
            if task and (task.session != session or task.state not in {"queued", "running", "redirecting"}):
                raise ValueError("Essa tarefa não está disponível para receber complementos.")
            if mode == "context" and task is None:
                raise ValueError("Informe a tarefa que deve receber o complemento.")
            if task and expected_revision is not None and task.revision != expected_revision:
                raise ValueError("A tarefa mudou desde a decisão do modelo. Envie o complemento novamente.")
            if task and mode != "new":
                if len(task.amendments) >= 20:
                    raise ValueError("Esta tarefa já recebeu muitos complementos; crie uma nova tarefa.")
                amendment = user_text or text
                if user_text and user_text != text:
                    amendment += "\nResumo do complemento pela IA: " + text
                task.notes_processed = False
                task.amendments.append(amendment)
                task.user_statements.append(user_text or text)
                if model:
                    task.model = model
                task.revision += 1
                if task.control:
                    task.control.event.set()
                    task.state = "redirecting"
                    task.stage = "Incorporando seu complemento"
                    self._record_event(task, kind="stage", stage=task.stage, status="started")
                acknowledgement = ""
                action = "redirected"
            else:
                if sum(t.state in {"queued", "running", "redirecting"} for t in self.tasks.values()) >= 50:
                    raise ValueError("A fila está cheia. Aguarde uma tarefa terminar.")
                task = Task(uuid.uuid4().hex, session, user_text or text, history or [])
                task.delegated_goal = text
                task.model = model or self.model
                task.user_statements.append(user_text or text)
                self.tasks[task.id] = task
                self._record_event(task, kind="stage", stage="Na fila")
                self.queue.append(task.id)
                acknowledgement = ""
                action = "queued"
            # Bounded history: never evict unfinished tasks.
            finished = [t.id for t in self.tasks.values() if t.state in {"done", "error", "cancelled"}]
            for key in finished[:-100]:
                self.tasks.pop(key, None)
            self.lock.notify_all()
            return {"task_id": task.id, "revision": task.revision, "action": action, "acknowledgement": acknowledgement}

    def snapshot(self, session=None):
        with self.lock:
            return [{"id": t.id, "session": t.session, "query": t.query, "revision": t.revision,
                     "state": t.state, "stage": t.stage, "result": t.result, "error": t.error,
                     "error_details": t.error_details, "model": t.model,
                     "created_at": t.created_at, "elapsed_seconds": round((t.finished_at or time.time()) - t.created_at, 1),
                     "stage_seconds": round((t.finished_at or time.time()) - t.stage_started_at, 1),
                     "events": [dict(e) for e in t.events], "failure_stage": t.failure_stage, "trace_error": t.trace_error,
                     "voice_message": t.error if t.state == "error" else "",
                     "finished_at": t.finished_at, "usage": dict(t.usage),
                     "amendments": list(t.amendments)} for t in self.tasks.values() if session is None or t.session == session]

    def _record_event(self, task, **details):
        # Only caller-supplied structural fields; never model output/arguments.
        allowed = {'kind', 'stage', 'status', 'model', 'tool', 'duration_ms', 'tokens', 'error_code'}
        event = {k: v for k, v in details.items() if k in allowed}
        event.update(task_id=task.id, revision=task.revision, sequence=(task.events[-1]['sequence']+1 if task.events else 1), timestamp=time.time())
        task.events.append(event)
        task.events[:] = task.events[-200:]
        if self.trace_path:
            try:
                self.trace_path.parent.mkdir(parents=True, exist_ok=True)
                if self.trace_path.exists() and self.trace_path.stat().st_size > 5*1024*1024:
                    self.trace_path.replace(self.trace_path.with_suffix('.previous.jsonl'))
                with self.trace_path.open('a', encoding='utf-8') as file:
                    file.write(json.dumps(event, ensure_ascii=False)+'\n')
            except OSError:
                task.trace_error = True

    def read_events(self, task_id):
        with self.lock:
            if task_id in self.tasks:
                return [dict(e) for e in self.tasks[task_id].events]
            events = []
            if self.trace_path:
                for path in (self.trace_path.with_suffix('.previous.jsonl'), self.trace_path):
                    try:
                        lines = path.read_text(encoding='utf-8').splitlines() if path.exists() else []
                    except (OSError, UnicodeError) as exc:
                        raise ValueError('Não foi possível ler o histórico de execução em disco.') from exc
                    for line in lines:
                            try:
                                event = json.loads(line)
                                if isinstance(event, dict) and event.get('task_id') == task_id:
                                    events.append(event)
                            except ValueError:
                                continue
            return events[-200:]

    def cancel(self, task_id, session):
        with self.lock:
            task = self.tasks.get(task_id)
            if not task or task.session != session:
                raise ValueError("Tarefa não encontrada.")
            if task.state in {"done", "error", "cancelled"}:
                return
            task.state, task.stage = "cancelled", "Cancelada"
            task.finished_at = time.time()
            self._record_event(task, kind="stage", stage="Cancelada", status="cancelled")
            if task.control:
                task.control.event.set()
            self.lock.notify_all()

    def _work(self):
        while True:
            with self.lock:
                self.lock.wait_for(lambda: self.closed or self.queue)
                if self.closed:
                    return
                task = self.tasks[self.queue.popleft()]
                if task.state == "cancelled":
                    continue
            while True:
                with self.lock:
                    if self.closed or task.state == "cancelled":
                        break
                    revision = task.revision
                    def progress(stage, current=task, version=revision):
                        with self.lock:
                            if current.revision == version and current.state == "running":
                                self._record_event(current, kind="stage", stage=current.stage, status="done", duration_ms=round((time.monotonic()-current.stage_started_monotonic)*1000))
                                current.stage = stage
                                current.stage_started_at = time.time()
                                current.stage_started_monotonic = time.monotonic()
                    def trace(current=task, version=revision, **event):
                        with self.lock:
                            if current.revision == version and current.state == "running":
                                self._record_event(current, **event)
                    control = TaskControl(progress, trace)
                    task.control, task.state, task.stage = control, "running", "Iniciando"
                    task.stage_started_at = time.time()
                    task.stage_started_monotonic = time.monotonic()
                    self._record_event(task, kind="stage", stage="Iniciando", status="started")
                    query = task.query + "".join("\nComplemento do usuário: " + a for a in task.amendments)
                    if task.delegated_goal and task.delegated_goal != task.query:
                        query += "\nObjetivo resumido pela IA (preserve o pedido original e seus complementos): " + task.delegated_goal
                    context = AgentContext(conversation=Conversation(messages=[Message(role=Role(item["role"]), content=item["content"]) for item in task.history[-12:] if item.get("role") in {"user", "assistant"}]), metadata={"task_control": control, "desktop": self.desktop, "desktop_session": task.session, "user_statements": "\n".join(task.user_statements), "requires_execution": task.requires_execution, "notes_processed": task.notes_processed})
                try:
                    options = {"model_override": task.model} if task.model else {}
                    outcome = getattr(self.agent, "run_task", self.agent.run)(query, context=context, **options)
                    with self.lock:
                        if task.state == "cancelled":
                            break
                        if revision != task.revision:
                            continue
                        failed = bool(outcome.metadata.get("error"))
                        if failed:
                            task.failure_stage = task.stage
                        self._record_event(task, kind="stage", stage=task.stage, status="error" if failed else "done", duration_ms=round((time.monotonic()-task.stage_started_monotonic)*1000))
                        task.state, task.stage = ("error", "Não foi possível concluir") if failed else ("done", "Concluída")
                        if failed:
                            task.error = outcome.metadata.get("voice_message") or outcome.content
                            task.error_details = outcome.metadata.get("error_details") or outcome.content
                        else:
                            task.result = outcome.content
                        task.finished_at = time.time()
                        task.usage = {key: outcome.metadata.get(key, 0) for key in ("prompt_tokens", "completion_tokens", "total_tokens")}
                        task.control = None
                        break
                except TaskInterrupted:
                    with self.lock:
                        if task.state == "cancelled" or self.closed:
                            break
                    continue
                except Exception as exc:
                    import logging
                    logging.getLogger(__name__).error("Task execution failed (task_id=%s; stage=%s; type=%s)", task.id, task.stage, type(exc).__name__)
                    with self.lock:
                        if task.state == "cancelled":
                            break
                        if revision != task.revision:
                            continue
                        task.failure_stage = task.stage
                        self._record_event(task, kind="stage", stage=task.stage, status="error", duration_ms=round((time.monotonic()-task.stage_started_monotonic)*1000))
                        task.state, task.stage, task.error = "error", "Não foi possível concluir", "Não consegui concluir o pedido. Confira os detalhes na interface."
                        task.error_details = str(exc)
                        task.finished_at = time.time()
                        task.control = None
                        break

            if self.desktop:
                with self.lock:
                    pending = any(t.session == task.session and t.state in {"queued", "running", "redirecting"} for t in self.tasks.values())
                if not pending:
                    self.desktop.release(task.session)

    def close(self):
        with self.lock:
            self.closed = True
            for task in self.tasks.values():
                if task.control:
                    task.control.event.set()
            for dialogue in self.dialogues.values():
                dialogue["control"].event.set()
            self.lock.notify_all()
        self.conversation_worker.shutdown(wait=False, cancel_futures=True)
