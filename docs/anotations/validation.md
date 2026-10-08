# Validação

## 2026-10-08 — R-025 auditoria exclusivamente documental: PASS

| Critério | Evidência desta rodada | Resultado |
|---|---|---|
| Oito relatórios, evidências e cobertura18itens | docs/auditoria/2026-10-08/README.md; índice35âncoras e AST | PASS |
| Revisão real A–E+final antes de entregar | Quatro subagentes/cinco papéis; gatefinaltask_failures confirmou fonte/prompt/documentos sem falha material | PASS |
| Resumo08<=1500palavras e exemploJSON válido | Script documental Python3:1039palavras; json.loads; revisorfinal | PASS |
| Links, arquivos e intervalos válidos | Script documental +ASTindependente dofinal | PASS |
| Não alterar código/config/dependências/runtime | SHA-256 baseline2122produto/testes vsfinal:zeroalterações/novosproduto; somente leitura e docs | PASS no workspace |
| Segurança/privacidade de evidências | Nenhum cofre/DB/cookies lido; journal somente camposwhitelisted; incident102s não correlacionado inequivocamente ao domínio/menu | PASS documental |

Não executados testes de produto, GUI, inferência, instalação ou restart. `git diff --check` PASS para alterações rastreadas; documentos não rastreados conferidos por validação própria. Benchmarks, binário/processo atual e subcausa da janela permanecem NÃO VERIFICADOS; não são substituídos por resultados anteriores. DireçõesF01–F15 são riscos documentados, não correções implementadas.

## 2026-10-08 — Aceite final R-022/023/024

- Última execução real MercadoLivre PASS:30,2s desdeenvio,24,7sbackground;5inferênciasbackground,1computer_step semfalha/semrepetição, navigate7,705s; revisão aprovada com summary reutilizado. Tokensbackground9430entrada+229saída=9659 (somatório das requisições, não tokens únicos). Tarefa198bb31861374321bd5561825bd674da; JSONL persistida, UIeventos acessíveis.
- Fonte final57testeslocais+8terminalfailuresPASS; frontend16PASS; buildtsc/vitePASS; gitdiffcheckPASS. Revisores memory_review/task_failures/voice_review aprovaram fatias, correções registradas.
- Instalação: hashes dos dois scripts correspondem à fonte revisada; backup speaker-protection-20261008T121027.620130Z. Servidor/interface reabertos com fonte atual.
- Limitações: hardwareacústico não testado; proteçãoaltofalante demonstrada com playbackstub/VADreset, não AECperfeito. Latência30s é resultado pontual, não SLA nem economia percentual.
- Suíte externa legada test_business.py:19PASS/1errodefixture, caso invalid_plan fornece uma resposta e agora são2tentativas, Enginefakeesgotaiterator. Teste equivalente local cobrecontrato novo; não registrar antiga como20PASS. Arquivo externo de teste não alterado.

## 2026-10-08 — R-022/023/024 diagnósticos e proteção de voz

| Critério | Evidência | Estado |
|---|---|---|
| Planejamento estrito, reparo limitado, nenhuma ferramenta com plano inválido, extração direta preservada | PlanTests em test_task_diagnostics; schema real4b agente task_failures válido3.43s,375entrada/61saída | PASS |
| Inferência bloqueada visível, fase do erro, eventos persistidos sem sentinela secreta, cancelamento ignora callback tardio, corrupção tratada | TraceTests/TraceCorruptionTests +revisão memory_review | PASS |
| Voz gate antesPortAudio, duranteplayback/cauda, síntese não bloqueia, resetVAD, opçãofones passada ao filho | test_speaker_capture3 +test_voice_model_routing2 +continuous5 | PASS sem dispositivos |
| UI fases, duração e escolha de fones | Vitest16 testes focais; buildtsc/vite; validate_task_ui Chromeheadlessisolado comrespostas simuladas | PASS |
| Suite local regressões | unittestdiscovertests/local56; reviewer repetiu56; terminalfailures8 | PASS |
| Tarefa real MercadoLivre | InicialFAILreplysemexec→corrigido→PASS32.3s/28.2background→repetiçãoFAILgeometria pósnavigate→corrigido | Revalidação final pendente |

