# Índice de evidências

Data:2026-10-08. Paths relativos à raiz OpenJarvis; linhas da árvore de trabalho auditada. Intervalos múltiplos delimitam símbolos/fatias, não implicam execução de todas as linhas. Dependências descrevem a implementação, não pacotes instalados. As evidências são âncoras de leitura; cada relatório explicita CONFIRMADO, INFERIDO, NÃO ENCONTRADO ou NÃO VERIFICADO. Nenhum conteúdo de contas/cofre foi copiado.

## E01 — Manifesto Python e CLI

- `pyproject.toml` — **project/dependencies/optional-dependencies/project.scripts**, linhas **5–115,203–205**.

Dependências/alcance: Click/HTTPX/FastAPI/Uvicorn, extras opcionais; declara requisitos, não instalação.

## E02 — Manifesto Rust

- `rust/Cargo.toml` — **workspace/members/dependencies**, linhas **1–56**.

Dependências/alcance: 17 crates, Rust/Tokio/Reqwest/Serde/Rusqlite/PyO3; implementações fonte.

## E03 — Bootstrap do servidor

- `src/openjarvis/cli/serve.py` — **_serving_engines/serve**, linhas **29–38,145–338,421–426,557–568,705–758**.

Dependências/alcance: Engine registry, setup_security, InstrumentedEngine, MultiEngine, classe do AgentRegistry e create_app.

## E04 — Entrada HTTP e ramificações

- `src/openjarvis/server/routes.py` — **chat_completions/_handle_agent/_handle_agent_stream**, linhas **160–211,279–311,593–640,676–817**.

Dependências/alcance: FastAPI, Message/Role, lock de override, SSE, TaskManager; facts system distintos de histórico Business.

## E05 — Registro/classificação Business

- `src/openjarvis/agents/business.py` — **_ROLES/BusinessAgent.__init__/chat/_validate_decision**, linhas **26–42,241–258,362–488**.
- `src/openjarvis/agents/conversation.py` — **módulo**, linhas **1–4**.

Dependências/alcance: AgentRegistry, InferenceEngine, schemas JSON; conversation é documentação.

## E06 — Estado, workers, controle e journal

- `src/openjarvis/agents/task_runtime.py` — **TaskControl/ControlledEngine/TaskManager.__init__/message/_converse/submit/_record_event/read_events/_work/close**, linhas **27–65,97–205,235–269,285–323,336–428**.

Dependências/alcance: Threads/queue/locks, time/time.monotonic, JSONL whitelist; um backup previous, tarefas em RAM.

## E07 — Ferramentas, planos, especialistas e verificação

- `src/openjarvis/agents/business.py` — **_ExecutionGuard/_GuardedTool/_observations/_tools/_ask/_allow_tool/_run**, linhas **99–137,268–324,506–512,529–668**.

Dependências/alcance: Orchestrator Python, ToolResult/AgentResult, shared engine/bus/policy; recibos não são pós-condição universal.

## E08 — Loop Python e continuação

- `src/openjarvis/agents/orchestrator.py` — **__init__/run/_run_structured/_run_function_calling**, linhas **62–101,171–229,368–413,475–526**.
- `src/openjarvis/agents/_stubs.py` — **_check_continuation/ToolUsingAgent.__init__**, linhas **333–366,462–474**.

Dependências/alcance: Function calling/structured, LoopGuard criado automaticamente pela base; continuações fora de turn count normal.

## E09 — Guard Python, configuração e bridge

- `src/openjarvis/agents/loop_guard.py` — **LoopGuardConfig/LoopGuard.__init__/check_call/_python_check**, linhas **17–22,57–69,71–125**.

Dependências/alcance: SHA256/counters/Rust optional; chave do aviso=reason, motivo idêntico inclui contagem.

## E10 — Exportação e Orchestrator Rust

- `rust/crates/openjarvis-agents/src/lib.rs` — **exports**, linhas **3–23**.
- `rust/crates/openjarvis-python/src/lib.rs` — **openjarvis_rust**, linhas **84–90**.
- `rust/crates/openjarvis-agents/src/orchestrator.rs` — **run**, linhas **76–98**.

Dependências/alcance: PyO3; Orchestrator uma chat sem execução de tools; outros agentes exportados.

## E11 — Loops/guard Rust

