# Continuidade do projeto OpenJarvis local

Você vai assumir um projeto existente de OpenJarvis local em um MacBook Air. Trabalhe como orquestrador, delegando investigação, implementação e revisão a subagentes. Entregue um sistema funcionando de ponta a ponta, com evidências reais de execução.

## Contexto e objetivo

O usuário é JP, fala português brasileiro e quer um assistente pessoal local, utilizável por uma pessoa comum através de uma interface e chamadas por voz.

Hardware informado na sessão anterior (confirme no ambiente):
- MacBook Air com Apple M5.
- 24 GB de memória unificada.
- macOS 26.6.2.

Repositório oficial: https://github.com/open-jarvis/OpenJarvis.git

Instalação existente:
- Projeto raiz: /Users/JP/OpenJarvis
- Configurações, scripts e dados locais: /Users/JP/OpenJarvis-local
- Atalhos .command: /Users/JP/Desktop
- Componente de controle: /Users/JP/Applications/JarvisMacControl.app

Não reinstale tudo nem descarte alterações existentes. Inspecione código, configurações, git diff e logs antes de modificar. Preserve mudanças locais e dados pessoais.

## Experiência final desejada

O usuário abre a interface, inicia uma chamada e conversa naturalmente.

Exemplo:
Usuário: “Bom dia!”
Jarvis responde diretamente, de forma natural, sem criar uma tarefa.

Usuário: “Abra o Mercado Livre.”
Jarvis responde rapidamente “Vou abrir para você”, delega a execução e realmente abre o site no Chrome pessoal, visível na tela do usuário.

O assistente deve:
- Conversar em português brasileiro.
- Responder rapidamente a conversas simples.
- Delegar tarefas demoradas e continuar disponível para conversar.
- Aceitar interrupções durante a fala.
- Manter tarefas em execução quando o usuário mudar de assunto.
- Adicionar novos pedidos à fila.
- Redirecionar uma tarefa quando o usuário complementar ou corrigir seu objetivo.
- Relatar progresso e resultados com base no que realmente aconteceu.
- Criar arquivos reais, como planilhas .xlsx, e abri-los quando solicitado.
- Utilizar a sessão pessoal do Chrome quando necessário.
- Aprender preferências e contexto pessoal através de memória persistente no Obsidian.

Quem decide entre responder, delegar, redirecionar e cancelar é a IA. Não implemente roteamento por listas de palavras como “bom dia”, “obrigado” ou “abra”. O código valida argumentos, estados e permissões técnicas, mas não substitui o raciocínio da IA por classificação de frases.

## Autorização

Um pedido explícito como “abra o Mercado Livre” já autoriza os passos necessários para essa tarefa. O usuário não quer uma segunda pergunta para abrir ou reutilizar o navegador.

Permissões obrigatórias do macOS, como Acessibilidade e Gravação de Tela, precisam estar corretamente concedidas ao processo que realiza o controle. Não tente contornar as proteções do macOS. Descubra exatamente qual aplicativo/processo precisa da permissão e forneça instruções precisas quando uma ação manual for inevitável.

Autorização para navegar não equivale a autorização genérica para compras, pagamentos, exclusões ou envios.

## Arquitetura dos agentes do Jarvis

Principal:
- Conversa com o usuário.
- Decide se responde diretamente ou pede ajuda.
- Mantém a conversa disponível durante as tarefas.

SUBAGENT_MAIN:
- Mantém objetivo, plano e resumo dos resultados.
- Realiza raciocínio e coordena o trabalho.
- Consulta memória persistente quando necessário.
- Delega passos concretos ao executor temporário.
- Confere cada resultado antes de continuar.

SUBAGENT_TEMP:
- Controla o computador em passos curtos.
- Recebe somente a instrução atual, dados necessários e observação atual da tela.
- Não recebe todo o histórico nem toda a memória pessoal.
- Retorna evidência do que executou.
- Seu contexto lógico é descartado após cada execução.
- Não é necessário encerrar o processo do modelo Ollama a cada passo.

Evite contextos enormes sem perder informações necessárias para executar corretamente.

## Modelos e voz

Configuração preparada:
- Principal e agentes de raciocínio: qwen3.5:9b.
- Executor temporário: qwen3.5:4b.
- Ollama local: 127.0.0.1:11434.
- OLLAMA_MAX_LOADED_MODELS=2.
- OLLAMA_NUM_PARALLEL=1.
- Contexto principal: 8192 tokens.
- TEMP: 4096 sem imagem; 8192 com imagem.

Logs reais confirmaram ambos carregados: uma execução mostrou 10,8 GiB; após aumentar o contexto TEMP, outra mostrou 13,9 GiB. Esses números são dos modelos, não do consumo total do Mac.

Transcrição preparada: Whisper small, CPU int8, português.

Síntese preparada: Kokoro ONNX local, voz pf_dora, velocidade 1,5, processo persistente. Há um ambiente .venv-voz; confirme seu caminho real em vez de presumir a localização.

