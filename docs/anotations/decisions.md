# Decisões

## D-014 — Auditoria documental antes do redesenho

- Data:2026-10-08; origem: prompt de auditoria anexado e pedido de validação por subagentes.
- Decisão: investigar a árvore atual (incluindo mudanças anteriores), gerar01–08 e índice em docs/auditoria/2026-10-08; não tocar produto/runtime.
- Motivo: outro arquiteto precisa de fatos rastreáveis e lacunas, sem suposições de capacidade generalista/memória procedural.
- Revisão: cinco papéis A–E, quatro instâncias reais (C/E mesma instância em tarefas separadas), revisor final independente do escritor; somente root escreve docs.
- Importante: CONFIRMADO estático não é PASS operacional. Journal102s confirma padrão estrutural12computer_step/11window_changed, mas não prova domínio/menu ou subcausa.
- Direções gerais F01–F15 são propostas de investigação/evolução, não alterações aprovadas/implementadas.

## D-013 — Execução observável, planejamento válido e modos de áudio

- Data2026-10-08; implementada e validada; origem pedido de diagnosticar demora/falha/autoescuta.
- Plano com schema1..3especialistas, validar inteiro e reparo único; nenhuma execução por palavra-chave/fallback inventado. Reusar processamento de memória da decisão principal via marcador explícito; chamadas diretas preservadas.
- Registrar somente metadados de execução (fase, tempo, modelo/ferramenta, status), preservar fase anterior ao erro. Timeline não expõe pensamento interno nem dados da tela. Retenção delimitada, falha de logging não derruba tarefa.
- Resumo já aprovado pelo revisor é reutilizado para evitar inferência só de reescrita; fallback se summary ausente. Observação Mac correlaciona janela após ativação, nunca relaxa guard de ações.
- Alto-falante default protege captura durante áudio+cauda, sacrificando barge-in nesse modo; opção fones mantém comportamento interrompível anterior. Rejeitar texto parecido não resolve eco acústico. Modelo e helper/TCC preservados.

## D-012 — Inventário legível após migração Ollama

- Data2026-10-08; origem: usuário pergunta por duas entradas gpt-oss20b e um llamacpp:hash desconhecido.
- Implementada e validada; somente apresentação alterada.
- GET/api/tags confirmou nome gpt-oss duplicado com digests distintos; entrada llamacpp tem digest idêntico à segunda. Documentação compatmigrate do Ollama descreve conversão local para child llama.cpp sem novo pull.
- Ajustar apresentação: deduplicar nomes e omitir alias llamacpp:hash somente quando hash/digest corresponde a modelo com nome público. Preservar entradas isoladas, modelos em disco e seleção. Nunca excluir blobs/manifests para corrigir lista.

## D-011 — Cache por cinco minutos de inatividade

- Data: 2026-10-08; aprovada pelo pedido explícito do usuário, implementada e validada.
- Origem: cargas/descargas repetidas prejudicam latência; manter modelo por cerca de cinco minutos desde último uso.
- Substitui descarga imediata na seleção das D-008/010. Startup e escolha continuam sem aquecimento; cada geração renova keep_alive=5m no Ollama. Selecionar outro modelo não força descarga do anterior nem renova seu prazo.
- Garantia limitada pela capacidade de RAM e pelo scheduler do Ollama; logs confirmaram evicção por RAM ao carregar gpt-oss20b. RAM não tem desgaste por ciclos de escrita comparável a armazenamento flash; motivação técnica é latência e uso de recursos.
- Contrato oficial: https://docs.ollama.com/api/chat (keep_alive).

## D-010 — Carregamento sob demanda no primeiro envio

- Data: 2026-10-08; aprovada pelo usuário e implementada.
- Origem: usuário não quer inicializar qwen9b na RAM sem saber se será usado.
  Substitui aquecimento automático nas D-007/008/009; preserva preferência e
  liberação segura de modelos anteriores em uso.
- Inicialização: preparar_modelos.py passa a consultar saúde/inventário somente,
  sem download automático, geração de teste ou garantir9b+4b residentes. Testes
  reais continuam em validadores explícitos, não nos atalhos normais.
- UI: abertura, restauração, escolha e pós-download usam models/select sem warm;
  primeiro envio é a geração normal que carrega principal escolhido. TEMP só
  carrega quando uma ferramenta realmente o utiliza. Voz mantém escolha no início
  da chamada, mas LLM não carrega antes de uma fala/mensagem processada.
- Histórico, substituído por D-011: consultar ps antes de liberar anterior; nenhum pedido de descarga para
  modelo não residente. Preservar locks e trabalho ativo. Modelos já utilizados
  podem permanecer no cache do Ollama; não forçar descarga de terceiros ao abrir.
