import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const fetchMock = vi.fn<typeof fetch>();
beforeEach(() => {
  vi.resetModules();
  vi.stubEnv('VITE_API_URL', '');
  vi.stubEnv('VITE_LOCAL_API_MANAGED', '');
  globalThis.fetch = fetchMock;
  fetchMock.mockReset();
  const settings = JSON.stringify({ apiUrl: 'http://localhost:8000' });
  vi.stubGlobal('localStorage', { getItem: () => settings });
});
afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

describe('local model connection', () => {
  it('selects a local GPT OSS model without issuing a preload', async () => {
    vi.stubEnv('VITE_LOCAL_API_MANAGED', 'true');
    fetchMock.mockResolvedValue(new Response('{}', { status: 200 }));
    const { selectModel } = await import('./api');
    await selectModel('gpt-oss:20b', 'openjarvis');
    expect(fetchMock).toHaveBeenCalledWith('/v1/models/select', expect.objectContaining({ body: JSON.stringify({ model: 'gpt-oss:20b' }) }));
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
  it('uses the launcher proxy instead of a stale persisted loopback port', async () => {
    vi.stubEnv('VITE_LOCAL_API_MANAGED', 'true');
    const { getBase } = await import('./api');
    expect(getBase()).toBe('');
  });
  it('preserves an explicitly configured remote server', async () => {
    vi.stubEnv('VITE_LOCAL_API_MANAGED', 'true');
    vi.stubGlobal('localStorage', { getItem: () => JSON.stringify({ apiUrl: 'https://jarvis.example.org' }) });
    const { getBase } = await import('./api');
    expect(getBase()).toBe('https://jarvis.example.org');
  });
  it('preserves custom local server configuration outside the launcher', async () => {
    const { getBase } = await import('./api');
    expect(getBase()).toBe('http://localhost:8000');
  });
  it('preloads through the authenticated API instead of direct Ollama fetch', async () => {
    vi.stubEnv('VITE_LOCAL_API_MANAGED', 'true');
    vi.stubGlobal('localStorage', { getItem: () => JSON.stringify({ apiKey: 'test-key' }) });
    fetchMock.mockResolvedValue(new Response('{}', { status: 200 }));
    const { preloadModel } = await import('./api');
    await preloadModel('qwen3.5:4b');
    expect(fetchMock).toHaveBeenCalledWith('/v1/models/preload', expect.objectContaining({
      method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer test-key' },
      body: JSON.stringify({ model: 'qwen3.5:4b' }),
    }));
  });
});
