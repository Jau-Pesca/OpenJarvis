# 06 — Falhas, segurança e riscos

Data:2026-10-08. [Índice de evidências](EVIDENCIAS.md). Diagnósticos de código são separados de ocorrências reais. Nenhuma correção de produto foi realizada. Prioridade considera efeito potencial e caminho de execução, não comprovação de incidente malicioso.

## Caso de referência: Central de Vendedores, aproximadamente102s

Relato fornecido: site já aberto → nova aba → navegação/clique → “Janela mudou durante a etapa” → repetições → sem confirmação. **CONFIRMADO no journal estrutural local:** uma tarefa com duração registrada102,0s,12 chamadas computer_step,11 erros window_changed. ID integral foi omitido da publicação; chave de correlação local começa `d851`. Fonte externa: `/Users/JP/OpenJarvis-local/logs/task-events.jsonl`, leitura somente de campos whitelisted de E06. **NÃO VERIFICADO:** correlação com este pedido específico, URL/menu, janela/aba e objetivo de cada chamada; o journal sanitizado não os contém.

| Pergunta do pedido | Diagnóstico e certeza | Evidência |
|---|---|---|
| Por que nova guia? | CONFIRMADO: navigate abre nova guia; INFERIDO: modelo escolheu navigate em vez de explorar aba existente | E14 act:272–316; argumentos do incidente ausentes |
| Por que mudou após clique? | INFERIDO: título/transição, popup/foco, bounds ou AX/AppleScript em instantes diferentes | E14 chrome_view e E15 guard; subcausa NÃO VERIFICADA |
| Por que virou erro? | CONFIRMADO: comparações de título/bounds/correspondência geram exceção; ferramenta agrupa prefixos | E13 execute:388–390; E14:181–210; E15:143–149 |
| Por que repetiu? | CONFIRMADO: código window_changed não é terminal; loop continua até limite; trace tem11 falhas | E07:123–136, E08, E13:386–390 |
| Por que não mudou estratégia? | CONFIRMADO: não há regra determinística de recuperação para esse código; escolha cabe à IA. Motivo específico da escolha NÃO VERIFICADO | E07,E08; journal não guarda decisão/prompt |
| Por que mais inferência? | CONFIRMADO: especialista precisa gerar próxima chamada; TEMP só quando observação inicial passa | E08,E13. Dez falhas do trace anteriores ao TEMP |
| Por que sem conclusão? | CONFIRMADO: novo observe pode invalidar recibo; exige alguma ação e revisão. Estado de negócio específico NÃO VERIFICADO | E07:611–664,E13:377–390 |
| Por que resposta final também pode falhar? | INFERIDO: backend/timeout/parse/síntese opcional podem falhar; NÃO VERIFICADO nesse ID | E07:645–668,E25; faltam eventos completos correlacionados dessa fase |

Primeira falha registrada durou8,526s: fase de click terminou após1,824s, erro em `Conferindo resultado na tela`. As dez seguintes duraram2,447–2,543s e falharam em `Localizando janela e observando tela`, antes de nova inferência TEMP. **Não são11 cliques fracassados:** houve uma ação retornada antes de erro posterior e repetição de localização. Nenhuma evidência comprova que o modelo foi a única origem da lentidão; efeitos parciais e polling/guard são relevantes.

Para fechar diagnóstico: comparar títulos/bounds esperados/observados com motivo específico, PID/windowID/aba antes-depois, tipo da ação sem dados sensíveis, ponto onde houve efeito e resultado parcial, eventos de navegação/popup e tempo de inferência por chamada. Coletar futuramente em página de teste, redigindo títulos/URLs/screenshots se pessoais. Não ampliar logs de contas reais nem registrar prompts/credenciais indiscriminadamente.

## Quinze problemas prioritários

Cada item informa componente, causa, impacto, condição de reprodução e direção geral. “Reprodução” descreve cenário a testar futuramente; não declara execução feita nesta auditoria.

### F01 — P0 — Piso de autorização perdido nos wrappers Business

**CONFIRMADO/alta confiança.** Componente `_GuardedTool` + canonical capabilities. Wrapper tem origem agents.business; computer_step/spreadsheet_create não constam do mapa canônico e specs não exigem capabilities; retorna lista vazia e política configurada não faz check desses nomes. E33:business110–117/584–588,capabilities294–334,executor330–345. Impacto: execução pode ocorrer apesar de intenção deny da política. Reprodução: policy default-deny + ferramenta wrapped em teste com executor nativo stub; nenhuma ação real necessária. Direção: preservar identidade/requisitos de autorização ao atravessar wrappers. Não confirmado abuso ou configuração deny no runtime atual.