- Descoberta relacionada: gpt-oss local era classificado como cloud pelo prefixo
  gpt-. Corrigido get_provider/MultiEngine e seleção frontend; instalação local
  agora pode aparecer no inventário sem encaminhamento errado à nuvem.
- Instalação: somente checker externo, backup lazy-startup-20261008T113407.207447Z;
  config, modelos em disco, helper/TCC e cofre preservados.

## D-009 — Retorno visível para downloads personalizados

- Data: 2026-10-08; estado: implementada, regressões e Chrome isolado PASS.
- Origem: nome gpt-oss:20b digitado sem indicação de início/conclusão. Modelo
  já instalado confirmado read-only no Ollama; nenhum download real iniciado por
  esta correção. Screenshot mostrava botão custom estático e desabilitado.
- Decisão: spinner/texto Baixando e Carregando no botão custom, mensagem e erro
  junto ao campo, nome preservado ao falhar. Guard síncrono evita Enter/clique
  duplicados; seleção concorrente bloqueada enquanto download segue.
- Não apresentar percentual: API atual aguarda resposta final stream=False;
  apenas fases conhecidas são mostradas. Não inventar quantidade transferida.
- Backend valida status success/ausência de error e inventário /api/tags antes
  de anunciar instalação; erros HTTP200, JSON/inventário inválido e timeout são
  explícitos. Nome sem tag é comparado também com :latest.
- Download concluído segue carregamento/seleção original; falha no carregamento
  conserva nome e diagnóstico. Não repetir download de gpt-oss já instalado.

## D-008 — Seleção também controla residência e novas chamadas por voz

- Data: 2026-10-08; estado: implementada após relato de RAM alta no4b.
- Fatos: /api/ps inicialmente9b7,10GiB +4b3,83GiB. Troca anterior só carregava
  novo modelo; voz usava default9b e preferência não era persistida.
- Decisão: carregar e selecionar em operação serializada com inferência
  non-stream; sob locks da mailbox/chamada, liberar somente principal anterior
  conhecido quando ocioso. Preservar TEMP, modelos de terceiros e tarefas existentes.
  Tarefa/conversa pendente ou chamada ativa retém modelo anterior; limpeza pode
  ocorrer em nova seleção quando ocioso ou pelo vencimento no Ollama.
- Padrão de novas submissões atualizado sem reescrever modelo de tarefas antigas.
  Preferência salva na interface e restaurada ao abrir pelo launcher.
- Voz: modelo explicitamente escolhido passa por OJ_CALL_MODEL no subprocesso
  até TaskClient/TaskSubmission; não editar runtime.sh/config.toml nem mudar
  chamada em andamento. Troca durante chamada vale para a próxima chamada.
- Alternativa rejeitada: descarregar todos os modelos; interromperia trabalhos
  e eliminaria executor que continua necessário. Residência não prova inferência.
- Evidência real: preload4b retornou unloaded=[qwen3.5:9b], retained=[];
  /api/ps posterior só4b3,68GiB. É memória de modelos informada pelo Ollama,
  não medição de toda RAM do Mac nem de toda alocação do processo.

## D-007 — Modelos instalados selecionáveis e conexão pelo launcher

- Data: 2026-10-08; estado: implementada, regressões e navegador PASS.
- Origem: usuário não conseguia selecionar modelo ou abrir Downloads.
- Causa confirmada: endpoint filtrava para OJ_MAIN_MODEL e construtor business
  substituía modelo explicitamente recebido. Remover filtro; usar variável como
  padrão apenas sem seleção explícita; OJ_TEMP_MODEL permanece independente.
- Carregamento: usar `/v1/models/preload` autenticado no backend configurado,
  em vez de fetch direto do navegador ao Ollama. Confirmar seleção só após
  carregamento bem sucedido, inclusive após download. Erros permanecem no seletor.
- Conexão: Vite com proxy configurado pelo launcher ignora URL loopback antiga
  persistida; URL remota e configuração customizada fora desse modo preservadas.
  Isso evita depender de porta fixa, sem apagar configurações ou chaves.
- DOM: seletor e tela de erro em português, translate=no/notranslate, textos
  alternantes em spans. Tradução automática é hipótese compatível com screenshot,
  não causa comprovada no navegador pessoal. Não interceptar removeChild global.
- Evidência: reprodução RED de lista/seleção, 28 testes locais, 40 frontend,
  build; Chrome isolado listou9b/4b, abriu abas e carregou4b real.

## D-006 — Espaço final para impedir autocomplete na navegação

- Data: 2026-10-07; estado: aprovada explicitamente pelo usuário, implementada.
- Contexto: controle físico funcionou, mas Chrome completou a URL com caminho
  de anúncio visitado e abriu a página errada dentro do mesmo domínio.
- Decisão: digitar `url + ' '` antes de Enter nas navegações; verificar resultado
  contra a URL original, sem espaço, incluindo domínio/caminho/query.
