# Registro de trabalho

## 2026-10-08 — R-025 consolidação e revisão

- Escritos oito relatórios01–08, README com cobertura18itens e EVIDENCIAS com35âncoras e complemento AST. Fonte atual, não apenasHEAD.
- A: task_failures (arquitetura/loops e gatefinal); B: mac_diagnosis (nativo/Chrome/journal); C/E: memory_review (inferência, depois segurança/testes); D: voice_review (memória/aprendizagem). Revisores somenteleitura, sem produto/runtime.
- Correções de relatório após validação: criação automática LoopGuard pela base, journal sem session e umbackup, JSONválido, limite20complementos, nomenclaturaMAIN, responsabilidadeSkillManager. Nenhuma correção executável.
- Comandos: rg/leitura numerada, AST sem importar módulos, hashesproduto, links/ranges/JSON/palavras08. Primeiro comando `python` indisponível; refeito compython3, sem instalar dependências.
- Comparação baseline2122produto/testes confirmou zeroalterações/novosprodutos. Nenhuma suíte, inferência, GUI, download ou instalação nesta auditoria. Resultados antigos continuam históricos.

## 2026-10-08 — Auditoria R-025 iniciada

- Lido documento anexo integral; requisito exclusivo investigação substitui trabalho de implementação anterior. Baseline de hashes de produto/testes em arquivo temporário, estadoGit preexistente preservado.
- Revisores reais: task_failures A (arquitetura/loops), mac_diagnosis B (ComputerUse), memory_review C (inferência). Root consolida e investiga memória/segurança; D/E delegados sequencialmente conforme limite4slots. Nenhuma mudança de funcionamento autorizada.

## 2026-10-08 — Fechamento R-022/023/024

- Adicionada otimização: summary do revisor aprovada com evidências pode ser resposta final; evita novaIA somentepara reescrita. Fallback/revisão/guards/eventos/metadados originais preservados, teste dedicadoPASS. task_failures revisou57tests/8terminalPASS.
- Erro recuperado de tool passa código público na timeline (window_changed etc), sem texto bruto. Duração porfase registrada monotonicamente.
- Última navegação realPASS30,2s/24,7background,5modelcallsbackground,1toolattemptsemfalha,7,705snaação nativa. Não representar como instantâneo. UIheadlessisoladaPASS,16frontend,build e57locals+8terminalPASS.
- Arquivo legadoexterno teste fixtureinvalidplan outdated19PASS/1error foi identificado pelaQA; não editado porque não integra produto e novo contratojátemregressão local. Limitação registrada.
- Implementação ativa e documentada; nenhuma mudança de helper/TCC/cofre/modelos e nenhum download. Acústica real mantém validação manual futura; modoaltofalante funcionalprotegido por gate+cauda.

## 2026-10-08 — R-022/023/024 implementação e loop de falhas

- Planner passou schemaestrito tasks1..3, validação integral, reparo máximo1 e erro curto+causa pública. notes_processed evita extração duplicada de mensagens já processadas; complemento direto redefine marcador. Menos etapas redundantes, sem reduzir revisão necessária ou classificar por palavras.
- TaskManager/ControlledEngine registram metadados e duraçõesmonotônicas, fase da falha, UI mostra etapa/tempo/modelo/linha do tempo; JSONL200eventos/task, rotação5MiB+arquivoanterior. /v1/business-tasks/events?task_id consulta histórico. Não incluir logs no contexto doLLM. Arquivo padrão logs/task-events.jsonl no runtime, sem prompts/telas/URLs/dados digitados.
- Revisão achou read_events quebrando com [] e arquivo ilegível; corrigido teste de corrupção/API503. Logger geral de erro agora id/fase/tipo, sem texto bruto da exceção.
- Voz: copiar audio_continuo externo para fonte revisável, resetVAD, gatealtofalante duranteplayback+.5s; checkboxfones permitebargein anterior. Corrida de inícioPortAudio corrigida publicando streamantescontext; indicadorOuvindo aguarda cauda no modoaltofalante. Instalados2scripts backup speaker-protection-20261008T121027.620130Z, checksum guard; helper/TCC/config/modelos preservados. Teste novo inicialmente chamou mock_play emvezimplementação; fixture corrigida, teste real de ordem semdevice PASS.
- Teste real inicialFAIL: principalreply alegou abertura semtask. Prompt encaminhamento explícito comexemplos e validação reply+requires_execution incompatível; seguintePASS32.3s/28.2background, computer_step real,6consultasLLM na tarefa.
- Repetição independenteFAIL24.2s/20.7background apósnavigate: posiçãojanela mudou na observação. chrome_view correlaciona título/bounds DEPOIS nativeactivate;3observações limitadas sem repetição deações, guardsdeclique preservados. Fonte/helpernativo não recompilado.
- QAfinalmemory_review56unittestsPASS, frontend16PASS, buildPASS; Chromeisolado timeline/checkboxPASS. Revalidação real final em andamento. Estado latência: não prometer instantâneo nem AEC acústico completo.

