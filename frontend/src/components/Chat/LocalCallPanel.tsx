import { useEffect, useRef, useState } from 'react';
import { Phone, PhoneOff } from 'lucide-react';
import { callStatusLabel, localCallRequest, type LocalCallState } from '../../lib/local-call';
import { useTtsStore } from '../../lib/tts';
import { BusinessTasksPanel } from './BusinessTasksPanel';
import { useAppStore } from '../../lib/store';

interface Props { disabled?: boolean; onActiveChange: (active: boolean) => void }

export function LocalCallPanel({ disabled, onActiveChange }: Props) {
  const [call, setCall] = useState<LocalCallState | null>(null);
  const [busy, setBusy] = useState(false);
  const [allowInterruptions, setAllowInterruptions] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const callRef = useRef<LocalCallState | null>(null);
  const mounted = useRef(false);
  const revision = useRef(0);
  const busyRef = useRef(false);
  const transcriptRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    mounted.current = true;
    let checking = false;
    const check = async () => {
      if (checking || busyRef.current) return;
      checking = true;
      const version = revision.current;
      try {
        const state = await localCallRequest('status', callRef.current?.call_id);
        if (mounted.current && version === revision.current) {
          callRef.current = state;
          setCall(state);
          setError(null);
        }
      } catch (err) {
        if (mounted.current && version === revision.current) setError(err instanceof Error ? err.message : 'Servidor indisponível.');
      } finally { checking = false; }
    };
    void check();
    const timer = setInterval(() => void check(), 1000);
    const disconnect = () => {
      const current = callRef.current;
      if (current?.active && current.call_id) void localCallRequest('stop', current.call_id, true).catch(() => {});
    };
    window.addEventListener('pagehide', disconnect);
    return () => {
      mounted.current = false;
      revision.current++;
      clearInterval(timer);
      window.removeEventListener('pagehide', disconnect);
      disconnect();
      useTtsStore.getState().setLocalCallActive(false);
    };
  }, []);

  useEffect(() => {
    const active = Boolean(call?.active || busy);
    useTtsStore.getState().setLocalCallActive(active);
    onActiveChange(active);
  }, [call?.active, busy, onActiveChange]);
  useEffect(() => {
    if (transcriptRef.current) transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight;
  }, [call?.transcript.length]);

  const toggle = async () => {
    if (busyRef.current) return;
    busyRef.current = true;
    revision.current++;
    setBusy(true);
    setError(null);
    try {
      useTtsStore.getState().stop();
      const store = useAppStore.getState();
      const context = callRef.current?.active ? undefined : {
        model: store.selectedModel,
        allow_interruptions: allowInterruptions,
        session: `chat-${store.activeId ?? store.createConversation(store.selectedModel)}`,
        history: store.messages.filter(m => m.role === 'user' || m.role === 'assistant').slice(-12).map(m => ({ role: m.role, content: m.content.slice(0, 1500) })),
      };
      const state = await localCallRequest(callRef.current?.active ? 'stop' : 'start', callRef.current?.call_id, false, context);
      if (!mounted.current) {
        if (state.active) await localCallRequest('stop', state.call_id, true);
        return;
      }
      callRef.current = state;
      setCall(state);
    } catch (err) {
      if (mounted.current) setError(err instanceof Error ? err.message : 'Não consegui iniciar a chamada.');
    } finally {
      busyRef.current = false;
      if (mounted.current) setBusy(false);
    }
  };

  const active = Boolean(call?.active);
  const message = error || call?.error;
  const interruptible = active ? call?.allow_interruptions : allowInterruptions;
  return (<>
    <section aria-label="Conversa por voz" className="mb-3 rounded-xl p-3" style={{ background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}>
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-medium" style={{ color: 'var(--color-text)' }}>Conversa por voz</p>
          <p role="status" aria-live="polite" className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
            {busy ? (active ? 'Encerrando…' : 'Preparando a chamada…') : active ? callStatusLabel(call?.status ?? '') : 'Converse usando o microfone deste Mac.'}
          </p>
          {active && call?.voice && <p className="text-[11px] mt-1" style={{ color: 'var(--color-text-tertiary)' }}>Voz: {call.voice}</p>}
        </div>
        <button type="button" onClick={() => void toggle()} disabled={busy || (!active && (disabled || call?.available === false))}
          className="inline-flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-sm cursor-pointer disabled:opacity-50 disabled:cursor-default"
          style={{ background: active ? 'var(--color-error)' : 'var(--color-accent)', color: 'var(--color-on-accent)' }}>
          {active ? <PhoneOff size={16} /> : <Phone size={16} />}
          {active ? 'Encerrar chamada' : 'Iniciar chamada'}
        </button>
      </div>
      {!active && <label className="flex items-center gap-2 text-xs mt-2" style={{ color: 'var(--color-text-secondary)' }}>
        <input type="checkbox" checked={allowInterruptions} disabled={busy} onChange={e => setAllowInterruptions(e.target.checked)} />
        Estou usando fones: permitir interrupção por voz
      </label>}
      <p className="text-xs mt-2" style={{ color: 'var(--color-text-tertiary)' }}>{interruptible ? 'Com fones, você pode falar durante as respostas.' : 'Modo alto-falante: fale depois da resposta. A captura pausa enquanto o Jarvis fala para evitar eco.'}</p>
      {message && <p role="alert" className="text-xs mt-2" style={{ color: 'var(--color-error)' }}>{message}</p>}
      {active && <p className="text-xs mt-2" style={{ color: 'var(--color-text-tertiary)' }}>Diga “outra tarefa” para um novo pedido ou “complementando” para corrigir o atual. Fones ajudam a evitar eco.</p>}
      {Boolean(call?.transcript.length) && (
        <div ref={transcriptRef} className="max-h-44 overflow-y-auto mt-3 space-y-2" aria-label="Transcrição da chamada">
          {call?.transcript.map((item, index) => <p key={index} className="text-sm" style={{ color: 'var(--color-text-secondary)', whiteSpace: 'pre-wrap' }}>
            <strong>{item.role === 'user' ? 'Você' : 'OpenJarvis'}:</strong> {item.text}
          </p>)}
        </div>
      )}
    </section><BusinessTasksPanel /></>
  );
}
