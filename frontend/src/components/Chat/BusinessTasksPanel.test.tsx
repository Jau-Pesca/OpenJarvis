import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { TaskTrace } from './BusinessTasksPanel';

describe('Task execution diagnostics', () => {
  it('shows failed phase, model, elapsed time and measured tool duration', () => {
    const html = renderToStaticMarkup(<TaskTrace task={{ id: 'test', session: 'test', query: 'test', state: 'error', stage: 'Não foi possível concluir', result: '', error: 'Falhou', model: 'qwen3.5:4b', elapsed_seconds: 12, failure_stage: 'Localizando janela e observando tela', events: [{ sequence: 1, revision: 1, timestamp: 1, kind: 'tool', stage: 'Ferramenta terminou', tool: 'computer_step', status: 'error', duration_ms: 2400 }] }} />);
    expect(html).toContain('Localizando janela e observando tela');
    expect(html).toContain('qwen3.5:4b');
    expect(html).toContain('12s no total');
    expect(html).toContain('computer_step');
    expect(html).toContain('2.4s');
    expect(html).toContain('falhou');
  });
});