## 2026-10-08 — Diagnóstico R-022/023/024

- Root inspecionou BusinessAgent/TaskManager/ComputerStepTool/painéis e runtime voz. task_failures reproduziu formato JSON válido semtasks causando erro; voice_review reproduziu eco duasreflexões RMS1961,9>900 com VAD indevido; memory_review mapeou ausência de timeline/duração persistida.
- Agentes somenteleitura; root implementador. Origem exata do output histórico não confirmada; nenhum conteúdo de conta/logbruto registrado.

## 2026-10-08 — Orientação do seletor de voz

- Inspecionados App shortcutCmdK, LocalCallPanel, local_call.start, chamada_continua.TaskClient, BusinessAgent e variáveis seguras runtime/voz. Nenhuma chamada iniciada ou config alterada.
- Resposta deve distinguir menuprincipal existente de menuindividual inexistente. Não afirmar voz fixa9b:9b é padrão; UI envia seleção explícita. Pedido de menu novo ainda não formulado. Revisão read-only memory_review solicitada.

## 2026-10-08 — R-021 entregue

- Fonte list_models normaliza nomes duplicados e remove alias somente quando hash/digest corresponde a nome público; não remover modeloisolado.
- Três regressões novas, suíte48PASS; memory_review revisou/read-only18PASS. mac_diagnosis confirmou dois filhos do manifest e aliasidêntico, logs de migração.
- Consulta real: lista corrigida3nomes, tagsbruto5preservado. Zero tarefas/diálogos/chamada antes de reabrir atalho; startup sóconsulta inventário.
- Nenhum modelo removido, baixado ou inferência gerada. Alterações preexistentes preservadas.

## 2026-10-08 — Investigar duplicação do inventário

- Root consultou tags:5registros, dois gpt-oss20b e alias llamacpp9ba9 com mesmo digest do segundo. mac_diagnosis delegado para logs/migração somenteleitura. Fonte oficial compatmigrate descreve conversão local.
- Implementação delimitada à normalização do inventário; nenhum download ou remoção.

## 2026-10-08 — R-020 validado

- Sonda real validate_model_cache.py: duas gerações4b num_ctx8192, prazo300s renovado, sem unload. Não alterar contexto/limites nem modelos do usuário.
- QA/revisão independente memory_review: subset15 +suite45 PASS; pytest ausente, cobertura HTTP via unittest disponível. Nenhum achado material.
- mac_diagnosis confirmou evicção por capacidade; leitura de logs/ps, sem edição. Modelo herdado usado conforme adaptação D-002.
- Atalho Interface.command reaberto para carregar fonte nova; checker relatou nenhuma geração no startup. Documentação dos oito arquivos reconciliada.

## 2026-10-08 — Cache após último uso

- Pedido R-020: cinco minutos de inatividade; startup lazy preservado. Root implementou; memory_review analisou contrato; mac_diagnosis leu ps/logs sem geração ou descarga.
- RED: duas regressões de seleção falharam por unload imediato anterior. GREEN: retirado unload da seleção, keep_alive5m explícito nos três caminhos HTTP de inferência, overrides intencionais preservados. 45 testes locais PASS.
- Logs confirmaram evicção por RAM ao carregar gpt-oss20b; TTL real já5m, logo não atribuir todas as recargas à seleção. Contexto não alterado nesta entrega.
- Validação read-only runtime: zero tarefas/diálogos/chamada e ps vazio. Próximo: sonda explícita de duas gerações4b e revisão independente; nenhuma geração integra startup.

