# Contexto do projeto

## 2026-10-08 — Arquitetura auditada R-025

A auditoria exclusiva de investigação está em [docs/auditoria/2026-10-08](../auditoria/2026-10-08/README.md). O caminho local configurado é Python/FastAPI/Business/TaskManager com especialistas Orchestrator; arquivo Rust aberto no IDE não comprova agentes Rust em execução. Plataforma oferece engines/skills/learning/vector/traces, mas wiring Business precisa ser comprovado por caminho. O objetivo futuro é harness generalista de interfaces desconhecidas, sem codificar exemplos comerciais como rotas obrigatórias. Não foi implementado redesenho nesta etapa.

## 2026-10-08 — Diagnóstico de execução e áudio

Ferramentas Python não gastam tokens por si; principal/planejador/especialista/executorTEMP/revisor/síntese fazem inferências. Execução de navegação ainda tem latência própria de IPC/captura/macOS/rede. BusinessTasksPanel mostra fila/conversa pendente e fase/tempo/modelo/tooltimeline; eventos sanitizados em runtime/logs/task-events.jsonl, consulta porid/APIevents.

Modo alto-falante pausa captura enquanto toca e por.5s depois; opçãofones mantém interrupção. Modelos/STT/TTS atuais preservados. PlanoJSONSchema+repair e memória não duplicada implementados. Resumo aprovado do revisor evita nova geração só de reescrita; casos semsummary usam síntese antiga. Último teste real30,2s não constitui latência garantida. Correlacionar janela após nativeactivation, comactions guardados pelo título/bounds observados.

## 2026-10-08 — Escolha de modelos na voz

Menu geral CmdK escolhe principal compartilhado chat/próxima chamada. Caminho confirmado: LocalCallPanel→start(model=selectedModel)→OJ_CALL_MODEL→TaskClient.model. TEMP configurado separado OJ_TEMP_MODEL4b; especialistas herdam principal, sem seletor individual. Reconhecimento Whisper small e síntese Kokoro pf_dora atuais, fora da lista Ollama. Chamada já ativa conserva escolha inicial.

## 2026-10-08 — Inventário Ollama e variantes internas

Ollama local passou gpt-oss20b por migração de compatibilidade llama.cpp: manifest público possui variantes ggml/llamacpp e alias hash da última. Inventário bruto5 não equivale a cinco IAs instaladas pelo usuário. Jarvis exibe três nomes públicos deduplicados, sem alterar arquivos.

## 2026-10-08 — Política vigente de residência

Startup e seleção só consultam inventário/alteram defaults. Inferências Ollama (generate/stream/stream_full) pedem keep_alive5m, renovado pelo próprio serviço após uso. Seleção não aquece nem libera modelo anterior; serviço cuida de prazo e evicção. D-011 substitui cleanup imediato D-008/010. Encerrar Jarvis continua podendo encerrar/liberar modelos explicitamente.

## 2026-10-08 — Atalhos no Dock

- Usuário pediu como fixar iniciar interface e encerrar Jarvis no Dock do Mac.
- Arquivos confirmados na Mesa: `OpenJarvis Interface.command` e
  `Encerrar Jarvis.command` em `/Users/JP/Desktop`.
- Procedimento: abrir Mesa no Finder e arrastar cada arquivo à área de arquivos
  do Dock, próxima à Lixeira, depois da linha separadora. Para Dock vertical,
  usar região abaixo do separador. Clicar no item abre o atalho correspondente.
- São arquivos .command; não fixar apenas o Terminal como substituto dos dois
  atalhos. Nenhuma configuração do Dock nem execução de encerramento realizada.
- Fonte oficial: https://support.apple.com/pt-br/guide/mac-help/mh35859/27/mac/27
- Esclarecimento posterior (“onde ele está?”): acessar os atalhos pelo Finder,
  Cmd+Shift+G e `/Users/JP/Desktop`; Dock é a barra de ícones normalmente na
  parte inferior da tela. Referência do usuário ambígua entre Dock e atalhos.

Atualizado em 2026-10-07 (America/Sao_Paulo).

## Fatos confirmados nesta sessão

- Repositório: OpenJarvis; branch inicial: `main`.
- O README descreve um framework de IA pessoal com execução local por padrão,
  primitivas compartilhadas para agentes, avaliações de eficiência e aprendizado
  a partir de rastros locais. Fonte: `README.md`, seção "Why OpenJarvis?".
- Superfícies documentadas: CLI `jarvis`, interface gráfica e servidor API local.
  Há diretórios `src/openjarvis`, `frontend`, `desktop`, `rust` e `tests`.
- O guia de contribuição informa Python 3.10+ e uso de `uv`.
- Há alterações preexistentes em frontend, agentes, engines, servidor e ferramentas,
  além de arquivos novos, incluindo `docs/prompts/`. Não foram produzidas nesta
  interação; seu conteúdo e sua validação ainda não foram auditados.
- Nenhum `AGENTS.md` foi encontrado pela busca inicial no repositório.

## Escopo inicial (substituído pela retomada abaixo)

Adotar o método indicado em `docs/prompts/PROMPT_HARNESS_CODEX.md` e inicializar a
memória documental. Nenhuma funcionalidade de produto foi solicitada nesta
interação. Arquitetura detalhada e integrações devem ser inspecionadas conforme
a próxima tarefa, sem inferir requisitos a partir de arquivos modificados.

## Contexto confirmado na retomada de 2026-10-07

- Hardware: MacBook Air Apple M5, 24 GB; macOS 26.6.2.
- Runtime externo existente: `/Users/JP/OpenJarvis-local`; config seleciona
  engine Ollama, principal qwen3.5:9b e agent business. runtime.sh define
  TEMP qwen3.5:4b, contexto8192, OJ_DESKTOP_CONTROL=1 e cofre Obsidian local.
- Voz: ambiente `/Users/JP/OpenJarvis-local/.venv-voz`, Kokoro local; scripts
  externos existentes foram inspecionados sem registrar conteúdo do cofre.
- Native: `/Users/JP/Applications/JarvisMacControl.app`, identidade
  `local.openjarvis.maccontrol`. Nova versão instalada oferece janela focalizada,
  evidência do cursor e transporte privado via LaunchServices.
- Cópias revisáveis e scripts diagnósticos versionáveis: `scripts/local/`.
- Escopo atual: resolver pendências do PROMPT_MEMORIA, preservando trabalho
  anterior e distinguindo testes simulados de uso real. Permissões TCC continuam
  condição para teste físico; não são contornadas.

## 2026-10-07 — Navegação por objetivo sem URL

- Dúvida do usuário: após abrir Mercado Livre, o assistente consegue chegar à
  seção de anúncios da conta de vendedor por cliques, sem receber uma URL?
- Arquitetura atual: ferramenta interna `computer_step` do agente business e
  aplicativo nativo auxiliar de controle do macOS; não é extensão/plugin do Chrome.
- Cada passo observa a janela (imagem e nós de acessibilidade), solicita uma ação
  ao TEMP e executa mouse/teclado reais. O especialista mantém o objetivo e usa
  a observação posterior para decidir o próximo passo; URL não é obrigatória.
- Capacidade prevista: abrir menu da conta, localizar área de vendedor e anúncios
  por passos observados, usando a sessão pessoal do Chrome. Login válido e
  elementos identificáveis são condições; não há roteiro específico comprovado
  para esse percurso nem garantia de conclusão de qualquer interface.
- Evidência atual: navegação real e clique real no campo de busca passaram.
  Percurso até anúncios de vendedor ainda não foi testado. Mensagem atual pede
  explicação, não autoriza executar esse percurso agora.