### F02 — P0 — Ação sensível sem gate obrigatório por significado

**CONFIRMADO/alta sobre ausência de gate; ocorrência indevida NÃO VERIFICADA.** computer_step spec não exige confirmação; `_allow_tool` só progresso/cancelamento; prompt TEMP orienta não concluir compras/publicações/envios sem autorização específica, mas click/type/key não classificam isso. E13:324–361,E07:506–512,E32:401–417. Impacto potencial: uma escolha errada em sessão autenticada pode finalizar ação sensível. Reprodução segura: checkout fictício que registre intenção sem compra; avaliar autorização omitida. Direção: autorização explícita verificável em operações sensíveis, preservando controle físico atual.

### F03 — P1 — Falha de janela repetida sem política de recuperação

**CONFIRMADO/alta.** E13:386–390,E14:181–204,E07:118–137,E08. Erro não terminal e sem contador específico; especialista insiste. Journal102s confirma padrão, não subcausa. Impacto: latência/inferências sem progresso. Reprodução: stub observe sempre window_changed, verificar decisões repetidas/turnos. Direção: recuperação baseada no tipo/estado da falha e orçamento explícito de repetição.

### F04 — P1 — Correlação de janela rejeita transição legítima e confunde efeito parcial

**CONFIRMADO mecanismo/INFERIDO subcausas, confiança alta/média.** E14:181–210,E15:143–149,E13:377–390. Guard rígido e observe pós-ação podem marcar chamada inteira como erro após click executado. Impacto: repetir clique ou não reconhecer navegação. Reprodução: página fictícia altera título/popup após clique com trace do before/after. Direção: distinguir identidade, transição esperada e pós-condição; preservar proteção contra alvo errado.

### F05 — P1 — Scanner não examina conteúdo externo observado pelo desktop

**CONFIRMADO/alta.** computer_step.is_localTrue é preservado pelo wrapper; scanner só atua em tool não-local. AX/screenshot alimentam modelo sem scanner dessa saída. E33/E34:mac_desktop324–326,350–361,business110–112,executor491–500. Impacto: conteúdo web pode induzir ações apesar da instrução “observação”. Reprodução: página de teste com texto adversarial e modelo stub; sem conta real. Direção: tratar origem do conteúdo separadamente do local onde executa a ferramenta. Eficácia de um ataque real NÃO VERIFICADA.

### F06 — P1 — Timeout/cancelamento não asseguram interrupção física imediata

**CONFIRMADO/alta.** E06:27–65,E32:434–469. Future.cancel não encerra função iniciada; controle só checado em fronteiras; inferência em curso segue. Impacto: UI pode dizer erro/cancelado enquanto trabalho iniciado ainda produz efeitos. Reprodução: ferramenta stub bloqueada liberada após timeout, registrar efeito inofensivo. Direção: definir garantias de interrupção e término de efeito; não alegar emergency stop instantâneo.

### F07 — P1 — Conclusão não tem pós-condição objetiva universal

**CONFIRMADO/alta.** E07:611–664: qualquer recibo elegível (inclusive move) satisfaz gate; revisor IA decide suficiência com recortes; replyFalse também sem prova semântica. Impacto: sucesso/alegação falsa ou objetivo não cumprido. Reprodução: move bem-sucedido sem navegação e revisão permissiva stub. Direção: evidências adequadas ao objetivo e separar execução parcial de conclusão comprovada.

### F08 — P1 — Procedimento bem-sucedido não é aprendido pelo fluxo Business

**CONFIRMADO/alta no wiring.** E07:_tools279–315/_run547–582,E18,E22–E24. Guarda declaração do usuário, não ações/condições; skills existem, mas não compõem esse fluxo. Impacto: refazer exploração amanhã e gastar inferência. Reprodução estática/integrada futura: duas tarefas iguais em ambiente fictício, conferir ausência de receita recuperada. Direção: conectar experiência verificável à recuperação/executor, sem substituir toda plataforma.

### F09 — P1 — Sem orçamento global de tarefa; várias camadas de inferência

**CONFIRMADO/alta sobre limites locais, NÃO ENCONTRADO orçamento agregado.** E06–E08,E13,E25. Turnos limitados não limitam número de tools por geração nem fornecem orçamento agregado para redirects (máximo20 complementos por tarefa); timeout backend até1800s. Impacto: tarefa simples lenta, custo difícil de prever. Reprodução: stub várias tools/turno ou backend lento, sem GUI. Direção: medir e controlar orçamento fim a fim e separar planejamento de primitivas determinísticas.