## 2026-10-08 — Inicialização sem pré-carregamento

- Pedido explícito de carregar apenas no primeiro envio. Preparação dos atalhos
  aquecia9b+4b; App e seletor também aqueciam. Substituídos por checker e seleção
  sem geração. Rota preload continua explícita, sem chamada automática na UI.
- Mudanças: preparar_modelos.py/install_lazy_startup.py, APIselect/model_residency,
  frontend App/CommandPalette/api, classificação localgpt-oss e regressões.
- Checker externo instalado com backup lazy-startup-20261008T113407.207447Z.
  Sem alterações de config/modelos/helper. 44 testes locais e15 frontend PASS;
  build PASS, revisores task_failures/voice_review confirmaram escopo.
- Revisores identificaram validadores antigos usando preload; três adaptados
  para select e status Selecionando. Fixture ps atualizada ao novo contrato.
- Teste frio: ps[] antes do atalho; abrir/selecionar9b/4b manteve ps[]; primeiro
  envio real carregou apenas4b. Primeira execução antecedeu prontidão do launcher
  (interface.json ausente); repetida depois de confirmar checker sem warm.
- Primeiro teste imprimiu PASS mas cleanup Playwright gerou Target closed após
  Response.finished; diagnóstico ajustado para aguardar corpo SSE/[DONE] completo
  e reexecutado, sem apresentar warning como falha de inferência.
- Reexecução aguardou SSE completo e terminou PASS sem warning.4b usado no teste
  foi liberado após confirmar Jarvis ocioso. Na conferência final gpt-oss:20b
  estava residente (não estava no teste frio); origem não atribuída sem evidência,
  preservado por estar fora da limpeza de Qwen do teste. Não alegar RAM final
  vazia. Alterações preexistentes preservadas, sem commit.

## 2026-10-08 — Downloads por nome

- Usuário não soube se gpt-oss:20b começou a baixar. Revisão read-only confirmou
  modelo instalado no Ollama e ausência de indicador custom, embora pulling=true.
- Frontend CommandPalette/api: feedback próximo ao campo, duas fases, nomes
  preservados, boolean de sucesso, guardref contra duplicidade/seleção concorrente.
- Backend routes: recusa error HTTP200, exige sucesso e modelo no inventário,
  distingue timeout; teste adicional de inventário inválido após revisão.
- Revisores somente-leitura voice_review e task_failures. 40 testes locais,
  cinco focais finais e build PASS. Chrome isolado testou duas vezes download/
  erro/retry/carregamento/sucesso com fetch controlado; nenhuma transferência real.
- Interface ociosa (sem tarefas/chamada) reaberta para carregar correções. Registros
  de modelos residentes não são usados como prova de download ou inferência.

## 2026-10-08 — Modelos residentes, RAM e voz

- Relato:4b selecionado, RAM segue alta; consulta real confirmou9b e4b residentes.
  macOS total/RSS não medidos. Diagnóstico não confunde carregamento com inferência.
- Implementados D-008: model_residency.py/routes, persistência store/App,
  LocalCallPanel/local-call, local_call/business_tasks, cópia de voz e regressões.
- Revisores task_failures e voice_review somente-leitura; duas corridas do
  primeiro foram reproduzidas e corrigidas. Revalidação independente PASS.
- Voz instalada com backup runtime-20261008T111548.449095Z, sem rebuild/TCC.
- Interface estava sem interface.json na primeira conferência; atalho reaberto.
  API sem trabalho ativo; seleção4b descarregou9b e consulta mostrou apenas
  4b3,68GiB. Modelos instalados e dados preservados.
- 36 testes locais, 32 frontend e build PASS; voz validada por payload/ambiente,
  sem uso do microfone. Preferência4b após reload no Chrome isolado PASS;
  inferência real4b PASS, memória pessoal temporária.
- Medição final: somente4b residente,4,25GiB após uso do contexto;9b ausente.
  Valor difere da medida inicial de3,68GiB após descarga; RAM não é constante.

## 2026-10-08 — Orientação para Dock

- Confirmados nomes dos dois atalhos na Mesa por busca de arquivos; consultada
  documentação oficial da Apple sobre área de arquivos no Dock. Instruções
  registradas no contexto; pergunta informativa, sem modificar Dock ou executar
  o atalho de encerramento.

