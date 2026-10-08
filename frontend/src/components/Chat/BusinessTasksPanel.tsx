import { useEffect, useState } from 'react';
import { apiFetch } from '../../lib/api';

interface TaskEvent { sequence: number; revision: number; timestamp: number; kind: string; stage: string; status?: string; duration_ms?: number; model?: string; tool?: string; tokens?: number; error_code?: string }
interface Dialogue { id: string; state: string; stage?: string; elapsed_seconds?: number; model?: string }
interface Task { id: string; session: string; query: string; state: string; stage: string; result: string; error: string; error_details?: string; model?: string; elapsed_seconds?: number; stage_seconds?: number; failure_stage?: string; events?: TaskEvent[]; trace_error?: boolean }

export function TaskTrace({ task }: { task: Task }) {
  return <>
    <p className="mt-1">Modelo: {task.model || 'padrão'} · {task.elapsed_seconds ?? 0}s no total{['running', 'queued', 'redirecting'].includes(task.state) ? ` · ${task.stage_seconds ?? 0}s nesta etapa` : ''}</p>
    {task.failure_stage && <p className="mt-1">Falhou durante: <strong>{task.failure_stage}</strong></p>}
    {task.trace_error && <p role="alert">Não consegui salvar o log em disco; as etapas desta sessão continuam abaixo.</p>}
    {Boolean(task.events?.length) && <details className="mt-2" open={['running', 'error'].includes(task.state)}>
      <summary className="cursor-pointer">Etapas e tempos de execução</summary>
      <ol className="mt-2 space-y-1">
        {task.events?.map(event => <li key={event.sequence}>
          {new Date(event.timestamp * 1000).toLocaleTimeString('pt-BR')} · {event.stage}
          {event.model && ` · ${event.model}`}{event.tool && ` · ${event.tool}`}
          {event.status && ` · ${{ started: 'iniciou', done: 'terminou', error: 'falhou', cancelled: 'cancelou' }[event.status] ?? event.status}`}
          {event.duration_ms != null && ` · ${(event.duration_ms / 1000).toFixed(1)}s`}
          {event.error_code && ` · ${{ window_changed: 'Janela mudou durante a etapa', executor_invalid_action: 'Ação inválida do executor', desktop_step_failed: 'Falha no controle do computador', accessibility_denied: 'Acessibilidade indisponível', screen_recording_denied: 'Captura de tela indisponível' }[event.error_code] ?? event.error_code}`}
          {event.tokens != null && ` · ${event.tokens} tokens`}
        </li>)}
      </ol>
    </details>}
  </>;
}

export function BusinessTasksPanel() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [error, setError] = useState('');
  const [dialogues, setDialogues] = useState<Dialogue[]>([]);
  useEffect(() => {
    let alive = true;
    let checking = false;
    const check = async () => {
      if (checking) return;
      checking = true;
      try {
        const response = await apiFetch('/v1/business-tasks/status');
        if (response.status === 503 || response.status === 404) return;
        if (!response.ok) throw new Error('Não consegui atualizar as tarefas.');
        const data = await response.json();
        if (alive) { setTasks(data.tasks); setDialogues(data.messages || []); setError(''); }
      } catch (err) { if (alive) setError(err instanceof Error ? err.message : 'Servidor indisponível.'); }
      finally { checking = false; }
    };
    void check();
    const timer = setInterval(() => void check(), 1000);
    return () => { alive = false; clearInterval(timer); };
  }, []);
  const visible = [...tasks.filter(t => ['queued', 'running', 'redirecting'].includes(t.state)), ...tasks.filter(t => ['done', 'error', 'cancelled'].includes(t.state)).slice(-5)];
  const pending = dialogues.filter(d => d.state === 'pending');
  if (!visible.length && !pending.length && !error) return null;
  return <section aria-label="Tarefas em segundo plano" className="mb-3 rounded-xl p-3" style={{ background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}>
    <p className="text-sm font-medium mb-2" style={{ color: 'var(--color-text)' }}>Tarefas em segundo plano</p>
    {pending.map(dialogue => <p key={dialogue.id} role="status" className="text-xs mb-2">{dialogue.stage || 'IA avaliando pedido'} · {dialogue.model || 'padrão'} · {dialogue.elapsed_seconds ?? 0}s</p>)}
    {error && <p role="alert" className="text-xs" style={{ color: 'var(--color-error)' }}>{error}</p>}
    <div className="max-h-48 overflow-y-auto space-y-2">
      {visible.map(task => <details key={task.id} open={['queued', 'running', 'redirecting', 'error'].includes(task.state)} className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
        <summary className="cursor-pointer"><strong>{task.stage}</strong> — {task.query.slice(0, 160)}</summary>
        <TaskTrace task={task} />
        {task.result && <p className="mt-2 whitespace-pre-wrap">{task.result}</p>}
        {task.error && <p className="mt-2" style={{ color: 'var(--color-error)' }}>{task.error}</p>}
        {task.error_details && task.error_details !== task.error && <details className="mt-2">
          <summary className="cursor-pointer">Detalhes do problema</summary>
          <p className="mt-2 whitespace-pre-wrap">{task.error_details}</p>
        </details>}
        {['queued', 'running', 'redirecting'].includes(task.state) && <button type="button" className="mt-2 cursor-pointer underline" onClick={() => {
          void apiFetch('/v1/business-tasks/cancel', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ task_id: task.id, session: task.session }) })
            .then(response => { if (!response.ok) throw new Error('Não consegui cancelar a tarefa.'); })
            .catch(err => setError(err instanceof Error ? err.message : 'Não consegui cancelar a tarefa.'));
        }}>Cancelar tarefa</button>}
      </details>)}
    </div>
  </section>;
}