Existe implementação de interrupção de áudio e captura contínua, mas não há comprovação de cancelamento de eco completo. Verifique o comportamento real antes de afirmar que equivale ao ChatGPT.

## Arquivos importantes

Leia pelo menos:
- /Users/JP/OpenJarvis-local/config.toml
- /Users/JP/OpenJarvis-local/runtime.sh
- /Users/JP/OpenJarvis-local/abrir_interface.py
- /Users/JP/OpenJarvis-local/preparar_modelos.py
- /Users/JP/OpenJarvis-local/chamada_continua.py
- /Users/JP/OpenJarvis-local/HARNESS-NEGOCIOS.txt
- /Users/JP/OpenJarvis-local/mac-control/control.m
- /Users/JP/OpenJarvis/src/openjarvis/agents/business.py
- /Users/JP/OpenJarvis/src/openjarvis/agents/task_runtime.py
- /Users/JP/OpenJarvis/src/openjarvis/agents/obsidian_memory.py
- /Users/JP/OpenJarvis/src/openjarvis/tools/mac_desktop.py
- /Users/JP/OpenJarvis/src/openjarvis/tools/spreadsheet_local.py
- /Users/JP/OpenJarvis/src/openjarvis/engine/ollama.py
- /Users/JP/OpenJarvis/src/openjarvis/engine/multi.py
- /Users/JP/OpenJarvis/src/openjarvis/cli/serve.py
- /Users/JP/OpenJarvis/src/openjarvis/server/routes.py

Confirme caminhos existentes; este documento não substitui a inspeção.

## Alterações já feitas

### 1. Roteamento pela IA

O principal retorna decisões estruturadas: reply, delegate, redirect, cancel e end_call.

Há código legado para solicitar/aprovar autorização do navegador, mas essas ações foram removidas do esquema atual de decisão, pois o pedido explícito já autoriza o uso.

Há validação e uma tentativa de reparo de resposta inválida, sem fallback por palavras-chave para decidir tarefas.

### 2. Tarefas em segundo plano

TaskManager separa conversa e execução pesada. Há fila, progresso, cancelamento e redirecionamento com revisão. Interrupções são cooperativas; não interrompem necessariamente uma requisição HTTP ao modelo em andamento.

### 3. Correção do engine

A descoberta de engines encaminhava o modelo para um suposto vLLM em localhost:8000, produzindo HTTP 500. Foi fixada a preferência pelo Ollama explicitamente selecionado. Ollama recebe o JSON Schema real e utiliza think=false nas chamadas pertinentes.

### 4. Seleção dos modelos

BusinessAgent usa OJ_MAIN_MODEL para o principal e OJ_TEMP_MODEL para ComputerStepTool. A interface foi ajustada para selecionar o principal. O launcher lê o modelo do config.toml.

### 5. Preparação automática

preparar_modelos.py baixa modelos ausentes, verifica residência dos dois, pode reiniciar um listener identificado como Ollama quando necessário, testa decisões reais do principal e navegação com computador simulado. Salva relatório em modelos-validados.json.

O teste de navegação foi corrigido para aceitar URLs equivalentes com ou sem “/” final e mostrar a ação recebida em caso de erro. Esses testes simulados NÃO comprovam controle real do Mac.

### 6. Memória no Obsidian

Fonte principal: /Users/JP/OpenJarvis-local/Obsidian Jarvis

Arquivos Markdown, propriedades e wikilinks representam usuário, declarações e temas. A leitura consulta os arquivos; Obsidian não precisa ficar aberto. Sua interface serve para visualizar/editar o grafo.

SQLite anterior foi preservado e houve migração de quatro declarações na sessão anterior. Preserve cofre e backups. Confirme o estado do aplicativo Obsidian; sua instalação não foi comprovada naquela sessão.

A memória registra declarações pessoais explícitas. Não treina pesos dos modelos nem transforma suposições em fatos.

### 7. Planilhas reais

SpreadsheetCreateTool gera .xlsx em /Users/JP/OpenJarvis-local/arquivos, com colunas, linhas e valores numéricos, evita sobrescrita e pode abrir o arquivo. Existe exemplo com SKU, PRODUTO e CUSTO.

### 8. Controle real do Mac

Python chama JarvisMacControl.app, cuja fonte Objective-C é OpenJarvis-local/mac-control/control.m.

Utiliza Acessibilidade para elementos/coordenadas, CGEvent para mouse/teclado reais, captura de tela enviada ao modelo local no campo images, imagem reduzida até 1280 pixels, conversão entre pixels e pontos globais e limitação de cliques à janela observada.

Aplicativos previstos: Chrome, Numbers, Excel e Finder. Captura preparada para monitor principal.

Compilado com /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk e assinado ad hoc com identificador local.openjarvis.maccontrol.

Investigue se reconstruir/reassinar o aplicativo invalidou ou alterou sua autorização em Acessibilidade/Gravação de Tela.

### 9. Mouse visível

Movimento gradual do cursor: aproximadamente 0,6 segundo até o destino, com CGWarpMouseCursorPosition e CGEvent, e pausa curta antes do clique.