- `rust/crates/openjarvis-agents/src/loop_guard.rs` — **new/check**, linhas **17–36,62–69**.
- `rust/crates/openjarvis-agents/src/native_react.rs` — **run**, linhas **118–185**.
- `rust/crates/openjarvis-agents/src/native_openhands.rs` — **run**, linhas **180–278**.
- `rust/crates/openjarvis-agents/src/monitor_operative.rs` — **run**, linhas **319–407**.

Dependências/alcance: Loops limitados/max_turns com tool execution e guard; parity com Python não assumida.

## E12 — Transporte e permissões nativas

- `src/openjarvis/tools/mac_desktop.py` — **native/chrome/DesktopSessions.preflight**, linhas **27–89**.

Dependências/alcance: subprocess/open LaunchServices, JSON arquivos privados, AppleScript; helper externo .app.

## E13 — ComputerStep e modelo TEMP

- `src/openjarvis/tools/mac_desktop.py` — **ComputerStepTool.spec/execute/in_window/compact**, linhas **324–402**.

Dependências/alcance: Message/Role, image, schema JSON, lock, DesktopSessions; is_local=True, timeout180, confirmação defaultFalse.

## E14 — Chrome lease/observação/navegação/apps

- `src/openjarvis/tools/mac_desktop.py` — **request/grant/_acquire/ensure/check_screen/chrome_view/chrome_action/release/app_observe/app_act/act**, linhas **102–316**.

Dependências/alcance: AppleScript ID/PID/bounds; AX/screens helper; guarda título/geometria; SSRF e URLpolls.

## E15 — Implementação física Objective-C

- `scripts/local/mac-control/control.m` — **walk/captura/teclado/mouse/main**, linhas **6–8,17–93,110–170**.

Dependências/alcance: AppKit/CoreGraphics/ApplicationServices/ImageIO, screencapture, AXFocusedWindow, JSON RPC; posted_not_confirmed.

## E16 — Correlação de fonte instalada

- `scripts/local/mac-control/control.m` — **arquivo completo**, linhas **1–170**.

Dependências/alcance: Comparado por SHA256 à fonte /Users/JP/OpenJarvis-local/mac-control/control.m; igualdade de fonte não prova binário instalado.

## E17 — Navegador alternativo

- `src/openjarvis/tools/browser.py` — **_BrowserSession._ensure_browser/BrowserNavigateTool.execute/BrowserClickTool.execute/BrowserTypeTool/BrowserExtractTool**, linhas **23–44,129–157,239–368,400–565**.

Dependências/alcance: Playwright Chromium/page DOM, seletores/texto e perfil próprio. Intervalos abrangem implementação e podem ser refinados por símbolo.

## E18 — Obsidian efetivo

- `src/openjarvis/agents/obsidian_memory.py` — **ObsidianGraph._lock/_write/_read/_files/remember/notes/forget/recall**, linhas **17–121,123–204**.
- `src/openjarvis/agents/business.py` — **BusinessGraph/_extract**, linhas **232–238,326–340**.

Dependências/alcance: Path/fcntl/tempfile/Markdown/frontmatter, hash citação, links temas, recuperação lexical.

## E19 — SQLite/grafo alternativo

- `src/openjarvis/agents/business.py` — **SQLiteBusinessGraph/recall**, linhas **140–229**.
- `src/openjarvis/tools/storage/knowledge_graph.py` — **KnowledgeGraphMemory/schema/search**, linhas **48–93,119–140**.

Dependências/alcance: SQLite entidades/relações/LIKE; grafo não é embedding.

## E20 — Facts e extração opcionais

- `src/openjarvis/memory/store.py` — **LocalFactStore/load_configured_facts**, linhas **217–390,423–443**.
- `src/openjarvis/memory/service.py` — **build_memory_service**, linhas **257–294**.

Dependências/alcance: FactStore/Trust/EventBus; ativação por configuração não consultada.

## E21 — Memória vetorial

- `src/openjarvis/tools/storage/faiss_backend.py` — **FAISSMemory.__init__/retrieve**, linhas **29–51,86–114**.

Dependências/alcance: Embeddings e FAISS IndexFlatIP; não chamado por recall Obsidian.

## E22 — Skills e descoberta