Não medir economia percentual entre execuções diferentes. Logsafeinference/phase não é pensamento privado do modelo. Acústica real microfone/altofalante não validada nesta rodada.

## 2026-10-08 — Orientação sobre seleção da chamada

Inspeção e revisão independente memory_review PASS: CmdK/App, selectedModel/LocalCallPanel, OJ_CALL_MODEL/local_call→TaskClient, TEMP/BusinessAgent. Não existe seletor individual no painel, chamada ativa captura escolha inicial. Verificação estática, sem chamada real nesta rodada; nenhuma configuração alterada.

## 2026-10-08 — R-021 inventário pós-migração

Servidor reaberto: /v1/models confirmou exatamente três nomes públicos; interface pronta5174.

| Critério | Evidência | Resultado |
|---|---|---|
| Deduplicar nomes; ocultar somente alias comprovado; manter isolados | test_model_inventory.py:3 testes, RED2falhas→GREEN; suíte48PASS | PASS |
| Lista real correta sem remoção | OllamaEngine.list_models3nomes: gpt-oss20b,qwen9b,qwen4b; tagsbruto permanece5 | PASS |
| Revisão independente | memory_review:18modeltestsPASS, leitura código sem achado material | PASS |

mac_diagnosis leu manifests: publicgpt contém filhosggml21fd e llamacpp9ba9; alias9ba9 idêntico à segunda variante. Logs confirmam migração08:37:39–08:37:58. Blobsoriginal/convertido distintos,≈12,85GiB cada; não inferir duplicação física APFS pelo tamanho lógico. Fonte oficial: https://pkg.go.dev/github.com/ollama/ollama@v0.40.1/compatmigrate.

## 2026-10-08 — R-020: cache de cinco minutos

| Critério | Evidência | Resultado |
|---|---|---|
| Seleção não força descarregamento | RED: dois testes falharam por keep_alive0; GREEN e revisão de model_residency | PASS |
| Três caminhos HTTP renovam keep_alive5m; override preservado | test_model_keep_alive.py, httpx.MockTransport real serializer | PASS |
| Lazy startup, seleção, tarefas/voz e concorrência preservados | `.venv/bin/python -m unittest discover -s tests/local -q`:45; agente memory_review repetiu45 e subset15 | PASS |
| Cache real e prazo renovado | `scripts/local/validate_model_cache.py`:4b residente após duas gerações, deadlines08:49:35.078907 e08:49:37.293888-03,300s restantes em ambas | PASS |

- Após reabrir atalho: Interface pronta5173; diagnóstico zero tarefas/diálogos/chamada,4b ainda residente3,83GiB. git diff --check PASS.
- Sem download, unload forçado, alteração de contexto ou helper/TCC. Teste real deixa4b expirar normalmente.
- Não foi aguardada expiração física por cinco minutos; sonda comprova prazo informado pelo serviço e renovação, não garantia contra pressão de memória.
- Pytest de engine não disponível na venv; unittest cobre serializers generate/stream/stream_full.
- mac_diagnosis (read-only) confirmou no log Ollama evicção por memória às08:37:39 e08:38:07; previsão13,1GiB versus disponíveis9,5/3,6GiB.

Data das evidências: 2026-10-07 (America/Sao_Paulo).

| Critério | Evidência | Resultado |
|---|---|---|
| Harness acessível e lido | `cat docs/prompts/PROMPT_HARNESS_CODEX.md` retornou o contrato, os oito arquivos e os gates | PASS |
| Estado inicial identificado | `git status --short` e `git branch --show-current`: alterações preexistentes e branch `main` | PASS |
| Memória criada e índice coerente | Script `python3` com `pathlib`/`re`: conjunto exato de oito Markdown não vazios e links locais existentes | PASS |
| Revisão independente | Subagente `memory_review`: leitura dos oito documentos; script Python confirmou arquivos, datas e oito links existentes; nenhum achado material | PASS |
| Escopo preservado | Revisão comparou `git status --short` inicial e final: apenas `?? docs/anotations/` foi acrescentado; demais entradas iguais | PASS |
| Diff rastreado sem problemas de whitespace | `git diff --check`, código de saída 0; não inclui documentos novos não rastreados | PASS |