- Origem e exemplo: mensagem do usuário; `mercadolivre.com` → `mercadolivre.com `.
- Motivo: suprimir a sugestão inline do Chrome; testar efeito real em seguida.
- Alternativas: diagnóstico com Escape estava em curso; orientação explícita
  do usuário substitui essa hipótese. Não alterar textos de outros formulários.
- Impacto: alteração Python, sem reconstruir helper nem renovar assinatura/TCC.

## D-003 — Retomar pendências com comprovação real

- Data: 2026-10-07 (America/Sao_Paulo); estado: aprovada pelo pedido do usuário.
- Origem: `PROMPT_MEMORIA.md` e mensagem para resolver problemas pendentes.
- Prioridade: Chrome pessoal, cursor físico, diagnósticos curtos, tarefas que
  preservam o pedido original, interrupção da voz e memória pessoal preservada.
- Motivo: a sessão anterior teve testes simulados, sem provar a experiência final.
- Impacto: testes reais e simulados são registrados separadamente; não declarar
  conclusão da experiência sem eventos e observações reais.

## D-004 — Lançamento nativo pela identidade do aplicativo

- Data: 2026-10-07; estado: implementada e validada pela cadeia real de execução.
- Fato: o usuário confirmou ambas as permissões e mostrou Acessibilidade ativa.
  O status fora sandbox depois confirmou Acessibilidade, mas continuou negando
  Gravação de Tela na cadeia de execução direta do binário.
- Ação: preparar lançamento por LaunchServices com arquivos privados temporários
  de pedido/resposta; verificar TCC nessa mesma cadeia antes de eventos físicos.
- Motivo: testar a identidade do aplicativo autorizado, evitando atribuir
  automaticamente todas as permissões ao binário iniciado por outro processo.
- Alternativa: repetir tentativas físicas não resolveria uma permissão negada.
- Impacto: atualização nativa exige instalação fora da raiz gravável, backup e
  possível reabilitação de permissões após nova assinatura ad hoc.
- Resultado: identidade do próprio app confirmada; versão final com AX1,
  screen=true e posting_events=true executou navegação e clique reais.

## D-005 — Renovar apenas autorização TCC obsoleta do helper

- Data: 2026-10-07; estado: executada após aprovação de escalation.
- Evidência: log TCC restrito ao helper informa requisito de código antigo
  incompatível com hash da versão atual para Acessibilidade. Acesso direto estava
  atribuído ao VS Code; LaunchServices identifica o próprio helper. Permissão de
  tela passou pelo aplicativo, mas Acessibilidade permaneceu negada.
- Ação: `/usr/bin/tccutil reset Accessibility local.openjarvis.maccontrol`,
  sucesso confirmado; abrir aplicativo atual para o usuário habilitar novamente.
- Motivo: eliminar registro antigo incompatível, sem contornar a concessão manual.
- Impacto: somente aprovação de Acessibilidade desse bundle foi removida; outras
  permissões/aplicativos não foram alvo. Concessão manual posterior e resultado
  físico confirmados; segunda instalação exigiu renovação específica também de tela.

## D-001 — Memória documental persistente

- Data: 2026-10-07 (America/Sao_Paulo).
- Estado: aprovada pelo usuário.
- Contexto: outros agentes precisarão recuperar pedidos e razões das decisões.
- Decisão: aplicar o harness indicado e manter os oito arquivos de memória em
  `docs/anotations/`, atualizando-os conforme a conversa e o trabalho evoluírem.
- Motivo: preservar contexto rastreável além da sessão de chat.
- Alternativas: manter contexto apenas no chat não atende ao pedido; transcrição
  integral não é o formato indicado pelo harness. Não houve debate de outras
  alternativas com o usuário.
- Impacto: documentação faz parte de cada entrega; fatos e evidências precisam
  ser separados de propostas, suposições e pendências.
- Exemplo de aplicação: ao decidir uma alteração, registrar data, origem, motivo,
  escopo, critério de aceite e depois a evidência de validação.

## D-002 — Aplicação às capacidades reais da sessão

- Data: 2026-10-07 (America/Sao_Paulo).
- Estado: adaptação operacional registrada; não é escolha de modelo aprovada.
- Contexto: o harness solicita `gpt-5.6-terra` e esforço `medium`; o modelo
  solicitado não aparece entre os modelos disponíveis para subagentes.
- Ação: usar o modelo herdado da sessão e declarar a limitação. Não afirmar
  que houve troca de modelo ou de esforço. Usar subagentes para leitura e
  verificação independente, conforme a instrução explícita do harness.
- Motivo: executar apenas capacidades efetivamente disponíveis.
- Impacto: o método é aplicável; a configuração exata solicitada não é garantida.
