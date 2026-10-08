# Requisitos e backlog

## 2026-10-08 — R-025: auditoria técnica profunda, somente investigação — CONCLUÍDA

- Origem: documento anexado AUDITORIA TÉCNICA PROFUNDA e pedido de validadores antes da entrega.
- Escopo: oito relatórios Markdown em docs/auditoria/2026-10-08, índice de evidências, revisões A–E e final confrontando código. Classificar CONFIRMADO/INFERIDO/NÃO ENCONTRADO/NÃO VERIFICADO, caminhos/funções/intervalos para afirmações importantes.
- Proibido alterar produto, configurações, instalar dependências, iniciar tarefas/GUI/LLM ou acessar contas. Apenas documentos e inspeção; testes locais somente com ambiente isolado. Caso102s é relato do usuário, não execução automaticamente comprovada.
- Gate concluído: completude validada pelo revisor final; afirmações não sustentadas corrigidas antes da entrega.

- Aceite2026-10-08:01–08+índice/README produzidos; cinco papéis por quatro subagentes reais+revisor final PASS;2122arquivosproduto preservados. Nenhuma implementação nova. Achados/próximas questões em06/08.

## 2026-10-08 — R-022/023/024: tarefas lentas, falha sem etapa e autoescuta

- Usuário relata navegação não executada, erro plano inválido, falta de etapa/log e voz transcrevendo a própria saída. Python executa ferramentas, mas decisão/planejamento/executor/revisão usam inferências; não alegar ausência de tokens.
- R-022: plano JSONSchema validado inteiro, um reparo limitado, erro preserva fase; remover extração de memória duplicada somente se principal já processou mensagem.
- R-023: timeline com início/fim/duração de modelos/ferramentas/desktop, tempo em fila/total, etapa da falha. Log sanitizado consultável sem prompts, URLs, argumentos ou transcrição.
- R-024: modo alto-falante bloqueia captura durante reprodução e cauda; opção fones mantém interrupção. Não prometer AEC completo ou prova acústica sem teste real. Sem mudar helper/TCC/modelos escolhidos.
- R-022/023/024 implementados e testes funcionais PASS. Última tarefa real30,2s/24,7background, cincoinferências e umaexecução de ferramenta semfalhas. Autoescuta protegida porgate default; não foi feito teste acústico de microfone/altofalante. Não inferir causa exata do plano histórico sem resposta bruta.

## 2026-10-08 — Dúvida sobre escolher modelos da chamada

- Usuário pergunta como escolher exatamente modelo por função e se existe menu pronto. Escopo atual é orientação/inspeção; não houve pedido explícito de implementar menu novo.
- Principal da chamada iniciada pela interface segue selectedModel. TEMP permanece OJ_TEMP_MODEL=qwen3.5:4b no runtime.sh; especialistas de raciocínio compartilham principal. Não existe UI de seleção individual por função nem perfil exclusivo da voz.
- Menuprincipal CmdK antes de iniciar; chamada ativa conserva modelo capturado, trocar seleção exige encerrar/reiniciar chamada para aplicar. TEMP troca manual em runtime.sh e reinício do servidor. Whisper small transcreve, Kokoro pf_dora sintetiza; esses não são LLM de raciocínio nem têm seletor dedicado na UI atual.

## 2026-10-08 — R-021: modelo duplicado e alias desconhecido

- Explicar origem com inventário/logs reais, sem assumir download manual de alias.
- Lista deve mostrar gpt-oss20b uma vez, preservar Qwen e ocultar alias interno comprovadamente vinculado ao mesmo digest; não deletar modelos. PASS: três regressões,48testes locais, revisão independente18tests e inventário real3nomes/tags5preservado.

## 2026-10-08 — R-020: preservar modelo entre requisições

- Usuário pede cinco minutos sem uso antes de descarregar, mantendo startup sob demanda R-019.
- Critérios: gerações normais e streaming enviam keep_alive=5m; novo uso renova cache nativo; seleção não descarrega nem aquece; preservar locks/defaults de tarefas e voz. PASS: 45 testes locais, revisão independente e duas gerações reais4b com prazo renovado de300s.

## 2026-10-08 — Carregar somente no primeiro envio

- Pedido explícito: não carregar qwen9b na RAM ao iniciar, pois modelo pode não
  ser usado; carregar somente após primeiro envio. Substitui pré-carregamento
  automático de startup, reabertura, seleção e pós-download.
- R-019: abrir e escolher modelo usa inventário/configuração sem gerar/aquecer;
  principal carrega quando mensagem é enviada, TEMP quando um passo o requer.
- Manter preferência, escolha de novas chamadas, download explícito e cache
  nativo de cinco minutos após uso (D-011). Não baixar modelos na inicialização.
- R-019 PASS real: abertura/seleção9b/4b mantiveram ps vazio; primeiro envio4b
  recebeu resposta completa SSE/[DONE] e carregou somente4b. Checker instalado;
  após teste,4b liberado ocioso. gpt-oss apareceu residente posteriormente e foi
  preservado; não alegar RAM final vazia nem atribuir essa carga ao startup.

## 2026-10-08 — Download pelo nome sem retorno visual

- Origem: usuário digitou gpt-oss:20b e não sabe se iniciou/concluiu download.
- Fato confirmado por revisão read-only: gpt-oss:20b já instalado no Ollama,
  registro08:22:54, tamanho em disco13793441244 bytes. Nenhum download novo iniciado.
