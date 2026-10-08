import { describe, expect, it, vi } from 'vitest';
vi.mock('./api', () => ({ apiFetch: vi.fn() }));
import { apiFetch } from './api';
import { callStatusLabel, localCallRequest } from './local-call';

describe('local call controls', () => {
  it('shares the current chat session and recent context with the voice call', async () => {
    vi.mocked(apiFetch).mockResolvedValue(new Response(JSON.stringify({ active: true })));
    await localCallRequest('start', null, false, { session: 'chat-123', history: [{ role: 'user', content: 'Pesquise produtos' }], model: 'qwen3.5:4b' });
    expect(apiFetch).toHaveBeenLastCalledWith('/v1/local-call/start', expect.objectContaining({
      body: JSON.stringify({ session: 'chat-123', history: [{ role: 'user', content: 'Pesquise produtos' }], model: 'qwen3.5:4b' }),
    }));
  });
  it('sends the call identity and a keepalive request on close', async () => {
    vi.mocked(apiFetch).mockResolvedValue(new Response(JSON.stringify({ active: false })));
    await localCallRequest('stop', 'call-123', true);
    expect(apiFetch).toHaveBeenLastCalledWith('/v1/local-call/stop', expect.objectContaining({
      method: 'POST', body: '{"call_id":"call-123"}', keepalive: true,
    }));
  });
  it('refreshes the lease of the active call when polling', async () => {
    vi.mocked(apiFetch).mockResolvedValue(new Response(JSON.stringify({ active: true })));
    await localCallRequest('status', 'call-123');
    expect(apiFetch).toHaveBeenLastCalledWith('/v1/local-call/status?call_id=call-123', {});
  });
  it('shows a restart instruction when an old server has no call endpoint', async () => {
    vi.mocked(apiFetch).mockResolvedValue(new Response('', { status: 404 }));
    await expect(localCallRequest('start')).rejects.toThrow('Reabra a interface');
  });
  it('preserves readable microphone errors from the local server', async () => {
    vi.mocked(apiFetch).mockResolvedValue(new Response(JSON.stringify({ detail: 'Permita o microfone.' }), { status: 503 }));
    await expect(localCallRequest('start')).rejects.toThrow('Permita o microfone.');
  });
  it('labels the states in Portuguese', () => {
    expect(callStatusLabel('listening')).toBe('Ouvindo você');
    expect(callStatusLabel('speaking')).toBe('Respondendo');
  });
});