- `src/openjarvis/skills/manager.py` — **discover_from_traces/_serialize_discovered_skill**, linhas **272–317,339–360**.
- `src/openjarvis/learning/agents/skill_discovery.py` — **analyze_traces**, linhas **47–104**.
- `src/openjarvis/cli/skill_cmd.py` — **discover**, linhas **650–685**.

Dependências/alcance: TraceStore/subsequências2–4/outcome, SkillManager grava TOML; arguments_template vazio.

## E23 — Recipes/learning/checkpoints

- `src/openjarvis/recipes/loader.py` — **Recipe/carregamento**, linhas **32–65,161–335**.
- `src/openjarvis/learning/learning_orchestrator.py` — **init/_maybe_optimize_skills**, linhas **101–122,223–253**.
- `src/openjarvis/learning/spec_search/checkpoint/store.py` — **checkpoint de configuração**, linhas **1–31**.

Dependências/alcance: TOML agentes/recipes, otimização condicional e Git rollback config; não checkpoint de janela.

## E24 — Traces gerais

- `src/openjarvis/traces/collector.py` — **TraceCollector.run/captura tool payloads**, linhas **22–24,50–103,160–204**.
- `src/openjarvis/server/app.py` — **create_app TraceStore**, linhas **420–448**.

Dependências/alcance: TraceStore SQLite/EventBus; query/result/arguments podem estar presentes; configuração opcional.

## E25 — Ollama Python

- `src/openjarvis/engine/ollama.py` — **_ollama_request_options/generate/stream/stream_full/_run_stream/list_models**, linhas **38–104,118–241,276–306,357–435,527–560**.

Dependências/alcance: HTTPX async pooling, options/think/keep_alive5m nas3payloads, schema/tool retry e tokens.

## E26 — API/painel de tarefas

- `src/openjarvis/server/business_tasks.py` — **create_business_task_router/status/eventos**, linhas **25–52**.
- `frontend/src/components/Chat/BusinessTasksPanel.tsx` — **TaskTrace**, linhas **1–77**.

Dependências/alcance: FastAPI localclient, TaskManager snapshot/read_events, React error_code labels; window_changed agrega mensagens.

## E27 — Escolha UI e voz

- `frontend/src/components/Chat/InputArea.tsx` — **seleção/chat**, linhas **118–130,379–381**.
- `frontend/src/components/Chat/LocalCallPanel.tsx` — **início da chamada**, linhas **69–79**.
- `src/openjarvis/server/local_call.py` — **LocalCall.start/router**, linhas **47–75,161–167**.
- `scripts/local/chamada_continua.py` — **engine/modelo/STT/histórico**, linhas **28–60,272–302,352–354**.

Dependências/alcance: UI selectedModel, OJ_CALL_MODEL, subprocess/watchers, STT CPU/int8; chamada captura escolha.

## E28 — Outro caminho de sistema

- `src/openjarvis/system/core.py` — **JarvisSystem.ask**, linhas **138–161**.
- `src/openjarvis/system/orchestrator.py` — **ask/_detect_agent_intent/_run_agent**, linhas **67–112,240–254**.
- `src/openjarvis/system/builder.py` — **skills/learning**, linhas **230–260,648–671**.

Dependências/alcance: QueryOrchestrator/builder, regex morning_digest e wiring skills/learning em outros caminhos.

## E29 — Engines/routing e paridade

- `src/openjarvis/engine/__init__.py` — **registro**, linhas **8–27**.
- `src/openjarvis/engine/openai_compat_engines.py` — **_ENGINES**, linhas **8–34**.
- `src/openjarvis/engine/multi.py` — **_refresh_map/_engine_for**, linhas **32–74**.
- `src/openjarvis/engine/_openai_compat.py` — **generate/stream/payload**, linhas **40–108,183–203,247–257**.
- `src/openjarvis/engine/cloud.py` — **_client_for_model**, linhas **2013–2043**.
- `rust/crates/openjarvis-engine/src/engine_enum.rs` — **engine variants**, linhas **14–39**.
- `rust/crates/openjarvis-engine/src/ollama.rs` — **generate/stream**, linhas **47–72,147–165**.
- `rust/crates/openjarvis-engine/src/llamacpp.rs` — **completion**, linhas **66–75,91–109,163–187**.

Dependências/alcance: HTTP engines/cloud/Rust; backend availability e parâmetros variam.

## E30 — Telemetria/cache e frontend