Testes de produto não executados: escopo exclusivo de documentação. Isso não
valida as alterações preexistentes de código nem o comportamento do aplicativo.

## Retomada — evidências em 2026-10-07

A observação acima descreve a entrega documental inicial. Na retomada houve
mudança de produto e verificações abaixo; simulação é indicada explicitamente.

| Critério | Evidência | Resultado |
|---|---|---|
| Saudação direta e delegação pela IA | `scripts/local/validate_models.py` fora sandbox, Ollama real qwen3.5:9b; reply para Bom dia e delegate para Mercado Livre; requires_execution false/true | PASS real, sem execução de tarefa |
| Pedido original preservado | Mesmo script: decisão real seguida de fila simulada; executor recebe original e resumo | PASS misto real/simulado |
| Bloqueio terminal e revisão negativa | `unittest discover -s tests/agents -p test_business_terminal_failures.py`: 8 testes | PASS simulado |
| Desktop e voz | `.venv/bin/python -B -m unittest discover -s tests/local`: 24 testes na revalidação final | PASS simulado |
| Memória Obsidian | `unittest discover -s /Users/JP/OpenJarvis-local -p test_obsidian_memory.py`: 4 testes, cofre temporário | PASS; cofre pessoal não alterado |
| Frontend voz/chamada | `npm test -- --run src/lib/local-call.test.ts src/lib/tts.test.ts`: 24 testes | PASS simulado |
| Frontend build | `npm run build`, revisão independente | PASS |
| Native compilação e transporte | clang SDK26.5, arquivo privado, status e entrada inválida; revisão independente | PASS técnico, sem eventos físicos |
| Atualização local | `scripts/local/install_runtime.py --install --check`: instalado com backup runtime-20261007T193946.484676Z | PASS instalação |
| TCC após atualização final | `scripts/local/validate_desktop.py`: identidade local.openjarvis.maccontrol via LaunchServices; AX1, screen=true, posting_events=true | PASS real após concessão manual |
| Chrome, site e próxima ação | `validate_desktop.py --navigate --screenshot --next-step`: URL exata, imagem real utilizável e TEMP4b clicou busca | PASS real |
| Microfone, eco e interrupção acústica | Testes sintéticos não comprovam uso real | Pendente |
| Kokoro real após interrupção | `validate_voice.py` com runtime.sh, WAV real 90380 bytes/24000Hz, nova resposta2,14s após interromper síntese longa | PASS real sem reprodução/microfone |
| Diagnóstico TCC exato | Log com filtro somente helper: requisito de código obsoleto em Accessibility; reset específico e concessão manual posterior | PASS diagnóstico e correção |
| Permissões da identidade atual | Após nova habilitação: validate_desktop mostra AX1, screen=true, bundle correto via LaunchServices | PASS real |
| Cursor físico | Retorno nativo mede x794,y97; usuário confirmou movimento e clique | PASS real |
| Navegação completa | Falha inicial de digitação corrigida no helper; usuário confirmou funcionamento, teste integrado chegou à URL exata | PASS real; FAIL inicial preservado no worklog |
| Captura utilizável | Captura inicial preta corrigida; JPEG posterior inspecionado mostrou página real | PASS real; FAIL inicial preservado no worklog |
| Conversão de captura corrigida | Fixtures versionáveis native/test_resize.m: antigo0,0,0; novo221,40,21; compilação SDK26.5 e revisão independente | PASS fixture e imagem real |
| Digitação real depois da correção | Usuário confirmou funcionamento muito bom e abertura de anúncio por autocomplete | PASS físico; destino inicial errado motivou D-006 |
| URL inicial após espaço final | Teste integrado e fluxo completo confirmaram igualdade exata com https://www.mercadolivre.com.br/; revisão independente e 10 testes focais | PASS real e regressão |
| Conversa disponível durante tarefa | unittest test_business_stream_runtime.py, 2 regressões; revisão independente | PASS simulado |
| Inicialização de modelos | runtime.sh → preparar_modelos.py real, relatório modelos-validados.json, 2 residentes10,8GiB | PASS real |
| Fluxo completo | runtime.sh → validate_flow.py: principal9b, fila, especialista, desktop, revisão, done; URL final exata e memória temporária | PASS real |
| Atalho e prontidão | `/usr/bin/open` no atalho da interface; estado externo indica portas8001/5173; curl fora sandbox `/health` retorna status ok, interface HTTP200 | PASS real; microfone não iniciado |