### F10 — P1 — Redirecionamento reinicia trabalho sem checkpoint/idempotência

**CONFIRMADO reinício/INFERIDO duplicação, alta/média.** E06:238–251,349–404,E07:579–610. Revisão protege publicação velha, não efeitos anteriores. Impacto: repetir write/click; retomada não é cursor. Reprodução: tool stub registra escrita única e redirect entre etapas. Direção: checkpoints/recibos úteis e política de repetição de efeitos.

### F11 — P1 — Journal não reconstitui execução nem recupera fila após restart

**CONFIRMADO/alta.** E06:97–114,285–323. Eventos sem argumentos/resultado/pedido; TaskManager reinicia vazio. Impacto: perder contexto operacional e incapacidade de fechar causa de102s. Reprodução: manager com tarefa fictícia→novo manager→eventos presentes/fila vazia. Direção: persistência e diagnóstico proporcionais, sem sacrificar privacidade por dump integral.

### F12 — P2 — Proteção de repetição varia e fallback avisa indefinidamente por contador

**CONFIRMADO/alta na implementação, ativação local NÃO VERIFICADA.** E09:86–107,E08:171–229,E11. Motivo variável vira chave nova; structured não chama check_call; Rust/fallback diferem. Business não injeta configuração explícita; ToolUsingAgent cria automaticamente o guard padrão habilitado (`agents/_stubs.py:462–474`). Impacto: comportamento divergente/manutenção frágil. Reprodução: checks idênticos4,5,6 com warn_before_block; testar structured/Rust separadamente. Direção: contrato consistente entre modos/backends e testes de progresso.

### F13 — P2 — Lease sem identidade de aba e confirmação rígida de URL

**CONFIRMADO/alta.** E14:117–169,272–316. Nova guia padrão, sem ID estável; aceita host/path/query iguais, redirects distintos falham; não prova page-ready. Impacto: aba duplicada, falso erro, fluxo desconhecido frágil. Reprodução: site de teste com redirect/popup/fechamento. Direção: preservar sessão com identidade e estado de navegação observáveis.

### F14 — P2 — Evidência para revisão incompleta e memória genérica filtrada

**CONFIRMADO/alta.** E07:268–276,609–617,E04:171–211,E06:157,E18. Revisor recorta resultados; system facts/documentos injetados não chegam ao `_converse`; recall lexical não resolve conflitos. Impacto: perda de informação/validação rasa. Reprodução: quinto resultado essencial ou fact exclusivo system com principalstub. Direção: contratos explícitos de evidência/memória entre camadas.

### F15 — P2 — Traces opcionais podem conter dados que o journal omite

**CONFIRMADO/alta sobre payload, dados efetivamente persistidos NÃO VERIFICADOS.** E24,E32,E34:executor426–429/473/528–546,collector160–204. Arguments/resultados integrais são publicados/coletáveis; nenhum redator obrigatório encontrado nessa fatia. Impacto: exposição de conteúdo sensível em traces configuradas. Reprodução: sentinela fictícia em ferramenta, inspecionar armazenamento temporário. Direção: sanitização/proveniência/retention consistente por canal.

## Outras observações, sem inflar ranking

**CONFIRMADO:** setup de scanners e middleware auth captura falhas e continua (E34); scan streaming ocorre depois da entrega; Orchestrator Rust tem só uma chamada; skills mineradas têm arguments_template vazio. **INFERIDO:** corrida entre dois message concorrentes (dois locks separados) e reinício TaskInterrupted sem revisão nova. Ativação/incidente não comprovados. Preservar componentes úteis em08; nenhum P3 foi inventado apenas para preencher lista.

## Controles existentes e alcance

TCC macOS/AX/captura/eventos, leases, allowed-app/action/bounds, SSRF em navigate, workspace de arquivos, rate limiter/capability policy e confirmação genérica quando ToolSpec exige são controles reais. APIs de tarefas/voz restringem loopback+Origin; serve recusa bind externo sem chave; autenticação global é opcional. Não há shell arbitrário na lista efetiva Business, embora plataforma ofereça ferramentas de comandos e sandbox. Cookies permanecem no Chrome/perfil; cofre e secrets não foram lidos. Lock serializa processo, não isola dados/desktop entre usuários. E07,E12–E17,E32–E34.