- `src/openjarvis/telemetry/instrumented_engine.py` — **uso de tokens avaliados**, linhas **134–226**.
- `frontend/package.json` — **scripts/dependencies**, linhas **1–65**.
- `src/openjarvis/server/model_residency.py` — **select_without_loading/preload_and_select/select_business_model**, linhas **10–46**.

Dependências/alcance: EventBus/meters, Vitest/Vite; seleção sem carregar, preload explícito5m; caches owned bybackend.

## E31 — Scripts locais/boot instalado

- `scripts/local/install_runtime.py` — **main/check/instalação**, linhas **49–95**.
- `scripts/local/preparar_modelos.py` — **script inventário inicial**, linhas **1–30**.
- `scripts/local/README.md` — **procedimentos de runtime**, linhas **1–32**.

Dependências/alcance: Subprocessos/backup/codesign/venv; não executados. Fonte externa runtime.sh1–41/abrir_interface.py111–155 lida sem credentials.

## E32 — Executor genérico

- `src/openjarvis/tools/_stubs.py` — **ToolSpec/ToolExecutor.execute**, linhas **120–131,251–302,305–417,426–469,473–546**.

Dependências/alcance: Capabilities/boundary/taint/injection/rate limit/confirmation/runner bounded/timeouts; Future.cancel não mata execução iniciada.

## E33 — Piso de segurança e wrappers

- `src/openjarvis/agents/business.py` — **_GuardedTool**, linhas **110–137**.
- `src/openjarvis/tools/mac_desktop.py` — **ComputerStepTool.spec**, linhas **324–333**.
- `src/openjarvis/tools/spreadsheet_local.py` — **SpreadsheetCreateTool.spec**, linhas **11–17**.
- `src/openjarvis/security/capabilities.py` — **canonical_tool_capabilities**, linhas **294–334**.

Dependências/alcance: Nome+provenance builtin, spec capabilities e wrapper não builtin; lacuna F01.

## E34 — Wiring/guards/autenticação

- `src/openjarvis/security/runtime.py` — **agent_security_kwargs/wire_agent_security**, linhas **23–132**.
- `src/openjarvis/security/__init__.py` — **setup_security**, linhas **43–62**.
- `src/openjarvis/security/guardrails.py` — **stream**, linhas **235–261**.
- `src/openjarvis/server/app.py` — **middleware/auth/CORS**, linhas **526–555**.
- `src/openjarvis/cli/serve.py` — **bind safety**, linhas **705–707**.

Dependências/alcance: Guardrails/callbacks/auth opcional e loopback; scanner output só non-local em E32; failopen setup possível.

## E35 — Testes e avaliações

- `tests/local/test_task_diagnostics.py` — **TraceTests/TraceCorruptionTests**, linhas **54–120**.
- `tests/local/test_mac_desktop_runtime.py` — **TempTests/PermissionTests/SpreadsheetTests**, linhas **54–170**.
- `tests/local/test_desktop_permissions.py` — **DesktopPermissionTests**, linhas **6–80**.
- `src/openjarvis/evals/core/agentic_runner.py` — **AgenticRunner/run/artefatos**, linhas **103–159,315–394,855–899**.
- `src/openjarvis/evals/skill_benchmark.py` — **SkillBenchmarkRunner/run_condition/run_all_conditions/write_report**, linhas **92–175,302–394**.
- `src/openjarvis/evals/scorers/browser_assistant.py` — **BrowserAssistantScorer.score**, linhas **89–150**.

Dependências/alcance: unittest mocks/pytest/Vitest, avaliações+scorers; existência não PASS operacional nem coveragepercent.

## Evidência operacional sanitizada do incidente

Fonte fora do repositório: `/Users/JP/OpenJarvis-local/logs/task-events.jsonl`, task_id com prefixo `d851`. Leitura pelo revisor B somente de eventos estruturais: intervalo102,0s;12 computer_step;11 window_changed; primeiro erro8,526s pós-click; dez falhas seguintes2,447–2,543s antesTEMP. O registro não fornece correlação inequívoca com pedido/domínio/menu. Nenhum log bruto anexado.

## Integridade e escopo

Baseline em `/tmp/openjarvis-audit-baseline.json`: SHA-256 de2122 arquivos de produto/testes existentes, docs excluídos. Comparação final no README. O conjunto inclui arquivos modificados/não rastreados anteriores à auditoria; não se confunde com HEAD. Fontes externas inspecionadas foram scripts/nativo e campos whitelisted de eventos; não configuração de credenciais ou cofre.