Latências reais focais do principal aquecido: aproximadamente 6,3–6,5s;
primeira carga: 22,41s. No fluxo completo posterior: confirmação24,14s e
conclusão80,22s. Esses tempos não comprovam resposta rápida por voz.

## Seletor de modelos — 2026-10-08

| Critério | Evidência | Resultado |
|---|---|---|
| Lista instalada completa e seleção respeitada | Teste RED mostrou apenas9b e escolha sobrescrita; test_model_selection.py inclui chat, clone de tarefa, TEMP independente e preload | PASS após correção, 4 regressões |
| Conexão gerenciada e autenticação | api.models.test.ts: loopback antigo, remoto preservado, modo não gerenciado, preload autenticado | PASS, 4 regressões |
| Regressões relacionadas | unittest discover tests/local:28; vitest api.models/api.auth/store.models/local-call/tts:40 | PASS |
| Compilação frontend | npm run build: tsc/vite | PASS; avisos de tamanho de bundle/importação de analytics |
| Abas e modelos em navegador | validate_model_picker.py, Chrome headless isolado:9b e4b listados; três ciclos Instalados/Downloads/Nuvem, pesquisa e escolha4b | PASS real |
| Carregamento e propagação da seleção | Mesmo script: /v1/models/preload real PASS; chat enviou4b com geração interceptada | PASS real preload; envio de chat com resposta simulada |
| Inferência com seleção real | Mesmo script: BusinessAgent padrão9b, chat escolhido4b, Ollama real registrou models_used=[qwen3.5:4b]; decisão reply e memória temporária | PASS real |
| Tradução externa | Mesmo script: emulação de mutação honra translate=no e não altera nós do seletor; sem pageerror | PASS emulação; Google Translate real não testado |
| URL local obsoleta e chamada | Contexto isolado configura localhost:1; UI funciona via proxy; endpoint local-call/status disponível | PASS; sem iniciar microfone |

Downloads novos não executados: o pedido é restaurar a aba e a seleção; evitar
instalar modelos somente para testar. A troca no seletor vale para o chat e suas
tarefas; a chamada contínua ainda usa o modelo configurado no runtime.

## RAM e modelo de voz — 2026-10-08

Nota anterior sobre voz foi substituída por D-008: novas chamadas recebem modelo
selecionado; chamada já em andamento conserva sua escolha inicial.

| Critério | Evidência | Resultado |
|---|---|---|
| Diagnóstico de residência | /api/ps real:9b7621298644 bytes +4b4115764768 bytes | CONFIRMADO: ambos carregados |
| Liberação real do9b | validate_model_memory.py --select qwen3.5:4b: sem tarefas/diálogos/chamada ativos, unloaded9b, retained[]; só4b3,68GiB depois | PASS real |
| Preservar trabalho e TEMP | test_model_residency.py: estados ativos, TEMP, nova limpeza ociosa e inferência non-stream com rota/lock real | PASS HTTP simulado |
| Concorrência | Revisão task_failures reproduziu duas corridas (FAIL); serialização de aquecimento+seleção+descarga e agent_model_lock compartilhado; reproduções independentes passaram | PASS após correção |
| Modelo de voz transmitido | TaskClient remoto, HTTP start/submit, ambiente de subprocesso testados sem microfone | PASS simulado |
| Instalação de voz | install_runtime.py --install --voice-only; backup runtime-20261008T111548.449095Z | PASS real; helper nativo não reconstruído |
| Regressões | unittest tests/local36; frontend store.models/api.models/local-call/tts32; build tsc/vite | PASS |
| Preferência após reabertura | validate_model_picker.py: seleção4b salva, page.reload manteve botão Ativo4b; inferência real posterior usou4b | PASS real |