- R-017: botão personalizado e mensagem próxima ao campo mostram download e
  carregamento; falhas preservam nome; Enter não inicia tentativa duplicada.
- R-018: backend não anuncia sucesso por HTTP200 com error no JSON; confirma
  conclusão e presença no inventário instalado. Não inventar percentual sem dados.
- Estado R-017 PASS em Chrome isolado com transferências simuladas; R-018 PASS
  com cinco regressões. gpt-oss já instalado pode ser escolhido em Instalados.

## 2026-10-08 — RAM após selecionar 4B

- Usuário suspeita que9b continua em uso porque selecionar4b não reduz RAM.
- Fato: /api/ps confirmou ambos residentes,9b7621298644 bytes e4b4115764768
  bytes (~10,9GiB juntos). Residência não identifica modelo de cada requisição.
- R-015: seleção deve liberar modelo anterior sem uso, sem interromper tarefas;
  manter TEMP necessário e distinguir modelo ativo de residente.
- R-016: nova chamada por voz deve receber escolha explícita da interface;
  preservar configuração externa, cofre e chamada já ativa.
- R-015 PASS real:9b descarregado,4b mantido; regressões de concorrência e
  retenção durante trabalho PASS. RAM de modelos reduziu de~10,9GiB para3,68GiB
  no primeiro teste de descarga; isso não mede toda memória do processo/Mac.
- R-016 PASS de contrato: UI→subprocesso→API→modelo escolhido; cópia externa
  instalada. Teste acústico não executado, sem iniciar microfone nesta correção.

Atualizado em 2026-10-07 (America/Sao_Paulo).

| ID | Requisito | Critério de aceite | Estado | Origem |
|---|---|---|---|---|
| R-001 | Ler e aplicar o harness | Arquivo lido e limitações documentadas | Concluído | Mensagem do usuário; harness |
| R-002 | Inicializar memória durável | Oito arquivos previstos presentes e relacionados pelo índice | Concluído | Harness, seção 2 |
| R-003 | Preservar contexto das conversas | Orientação atual registrada com data, motivo e origem | Concluído; obrigação contínua | Mensagem do usuário |
| R-004 | Preservar trabalho preexistente | Não remover alterações anteriores nem dados pessoais | Mantido na retomada; escopo documental inicial ampliado pelo usuário | Harness, contrato de execução |

## 2026-10-07 — Retomada da implementação

Origem: pedido para resolver pendências de `docs/prompts/PROMPT_MEMORIA.md`,
reiterado após interrupção da sessão. O usuário informou que mudou o esforço
de light para medium. Não há confirmação programática dessa configuração.

Escopo autorizado: investigar e corrigir controle real do Mac, permissões,
orquestração de tarefas, voz, ferramentas e inicialização; preservar dados e
alterações locais. Sem commit, push ou deploy.

| ID | Requisito / aceite | Estado |
|---|---|---|
| R-005 | Conversa natural em português, sem tarefa para saudação; decisões pela IA | Decisões reais PASS; latência de conversa ainda requer avaliação |
| R-006 | Pedido de abrir site usa Chrome pessoal visível, mouse real e guia correta sem segunda autorização | PASS real: usuário confirmou funcionamento; URL exata validada com espaço final (D-006) |
| R-007 | Ação posterior navega/clica; resultado conferido por observação | PASS real: TEMP qwen3.5:4b clicou busca, captura utilizável e fluxo completo concluído |
| R-008 | Permissão ausente gera diagnóstico curto e não repete tentativas inúteis | Correção implementada, testes PASS; diagnóstico TCC real confirmado |
| R-009 | Interrupção de fala, conversa durante tarefa e redirecionamento correto | Regressões e síntese Kokoro reais PASS; microfone/eco acústico pendentes |
| R-010 | Preservar Obsidian e gerar arquivo .xlsx real | PASS com arquivos e cofre temporários; não modificar cofre pessoal em testes |
| R-011 | Inicialização simples e logs úteis; distinguir simulação de execução real | PASS real: atalho iniciou API (/health ok em8001) e interface (HTTP200 em5173) |

## 2026-10-08 — Seleção de modelos e Downloads

- Origem: usuário não consegue trocar modelo, lista mostra apenas um instalado,
  Downloads termina em erro `removeChild`; screenshot também mostra Failed to fetch.
- R-012: listar todos os modelos de conversa instalados, permitir seleção explícita
  para principal/especialistas e manter executor TEMP independente.
- R-013: abrir e alternar abas do seletor sem falha de DOM; português nativo na
  superfície corrigida, sem depender de tradução externa.
- R-014: carregar modelos e chamada pelo servidor correto da interface local;
  investigar configurações antigas e carregamento direto do Ollama no navegador.
- Plano: testes de regressão → correção mínima → testes/build → validação HTTP
  e navegador. Não baixar modelos novos nem iniciar microfone para testar.
- Estado final R-012: PASS, listagem9b/4b e inferência real no4b selecionado;
  clone de tarefas testado e TEMP independente. Escolha no chat não reconfigura voz.
- Estado final R-013: PASS no Chrome isolado com três ciclos de abas; proteção
  de tradução validada por emulação, sem reproduzir Google Translate pessoal.
- Estado final R-014: PASS de proxy com URL loopback antiga e status de chamada;
  microfone fora deste teste. Interface reaberta com versão corrigida.