## Âncoras complementares de arquivo/timeout

- `src/openjarvis/engine/_http_async.py` — `AsyncHTTPEngineMixin._make_async_client/_get_async_client`, linhas68–85: HTTPX pool por event loop.
- `src/openjarvis/tools/file_read.py` — `_is_path_allowed/execute`, linhas50–98: resolve caminho, pasta permitida, política de arquivo sensível e tamanho.
- `src/openjarvis/tools/file_write.py` — `spec/_is_path_allowed/execute`, linhas62–116: capability file:write, raiz resolvida e checagens antes da escrita.
- `src/openjarvis/tools/spreadsheet_local.py` — `execute`, linhas19–65: nome sem diretório, limites de colunas/linhas, valores literais, preserva arquivo existente; OOXML ZIP não exige Excel para produzir arquivo.
- `/Users/JP/OpenJarvis-local/abrir_interface.py` — inicialização, linhas111–155: identidade/fingerprint da instância, Popen Python serve pinned ollama/business e npm Vite; metadados em interface.json. Leitura de script, não confirmação de processos.
- `/Users/JP/OpenJarvis-local/runtime.sh` — variáveis e oj_start_ollama, linhas1–41: defaults/exportação e startup sob demanda do servidor Ollama, não dos pesos.

## Localização precisa de símbolos Python centrais (extração AST, sem importar)

Os intervalos abaixo complementam as fatias temáticas anteriores, incluindo o final real de cada método. Extração somente de fonte; nenhum módulo do produto executado.

- `src/openjarvis/agents/business.py` — `_BrowserTool.__init__`:71–74; `_BrowserTool.execute`:80–81; `_ExecutionGuard.__init__`:89–94; `_ExecutionGuard.generate`:99–106; `_GuardedTool.__init__`:110–112; `_GuardedTool.execute`:118–137; `SQLiteBusinessGraph.__init__`:148–149; `BusinessAgent.__init__`:248–260; `BusinessAgent._observations`:268–277; `BusinessAgent._tools`:279–315; `BusinessAgent._ask`:317–324; `BusinessAgent._extract`:326–340; `BusinessAgent.run`:350–360; `BusinessAgent.chat`:362–461; `BusinessAgent._run`:514–668.
- `src/openjarvis/agents/task_runtime.py` — `TaskControl.__init__`:28–31; `ControlledEngine.__init__`:48–49; `ControlledEngine.generate`:54–65; `TaskManager.__init__`:98–114; `TaskManager.message`:116–143; `TaskManager._converse`:145–213; `TaskManager.submit`:219–271; `TaskManager._record_event`:285–300; `TaskManager.read_events`:302–320; `TaskManager._work`:336–417.
- `src/openjarvis/agents/orchestrator.py` — `OrchestratorAgent.__init__`:52–91; `OrchestratorAgent.run`:93–101; `OrchestratorAgent._run_structured`:148–229; `OrchestratorAgent._run_function_calling`:345–541.
- `src/openjarvis/tools/mac_desktop.py` — `DesktopPermissionError.__init__`:19–24; `DesktopSessions.__init__`:74–78; `DesktopSessions.preflight`:80–89; `DesktopSessions._acquire`:117–155; `DesktopSessions.ensure`:157–169; `DesktopSessions.chrome_view`:181–204; `DesktopSessions.chrome_action`:206–210; `DesktopSessions.app_observe`:220–248; `DesktopSessions.app_act`:250–260; `DesktopSessions.observe`:262–270; `DesktopSessions.act`:272–321; `ComputerStepTool.__init__`:328–329; `ComputerStepTool.execute`:335–390.
- `src/openjarvis/tools/browser.py` — `_BrowserSession.__init__`:18–21; `_BrowserSession._ensure_browser`:23–44; `BrowserNavigateTool.execute`:103–157; `BrowserClickTool.execute`:239–289; `BrowserTypeTool.execute`:440–485; `BrowserScreenshotTool.execute`:526–565; `BrowserExtractTool.execute`:609–699.
- `src/openjarvis/engine/ollama.py` — `OllamaEngine.__init__`:118–139; `OllamaEngine.generate`:141–274; `OllamaEngine.stream`:276–355; `OllamaEngine.stream_full`:357–408.