Teste acústico continua pendente; não houve gravação ou chamada real nessa
validação. Valores de memória são os informados por Ollama, não RAM total.
Conferência final depois da inferência/reload: só qwen3.5:4b residente,4,25GiB;
sem tarefas/conversas/chamada ativos. O tamanho varia conforme contexto/alocações;
3,68GiB foi a medida imediatamente após descarregar9b, não um consumo fixo.

## Downloads personalizados — 2026-10-08

| Critério | Evidência | Resultado |
|---|---|---|
| Saber se gpt-oss foi instalado | task_failures consultou /api/tags read-only: gpt-oss:20b,13793441244 bytes em disco, registro08:22:54 | CONFIRMADO instalado; não confundir tamanho em disco com RAM |
| Retorno visual perto do campo | validate_custom_download_ui.py: Chrome isolado, botão/status download, erro, nome preservado, nova tentativa, carregamento e sucesso | PASS, transferências simuladas |
| Evitar falso sucesso | test_model_download.py: error com HTTP200, falta de conclusão, modelo ausente, :latest e inventário inválido | PASS, 5 regressões |
| Regressões e build | 40 testes locais antes do caso adicional; 5 testes focais após ajuste; npm run build final | PASS |
| Revisão independente | voice_review/task_failures; bordas de seleção concorrente e inventário inesperado corrigidas e revalidadas | PASS focal |

Sem teste de transferência grande real: modelo do usuário já está instalado;
não iniciar novo download somente para provar retorno visual. Percentual/bytes
não disponíveis no contrato atual; interface mostra fases e confirmação final.

## Primeiro envio — 2026-10-08

| Critério | Evidência | Resultado |
|---|---|---|
| Checker não aquece ou baixa | tests/local/test_lazy_models.py: engine só recebe health/list_models, mesmo faltando modelos; checker instalado executado real | PASS |
| Seleção fria não gera | Teste com ps vazio, client.post não chamado; endpoint valida instalado; GPT-OSS tratado como local | PASS simulado |
| Abrir/selecionar deixa RAM vazia | validate_lazy_models.py: baseline ps[], atalho sem warm, Chrome isolado selecionou9b e4b mantendo ps[] | PASS real |
| Primeiro envio carrega escolhido | Mesmo script: saudação real escolheu4b; residentes somenteqwen3.5:4b | PASS real |
| Regressões | 44 testes locais; 15 frontend seleção/persistência/voz; build tsc/vite e revisão independente | PASS |
| Download sem aquecimento | validate_custom_download_ui.py adaptado para select: feedback download/seleção, erro e retry com transferências simuladas | PASS |

Validação fria liberou apenas Qwen9b/4b já residentes após comprovar ausência de
trabalho ativo, sem apagar modelos. Abrir aplicativo normalmente não descarrega
modelos de terceiros. Scheduler existente pode gerar se houver trabalho agendado
devido; não é aquecimento automático. Modelos de áudio são independentes dos LLMs.

## 2026-10-08 — Reafirmação do contrato documental

| Critério | Evidência | Resultado |
|---|---|---|
| Pedido atual registrado com data, origem e finalidade | user-preferences.md, seção de reafirmação; worklog.md, retomada do contrato | PASS |
| Coerência com memória e capacidades reais | Subagente `verify_context`, somente-leitura: conferiu quatro documentos e consistência com D-001/D-002 | PASS |
| Oito documentos de memória presentes e não vazios | Script Python com `Path.stat().st_size > 0`, saída PASS, exit 0 | PASS |

`git diff --check -- docs/anotations` retornou 0; a pasta está não rastreada no estado inicial, portanto esse comando não comprova seu conteúdo. Evidência documental fornecida pela leitura independente. Nenhum teste de produto executado: não houve mudança de comportamento executável.
