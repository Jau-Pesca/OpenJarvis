# 07 — Testes, observabilidade e reprodução

Data:2026-10-08. Evidências E06,E24,E26,E30,E32–E35 em [EVIDENCIAS.md](EVIDENCIAS.md). Nenhuma suíte de produto, inferência, GUI, download, instalação ou restart foi executado nesta auditoria. Executados somente buscas/leitura, hashes e validações documentais. Resultados anteriores em docs/anotations/validation.md são históricos, não reexecução atual.

## Três mecanismos diferentes

| Mecanismo | O que registra | O que não prova |
|---|---|---|
| TaskControl/TaskManager + JSONL | task_id/revision/sequence/timestamp; etapas, begin/end/fail; modelo/ferramenta; duração/tokens/códigoerro | Prompt, argumentos, screenshot, decisão semântica e pós-condição de negócio |
| EventBus/TraceCollector/TraceStore | query/result e etapas, chamadas/argumentos/resultados conforme collector; persistência SQLite configurável | Mesmo wiring em mailbox SSE; sanitização uniforme; reprodução determinística |
| InstrumentedEngine/telemetry | geração, tokens avaliados, duração/custo; energia quando sensor disponível | ZeroW/custo UI não demonstra ausência de inferência; cache física/RAM correta |

Journal: whitelist,<=200 eventos por tarefa, arquivo com rotação após ultrapassar5MiB e um backup `.previous.jsonl` (dois arquivos no total); falhas de IO tratadas, JSON inválido ignorado, erro de leitura controlado pela API. Fila/decisões/tarefas são RAM; `read_events` não restaura execução. `TaskTrace` UI apresenta etapa/falha/duração/error code. O mesmo rótulo window_changed agrega motivos distintos. E06,E26.

**CONFIRMADO:** TraceCollector e journal Business têm payloads e caminhos distintos. `_handle_agent` pode usar coletor; mailbox `_handle_agent_stream` executa tarefas fora desse wrapper. Sem configurar/provar coleta por esse worker, não declarar TraceStore completo para cada chamada de voz. Executor publica tool events; event bus pode ser consumido por outros mecanismos, mas existência não prova cobertura fim a fim. E04,E24,E32.

**NÃO ENCONTRADO no journal:** replay da execução original ou justificativa exata da escolha IA. Dá para reconstituir cronologia parcial, não interface/argumentos/contexto. Resposta posterior explicando “por que cliquei” é geração nova, não prova da decisão original nem acesso a raciocínio privado. Instrumentação útil é inputs/outputs autorizados, estado, ações/recibos e motivos estruturais, com sanitização.

## Testes existentes examinados

| Área | Arquivos / abordagem | Limite de evidência |
|---|---|---|
| Tasks/diagnóstico | tests/local/test_task_diagnostics.py:54–120, unittest/stubs: journal sem sentinela, cancel, corrupção, falhaIO | Não prova recuperação GUI real nem restauração de fila |
| Desktop | test_mac_desktop_runtime.py, test_desktop_permissions.py: mock native/desktop/engine, contexto fresco/parametros/janela fechada | Sem prova universal de transição título/popup real |
| Modelo/RAM | test_lazy_models.py, test_model_keep_alive.py, test_model_residency.py, test_voice_model_routing.py | Contratos/payloads e stubs; servidor pode evictar |
| Downloads/UI | test_model_download.py; frontend api.models/store.models e BusinessTasksPanel.test.tsx | Não instala modelo nessa leitura |
| Falha terminal | tests/agents/test_business_terminal_failures.py | Erros terminal e bloqueio; não tolerância geral a falha repetível |
| Guard/Orchestrator | test_loop_guard.py,test_loop_guard_warn.py,test_orchestrator.py | Backend/modo/wiring precisam ser distinguidos |
| Segurança | test_capabilities,test_security_wiring,test_security_factory_wiring,test_injection_scanner,test_tool_confirmation | Não encontrada regressão wrapperDesktop/Spreadsheet deny/injection desktop/efeito pós-timeout |
| Traces | tests/traces/test_collector.py,test_store.py,test_types.py | Não é prova de coleta mailbox ativo |
| Nativo | tests/local/native/test_keyboard.m,test_resize.m | Execução toca APIs/macOS; não rodada nesta etapa |

E35 identifica suítes e funções/linhas; inventário estático não significa PASS. Pytest/pytest-cov declarados no extra dev; frontend tem `npm test=vitest run`, build=tsc -b+vite. **NÃO VERIFICADO:** cobertura percentual atual, resultados de toda suíte, stack instalada para cada extra e CI da árvore modificada. Nenhuma dependência foi instalada. Suítes que acessam endpoints, dispositivos, modelos, dados externos ou escrevem ambiente foram deliberadamente evitadas.

## Evals, benchmarks e E2E

**CONFIRMADO:** `AgenticRunner` executa consultas sequenciais/concurrentes, gera QueryTrace, correlaciona energia e grava artifacts; `SkillBenchmarkRunner` compara condições/seeds e escreve relatório. Dataset/scorer browser_assistant e configs de modelos existem. Isso não equivale a benchmark já executado para Central de Vendedores nem medição controlada4Bvs9B no macOS atual. E35. Scripts `scripts/local/validate_flow.py`, validate_desktop/voice/task_execution/model_* exercitam fluxos locais, alguns com GUI/inferência: existentes, não executados na auditoria. Nem rerun de LLM é replay determinístico.

## Reprodução necessária, ainda não realizada

1. Página local fictícia com transição de título, popup e mudança de bounds separadamente; anotar qual guard falha antes/depois da ação.
2. Modelo/desktop stub para repetir window_changed, contar tools/turnos e confirmar falha antesTEMP.
3. Stub efeito pós-timeout e redirect após escrita: distinguir publicação cancelada de efeito executado.
4. Política deny com `_GuardedTool` em teste sem GUI; confirmar F01 e não só builtin direto.
5. Página fictícia com injection; verificar fluxo de conteúdo local/remoto e autorização sem ação sensível real.
6. Fluxo de navegação fictício repetido amanhã/restart, medir se memória/recipe recuperada e se fila persiste.

Dados ausentes do incidente: motivo detalhado do guard, janela/aba/PID/bounds correlacionados, transições e evidência redigida de pós-condição. O journal confirma102s/12calls/11window_changed, não identifica domínio/menu. Não capturar cookies/senhas/screen pessoal para preencher lacuna. Preparar fixtures locais em futura fase autorizada.

## Validação desta entrega

Os cinco papéis A–E foram revisados por quatro subagentes reais, conforme README, com leitura por especialidade; um revisor final confronta documentos e fonte. [README](README.md) registra cobertura do pedido e resultado final. SHA-256 dos2122 arquivos de produto/testes existentes foi armazenado no início e comparado ao final; relatórios/memória documental são as únicas escritas autorizadas. Comandos de produto foram evitados por ser auditoria exclusiva. Resultado final do gate documental está no README, sem atribuir testes históricos a esta rodada.
