# 01 — Arquitetura atual

Data: 2026-10-08. Escopo: árvore de trabalho atual, incluindo alterações preexistentes e arquivos ainda não rastreados. Auditoria de leitura; não corresponde apenas ao HEAD. As referências E01–E35 são detalhadas no [índice de evidências](EVIDENCIAS.md), com símbolos, linhas e dependências. CONFIRMADO significa implementação comprovada; estado do processo atual exige evidência separada.

## Mapa do repositório

```text
frontend/                 React + TypeScript, Vite, estado/UI, cliente HTTP/SSE, Vitest
src/openjarvis/
  cli/                    jarvis serve, skills, configuração e comandos
  server/                 FastAPI, rotas compatíveis com OpenAI, tarefas, voz, modelos
  agents/                 Business, Orchestrator, ReAct e outros agentes/guards
  engine/                 Ollama, HTTP compatibles, cloud, multiplexação
  tools/                  ferramentas, executor, navegador, desktop, arquivos, armazenamento
  system/                 builder e QueryOrchestrator: outro caminho de execução
  memory/                 FactStore, extração e serviço opcional
  traces/ telemetry/      traces SQLite, eventos, métricas de inferência/energia
  skills/ recipes/        skills e composição configurável de agentes
  learning/               descoberta/otimização/treinamento/spec-search
  security/               capabilities, boundary, injection, SSRF, confirmação
  evals/                  runners, datasets, scorers, configs e benchmarks
  channels/ connectors/   integrações opcionais, mensageria e fontes
  workflow/               composição de workflows
rust/crates/              17 crates, motores/agentes/ferramentas e bridge PyO3
scripts/local/            instalação/validação local, voz e fonte Objective-C do helper
 tests/                   testes Python e testes nativos locais
 docs/anotations/         memória documental da colaboração
```

**CONFIRMADO — stack:** Python >=3.10,<3.14; Click para CLI, HTTPX para backends HTTP; FastAPI/Uvicorn/Pydantic nos extras server/desktop. Voz usa sounddevice/numpy, faster-whisper e Kokoro opcionais. Frontend usa React/TypeScript/Vite e Vitest. Rust usa Tokio/Reqwest/Serde/Rusqlite/PyO3 e MSRV 1.88. Dependência declarada não prova instalação ou utilização local. E01, E02, E30.

## Entradas, serviços e comunicação

**CONFIRMADO:** `jarvis` aponta para `openjarvis.cli:main`; `openjarvis-eval` para CLI de avaliações. `serve` seleciona engine, registra/instancia classe de agente e chama `create_app`. `BusinessAgent` é registrado como `business`; `create_app` cria seu TaskManager apenas quando essa classe está selecionada. E01, E03–E05.

**CONFIRMADO pela configuração externa lida:** `/Users/JP/OpenJarvis-local/runtime.sh:1–41` define Ollama em loopback:11434, principal9b/TEMP4b, contexto8192, máximo2 modelos/1 inferência paralela e desktop ativo. `oj_start_ollama` primeiro verifica `/api/tags` e só inicia `ollama serve` se indisponível. Isso não confirma qual ambiente um processo já aberto herdou. Não foram lidos arquivos de credenciais. O launcher local é externo ao repositório; scripts de instalação são E31. **NÃO VERIFICADO:** processos, portas e binários carregados neste instante.

**CONFIRMADO — processos previstos pelo código:** servidor Python/FastAPI e frontend Vite no launcher local; Ollama é servidor independente. A chamada de voz inicia subprocesso shell/script e threads de watcher/lease (`local_call.py:47–75`). Controle físico usa helper `.app` via LaunchServices e RPC em arquivos privados (`mac_desktop.native:27–60`). Modelos se comunicam por HTTP; frontend usa HTTP/SSE e consulta tarefas por API. Não há evidência de uma extensão obrigatória instalada dentro do Chrome. E04, E12, E27, E31.

**CONFIRMADO — workers:** decisões conversacionais e execução pesada têm workers distintos no TaskManager. Especialistas são sequenciais; controle desktop tem lock de processo. O executor genérico possui runner de ferramentas limitado e timeouts cooperativos. E06–E09, E32. Isto serializa algumas operações locais; não isola o desktop do usuário nem de outro processo.

## Fluxos existentes e diferenças relevantes

1. **Business streaming:** frontend → `/v1/chat/completions` → conversa principal decide → ack SSE → mailbox executa tarefa → painel consulta estado/eventos. O SSE inicial não aguarda a tarefa inteira. E04–E07.
2. **Business não streaming:** rota chama `agent.run` sob override de modelo; delegação é síncrona. Não reproduz integralmente redirect/cancel do mailbox. E04, E07.
3. **Ferramentas explicitamente enviadas pelo cliente:** ramo próprio da rota compatível com OpenAI. Não atribuir a ele automaticamente todas as garantias Business. E04.
4. **`JarvisSystem.ask → QueryOrchestrator.ask`:** builder/orquestrador genérico, com roteamento próprio; inclui regex de morning_digest. O protocolo Business decide pela IA, mas o projeto inteiro não é livre de heurísticas. E28.
5. **Rust:** agentes exportados via PyO3 são acessíveis. Business importa Orchestrator Python; seu LoopGuard pode usar bridge Rust. Orchestrator Rust faz uma única chamada, sem despacho multiturno de ferramentas. Outros agentes Rust possuem loops reais. E10–E11.

## Persistência, configuração e maturidade

**CONFIRMADO:** BusinessGraph escolhe Markdown Obsidian por padrão ou SQLite para sufixo explícito `.db/.sqlite/.sqlite3`; arquivos de trabalho têm raiz local separada; JSONL guarda eventos estruturais; TaskManager guarda fila/estado em RAM. Plataforma oferece SQLite TraceStore/KnowledgeGraph, FactStore e FAISS opcionais. TOML/config/env selecionam funcionalidades; disponibilidade não prova wiring no caminho Business. E06, E18–E24.

**Duplicações confirmadas:** Python/Rust possuem implementações de engines/agentes com contratos diferentes; navegador Playwright e controle Chrome nativo usam sessões distintas; journal Business e TraceStore são mecanismos diferentes. **Implementação parcial confirmada:** Orchestrator Rust não tem loop de despacho. **Legado identificável:** backend SQLiteBusinessGraph permanece acessível explicitamente; não é código morto. `conversation.py` atual é documentação, não executor. **NÃO ENCONTRADO com prova suficiente:** componentes definitivamente abandonados ou dependências comprovadamente não utilizadas em todos os caminhos. Não remover nada por esta auditoria.

Pontos fundamentais para extensão: registros engine/agente/ferramenta, `ToolSpec/ToolExecutor`, `ComputerStepTool/DesktopSessions`, eventos/TraceStore, SkillManager/recipes e runners de avaliação. O objetivo futuro generalista contrasta com a lista atual de aplicativos/ferramentas permitidos no Business; nenhuma evolução foi implementada nesta etapa.
