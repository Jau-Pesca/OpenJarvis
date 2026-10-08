"""Local-only HTTP mailbox; submission never waits for model inference."""
from fastapi import APIRouter, HTTPException, Request
import asyncio
from pydantic import BaseModel, Field
from typing import Literal

from openjarvis.server.local_call import _local_request


class TaskSubmission(BaseModel):
    model: str | None = Field(default=None, min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=12000)
    session: str = Field(default="chat", max_length=100)
    mode: Literal["auto", "new", "context"] = "auto"
    target: str | None = None
    history: list[dict[str, str]] = Field(default_factory=list, max_length=12)


class TaskCancellation(BaseModel):
    task_id: str
    session: str


def create_business_task_router(manager):
    router = APIRouter(prefix="/v1/business-tasks", tags=["business-tasks"])

    def require(request):
        _local_request(request)
        if manager is None:
            raise HTTPException(503, "Reabra a interface com o agente de negócios habilitado.")

    @router.post("/submit")
    async def submit(body: TaskSubmission, request: Request):
        require(request)
        try:
            return await asyncio.to_thread(manager.message, body.text, body.session, body.history, body.mode, body.target, model=body.model)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc

    @router.get("/status")
    async def status(request: Request, session: str | None = None):
        require(request)
        return {"tasks": manager.snapshot(session), "messages": manager.dialogue_snapshot(session)}

    @router.get("/events")
    async def events(request: Request, task_id: str):
        require(request)
        try:
            return {"events": await asyncio.to_thread(manager.read_events, task_id)}
        except ValueError as exc:
            raise HTTPException(503, str(exc)) from exc

    @router.post("/cancel")
    async def cancel(body: TaskCancellation, request: Request):
        require(request)
        try:
            manager.cancel(body.task_id, body.session)
            return {"status": "cancelled"}
        except ValueError as exc:
            raise HTTPException(404, str(exc)) from exc

    return router