## 2026-10-08 — Diagnóstico do seletor de modelos

- Imagens do usuário: lista só qwen3.5:9b, chamada Failed to fetch, Downloads
  provoca erro de remoção de nó. Preservado estado Git preexistente.
- Subagentes somente-leitura: task_failures confirmou filtro OJ_MAIN_MODEL no
  endpoint e substituição da seleção no construtor BusinessAgent; voice_review
  confirmou catálogo local e hipótese de tradução externa mutando DOM.
- getBase prioriza URL persistida sobre proxy; preloadModel acessa Ollama direto
  do navegador. Investigar ambos sem atribuir causalidade ainda não comprovada.
- RED: lista só9b, chat ignora another:8b, preload ausente; frontend ignora modo
  gerenciado e envia preload diretamente a11434. GREEN após correções D-007.
- Regressões: 28 testes locais, 40 frontend, build tsc/vite PASS. Revisores
  confirmaram backend e frontend. Achado handlePull selecionava antes de carregar;
  corrigido para usar handleSelect e confirmado pelo revisor.
- Chrome isolado: abas, pesquisa, modelo4b carregado pelo backend e seleção
  enviada em chat com resposta simulada PASS. URL antiga localhost:1 não interfere
  no modo gerenciado; status da chamada disponível. Sem downloads ou microfone.
- Teste de navegador teve duas falhas de fixture/sincronização: onboarding-seen
  usa string true (não1); aguardar textarea antes do atalho. Corrigidas no script,
  não eram falhas de produto. Primeira execução ocorreu antes da prontidão do
  launcher; modelos preparados e interface confirmada em5173/API8001.
- Validação adicional real: principal padrão9b recebeu seleção4b e gerou via
  Ollama com models_used=[qwen3.5:4b], resposta sem delegação. Memória temporária.
  Entrega deste escopo concluída; limitações de tradução pessoal e voz anotadas.

## 2026-10-07 — Explicação da navegação sem URL

- Usuário perguntou se o controle é plugin e se consegue acessar anúncios da
  conta de vendedor por cliques. Inspeção de `ComputerStepTool.execute` e do
  prompt do especialista confirmou observação → ação única → nova observação,
  com objetivo mantido pelo especialista. Não é extensão do Chrome.
- Explicação distingue capacidade implementada de percurso ainda não testado;
  nenhum acesso à área de vendedor executado nesta resposta.

## 2026-10-07 — Retomada das pendências anteriores

- Pedido: resolver problemas descritos em `PROMPT_MEMORIA.md`; usuário retomou
  após interrupção e informou ajuste do esforço para medium.
- Prioridade: Chrome pessoal e cursor real, diagnóstico correto de permissões,
  sem alegar sucesso a partir de simulações.
- Papéis: `mac_diagnosis` (leitura de controle nativo/permissões), `task_failures`
  (edição delimitada em business/task_runtime e testes), `voice_review` (leitura
  de voz e inicialização); principal integra e corrige ferramenta desktop.
- Estado inicial: mesmas alterações preexistentes e memória inicial já criada.
- Arquivos externos existem em `/Users/JP/OpenJarvis-local`; alterações ali
  exigem escalation. Leituras não registram dados pessoais do cofre.
- Hardware/macOS confirmados: Apple M5, 24 GB, macOS 26.6.2. Identificadores
  pessoais do equipamento não são guardados na memória.
- Diagnóstico autorizado fora sandbox: Chrome disponível; inicialmente ambas
  permissões negadas. Após configuração do usuário, Acessibilidade=true;
  Gravação de Tela=false na chamada direta, apesar da confirmação de inclusão.
- Testes RED de desktop: três falhas reproduziram metadados de permissão
  ausentes e continuação indevida após erro AX. Correção focada passou.
- Ollama real: saudação respondeu sem tarefa; abrir Mercado Livre delegou.
  Tempos observados 22,41s com modelo inicialmente descarregado e 6,32s seguinte.
  Delegação resumiu o objetivo como `abrir_site`, perdendo a intenção completa;
  correção preserva pedido original além do resumo IA.
- Suíte anterior: 69/70 passaram; falha restante era fixture sem permissões
  no teste de aquisição. Cópia versionável ajusta fixture ao novo contrato.
  Nenhum dado do cofre foi alterado pelos testes (diretórios temporários).