Fluxo de navegação:
- Tenta abrir Chrome clicando no Dock; sem ícone, usa Spotlight.
- Seleciona e ativa a janela pessoal.
- Localiza botão de nova guia pelos elementos AX e clica.
- Se não localizar o botão, usa Cmd+T.
- Localiza barra de endereço pelos elementos AX e clica nas coordenadas.
- Usa Cmd+A, digita URL e pressiona Enter.
- Confere domínio da URL observada.

Se não identificar a barra, retorna erro em vez de inventar coordenadas.

Teste direto, sem LLM:
- /Users/JP/OpenJarvis-local/testar_mouse.py
- /Users/JP/Desktop/Testar Mouse Jarvis.command

### 10. Evitar navegador invisível

Quando OJ_DESKTOP_CONTROL=1, BusinessAgent deve disponibilizar controle nativo mesmo fora da chamada e evitar ferramentas de navegador separado. Verifique voz, chat comum, especialistas e testes.

## Problema atual — prioridade

O objetivo do usuário ainda NÃO foi alcançado.

Última conversa real:
Usuário: “Abra o mercado livre.”
Jarvis: “Vou abrir o Mercado Livre no navegador.”
Depois informou que computer_step falhou quatro vezes porque Acessibilidade para JarvisMacControl não estava habilitada.

O usuário relata que o comportamento continua errado e quer ver seu mouse real controlando o Chrome pessoal.

A última fala transcrita foi “e conseguiu abrir”, mas não é confirmação inequívoca de sucesso. Investigue sem presumir que abriu corretamente.

O diagnóstico aponta para Acessibilidade. Não trate isso como causa única comprovada de todos os problemas: investigue caminhos de execução, identidade do componente, seleção da janela, reconhecimento dos controles e verificação do resultado.

A resposta de voz sobre a falha foi longa e técnica demais. Explique brevemente o bloqueio e deixe detalhes na interface/log.

## Como investigar

Organize subagentes, por exemplo:
- Controle macOS, permissões TCC, assinatura e identidade do processo.
- Orquestração, decisões da IA, ferramentas e tratamento de falhas.
- Voz, interrupções, latência e apresentação dos resultados.
- Revisão independente e validação integrada.

Investigue a cadeia completa:
pedido → decisão → tarefa → ferramenta → processo nativo → evento físico → observação → resultado.

Determine:
- Qual processo efetivamente move o cursor.
- Se esse mesmo processo está autorizado pelo macOS.
- Se a permissão sobrevive a atualizações.
- Se Chrome fica visível e em primeiro plano.
- Se a janela AX corresponde à janela selecionada.
- Se coordenadas correspondem ao monitor e escala corretos.
- Se o cursor chega ao destino.
- Se a ferramenta retorna evidência suficiente.
- Se o agente distingue tentativa, execução e conclusão.
- Se quatro tentativas repetem inutilmente um erro de permissão.

Não repita ações quando nenhuma tentativa puder resolver o bloqueio.

## Limitações da sessão anterior

O ambiente de ferramentas não conseguia acessar Ollama em localhost nem controlar a sessão gráfica do usuário. Também havia restrições de rede.

Os testes eram principalmente simulados; o usuário executava atalhos na sessão real. Não foi validado visualmente o mouse nem comprovadas permissões do componente correto.

Verifique capacidades desta nova sessão. Se a limitação persistir, prepare diagnósticos concretos para o usuário executar, sem afirmar que testou o que não conseguiu testar.

## Validação necessária

A sessão anterior terminou com 70 testes locais passando; depois houve pequena alteração para disponibilizar DesktopSessions no chat comum, com dois testes de seleção de modelos passando. Isso não comprova a experiência final.

Critérios reais de aceitação:
1. “Bom dia” recebe resposta natural, sem tarefa.
2. “Abra o Mercado Livre” recebe confirmação rápida, sem segunda autorização.
3. Chrome pessoal aparece na tela.
4. O usuário vê cursor mover e clicar em controle identificado.
5. Site solicitado abre na guia correta.
6. Pedido seguinte consegue clicar e navegar na página.
7. Cada ação é conferida pela observação seguinte.
8. Permissão ausente produz diagnóstico curto/correto, sem tentativas inúteis.
9. Usuário pode interromper fala e conversar enquanto tarefa continua.
10. Complemento redireciona a tarefa correta.
11. Memória Obsidian permanece preservada.
12. Planilha solicitada vira arquivo .xlsx real.

## Entrega esperada

Entregue correções implementadas/revisadas, inicialização simples pelos atalhos, diagnóstico confiável de permissões, logs/resultados úteis, instruções curtas para passos manuais inevitáveis e separação clara entre simulação e validação real.

Explique objetivamente o que funciona, o que foi confirmado e o que permanece pendente.

O usuário está frustrado com repetidas afirmações de que ficou pronto seguidas de falhas. Priorize comprovar funcionamento. Não declare sucesso apenas porque compilou ou testes simulados passaram.

Fale em português brasileiro.
