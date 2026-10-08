"""Select future defaults without disturbing Ollama's idle model cache."""
import threading
from contextlib import ExitStack

import httpx

_SWITCH_LOCK = threading.RLock()


def select_without_loading(state, engine, model, agent_lock):
    with _SWITCH_LOCK, agent_lock:
        return select_business_model(state, engine, model)


def preload_and_select(state, engine, model, agent_lock):
    # Serialize explicit load/selection, also against the
    # non-stream agent's override/run/restore lock.
    with _SWITCH_LOCK, agent_lock:
        with httpx.Client(base_url=engine._host, timeout=120, trust_env=False) as client:
            response = client.post('/api/generate', json={
                'model': model, 'prompt': '', 'keep_alive': '5m', 'stream': False,
            })
            response.raise_for_status()
        return select_business_model(state, engine, model)


def select_business_model(state, engine, model):
    manager = getattr(state, 'business_tasks', None)
    agent = getattr(state, 'agent', None)
    if manager is None or getattr(agent, 'agent_id', None) != 'business':
        return {'unloaded': [], 'retained': []}
    call = getattr(state, 'local_call', None)
    # Run in a worker thread: never carry thread locks across an async await.
    with _SWITCH_LOCK, ExitStack() as locks:
        locks.enter_context(manager.lock)
        if call is not None:
            locks.enter_context(call.lock)
        previous = getattr(state, 'model', None) or manager.model
        # Selection never generates, unloads or refreshes an idle timer.
        # Each inference requests five minutes; Ollama owns expiration/eviction.
        retained = [previous] if previous and previous != model else []
        # Only future requests change defaults; Task.model is already captured.
        state.model = model
        manager.model = model
        agent._model = model
        return {'unloaded': [], 'retained': retained}
