import { apiFetch } from './api';

export interface LocalCallState {
  active: boolean;
  allow_interruptions?: boolean;
  available: boolean;
  call_id: string | null;
  status: string;
  error: string | null;
  voice: string;
  model: string;
  transcript: { role: 'user' | 'assistant'; text: string }[];
  tasks?: { id: string; query: string; state: string; stage: string }[];
}

export const callStatusLabel = (status: string): string => ({
  idle: 'Chamada encerrada', starting: 'Preparando a chamada…',
  listening: 'Ouvindo você', transcribing: 'Entendendo sua fala…',
  thinking: 'Pensando…', speaking: 'Respondendo',
  stopping: 'Encerrando…', error: 'Confira a mensagem abaixo',
}[status] ?? 'Preparando a chamada…');

export async function localCallRequest(
  action: 'status' | 'start' | 'stop', callId?: string | null, keepalive = false,
  context?: { session: string; history: { role: string; content: string }[]; model?: string; allow_interruptions?: boolean },
): Promise<LocalCallState> {
  const query = action === 'status' && callId ? `?call_id=${encodeURIComponent(callId)}` : '';
  const response = await apiFetch(`/v1/local-call/${action}${query}`, action === 'status' ? {} : {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(action === 'stop' ? { call_id: callId } : context ?? {}), keepalive,
  });
  if (!response.ok) {
    if (response.status === 404) throw new Error('Reabra a interface para carregar o botão de chamada.');
    let detail = '';
    try { const data = await response.json(); if (typeof data.detail === 'string') detail = data.detail; } catch { /* Use a readable fallback. */ }
    throw new Error(detail || 'Não consegui conectar à chamada. Reabra a interface e tente novamente.');
  }
  return response.json();
}