- Frontend: 24 testes de voz/chamada passaram; build tsc/vite passou na revisão.
- Preparadas cópias de voz/helper e instalador com backup/rollback em
  `scripts/local/`; aplicação externa ainda pendente da revisão e escalation.
- Atualização aplicada com aprovação; backup em
  `/Users/JP/OpenJarvis-local/backups/runtime-20261007T193946.484676Z`.
  Cópias versionáveis iguais às instaladas; launcher existente calcula fingerprint
  dos arquivos modificados para reiniciar serviços na próxima abertura.
- Kokoro real (sem playback/microfone): `validate_voice.py`, carregamento0,86s,
  interrupção de síntese longa e nova resposta2,14s, WAV90380 bytes/24000Hz,
  somente resposta da versão nova entregue. PASS de síntese, não teste acústico.
- TCC: usuário reautorizou; tela=true, AX=0. Log dirigido comprovou hash obsoleto;
  reset específico de Accessibility aprovado e executado; aguardando habilitação
  manual do aplicativo atual. Não há ação física repetida contra bloqueio.
- Após habilitação posterior, LaunchServices confirmou AX=1 e screen=true.
  Primeiro teste físico encontrou Chrome sem janela (-1719); fluxo reabre pelo
  Dock/Spotlight uma vez e fixture nova passou. Depois janela apareceu.
- Divergência real de título: AppleScript retorna título da guia e AX inclui
  sufixo do Chrome/perfil. Ajustada comparação mantendo bounds e título AX
  exato como guarda da ação; teste de janela diferente continua falhando seguro.
- Navegação ainda falhou: mouse chegou à barra (posição medida x794,y97), mas
  campo não recebeu URL e guia continuou `chrome://newtab/`.
- Usuário confirmou: viu cursor mover e clicar; não houve digitação nem
  navegação concluída. É evidência física parcial, não sucesso do objetivo.
- Captura JPEG observada totalmente preta; investigar conversão com fixture.
  Hipótese de teclado: flags herdadas após atalhos Command; testar e corrigir
  antes da próxima atualização nativa, sem apresentar hipótese como fato.
- Fixture nativa reproduziu captura antiga preta (RGB0,0,0) e nova conversão
  preservando cor (RGB221,40,21). Teclado testa 12 eventos interceptados com
  fonte privada, flags explícitos, Command liberado e UTF-16 por codepoint.
  Evidências versionáveis em `tests/local/native/`.
- Atualização conjunta nativa aplicada com backup
  `/Users/JP/OpenJarvis-local/backups/runtime-20261007T195817.875397Z`.
  Reset somente Accessibility/ScreenCapture desse bundle aprovado e executado;
  usuário renovou permissões. Versão final confirma AX1, screen=true, posting=true.
- Usuário confirmou funcionamento físico muito bom, incluindo digitação; site
  abriu um anúncio por autocomplete do Chrome. Instrução nova D-006 aplicada:
  espaço após URL; query original usada para conferir resultado. Sem rebuild.
- URL da página inicial foi confirmada real por AppleScript após mudança do
  espaço: `https://www.mercadolivre.com.br/`. Observação depois teve mudança
  transitória de bounds; corrigida uma única repetição de observação (sem repetir
  ação), com guards de ação preservados e teste específico PASS.
- Chat comum: SSE antes esperava tarefa completa e bloqueava novo input. Nova
  confirmação encerra stream e mantém execução no painel; TDD TimeoutError→PASS,
  revisão independente confirmou continuidade, redirecionamento e histórico1x.
- Preparação real via `runtime.sh`/`preparar_modelos.py` passou, dois modelos
  residentes10,8GiB nessa configuração; relatório externo atualizado.
- Validação integrada `validate_desktop.py --navigate --screenshot --next-step`
  confirmou URL exata após digitar espaço, captura real utilizável e clique real
  de qwen3.5:4b na busca. Captura temporária contém dados da sessão pessoal;
  seu conteúdo não é incluído na documentação.
- `validate_flow.py` com `runtime.sh`: principal9b → fila → especialista →
  ferramenta desktop → revisão → done, sem erro e URL final correta. Memória
  SQLite temporária, cofre pessoal preservado. Confirmação24,14s e fluxo80,22s:
  sucesso funcional, sem alegação de resposta instantânea.
- Revalidação final: 24 testes locais e 8 regressões de falhas terminais PASS;
  `git diff --check` PASS. Revisor `task_failures` somente-leitura confirmou
  espaço final apenas na URL, verificação original preservada e 10 testes focais PASS.
- Atalho `OpenJarvis Interface.command` aberto com escalation aprovada para
  verificar inicialização dos serviços após correções. Estado externo confirma
  portas8001/5173; API `/health` retorna status ok e interface HTTP200. Consulta
  inicial a `/v1/health` devolveu HTML (rota incorreta), descartada como evidência
  de saúde; verificação correta executada depois. Microfone não iniciado.
- Estado de entrega: regra do espaço e controle físico validados; retomada geral
  parcial apenas quanto à experiência acústica e ao objetivo de baixa latência.
  Nenhum commit/push/deploy, alteração de cofre pessoal ou troca de modelos.

## 2026-10-07 — Inicialização da memória

- Objetivo: aplicar o harness indicado e preservar a orientação documental.
- Estado inicial: branch `main`; árvore com alterações preexistentes; pasta
  `docs/anotations/` ausente. Os prompts também já estavam presentes e não rastreados.
- Inspeção: leitura de `docs/prompts/PROMPT_HARNESS_CODEX.md`, `README.md` e
  `CONTRIBUTING.md`; busca de `AGENTS.md` e documentação relevante.
- Comandos: `git status --short`, `git branch --show-current`, `rg --files`,
  `ls docs/anotations` e leitura dos arquivos com `cat`/`sed`.
- Resultado inicial: a pasta de memória não existia; a busca opcional em
  `.agents` e `.codex` também encontrou diretórios ausentes. Não são bloqueios.
- Arquivos criados: os oito documentos previstos em `docs/anotations/`.
- Papéis: agente principal implementa e integra documentação; subagente
  `memory_review` realiza descoberta e validação independente somente-leitura.
- Validação equivalente ao TDD: conferir existência, links, consistência e
  escopo dos documentos; não há mudança executável que justifique testes de produto.
- Resultado final: script Python confirmou os oito documentos não vazios e
  links locais existentes; `git diff --check` retornou 0 para o diff rastreado.
  Revisão independente confirmou datas, links e conteúdo, sem achados materiais.
  Comparação do status acrescentou apenas a nova pasta de memória; as demais
  entradas permaneceram iguais. Isso não é uma auditoria do conteúdo preexistente.
- Próximo estado: memória inicial concluída; aguardar uma tarefa concreta e
  continuar registrando as informações relevantes nas próximas interações.

## 2026-10-08 — R-025 aceite final

Revisorfinaltask_failures retornou PASS após correções; C/Evalidaram04/06/índice, Bvalidou03/06/08, Dvalidou05/06/08. Artefatosfinals e memória completos. Hashes2122produto/testes e inventário reconferidos intactos; links/JSON/ranges/AST/1039palavras08 PASS. Nenhum commit/push/deploy ou mudança de produto/runtime nesta auditoria.

## 2026-10-08 — Retomada do contrato documental

- Pedido: reler o harness e manter contexto durável de tudo que for relevante nas conversas. Nenhuma nova alteração de produto foi solicitada.
- Descoberta: harness, índice da auditoria e memória existente lidos; D-001/D-002 já registram esta política e a adaptação ao modelo disponível. Alterações preexistentes no Git preservadas.
- Implementação: reafirmação em user-preferences.md e registro deste ciclo; sem duplicar decisão arquitetural ou reabrir auditoria concluída.
- Inspeção: `git status --short`, `rg --files` e leitura documental. Busca inicial em `.agents`/`.codex` encontrou diretórios ausentes; uma busca de AGENTS.md no diretório pai excedeu o escopo necessário e encontrou negativas de acesso, sem alterar arquivos. Buscas seguintes restritas ao projeto.
- Validação: revisão documental independente solicitada a subagente somente-leitura; resultado registrado em validation.md após retorno. Testes de produto não se aplicam a esta reafirmação documental.
- Próximo estado: contexto de execução registrado; aguardar tarefa concreta sem inferir autorização para implementar o redesenho da auditoria.
