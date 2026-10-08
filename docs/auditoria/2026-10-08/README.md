# Auditoria técnica OpenJarvis — 2026-10-08

Estado: CONCLUÍDO — gate documental final independente PASS. Escopo exclusivo de investigação solicitado pelo usuário. Nenhum código/configuração/dependência ou estado operacional foi alterado. Alterações de produto anteriores à auditoria foram preservadas, inclusive arquivos não rastreados. A árvore de trabalho, e não somente o HEAD, é a referência.

## Relatórios

1. [Arquitetura atual](01-ARQUITETURA-ATUAL.md)
2. [Harness e loops](02-HARNESS-E-LOOPS.md)
3. [Computer Use e macOS](03-COMPUTER-USE-MACOS.md)
4. [Modelos, contexto e tokens](04-MODELOS-CONTEXTO-E-TOKENS.md)
5. [Agentes e memória](05-AGENTES-E-MEMORIA.md)
6. [Falhas e riscos](06-FALHAS-E-RISCOS.md)
7. [Testes e observabilidade](07-TESTES-E-OBSERVABILIDADE.md)
8. [Resumo para redesenho](08-RESUMO-PARA-REDESENHO.md)

[Índice de35evidências](EVIDENCIAS.md): caminhos relativos, símbolos, linhas, dependências e complemento AST. Classificações: CONFIRMADO=código/evento comprovado; INFERIDO=conclusão fundamentada; NÃO ENCONTRADO=ausência na fatia pesquisada; NÃO VERIFICADO=exige runtime/dados/configuração fora do escopo. Ausência localizada não é prova de ausência em todo o projeto.

## Cobertura dos18itens do pedido

| Item | Cobertura | Evidências principais |
|---|---|---|
|1 Contexto/objetivo generalista |01,03,08; distingue atual/desejado |E07,E13,E28 |
|2 Regras/evidências/privacidade |Todos, índice e este registro |E01–E35 |
|3 Repositório/stack/startup |01 |E01–E03,E28–E31 |
|4 Fluxo/harness/diagrama |02,08 |E04–E11 |
|5 Loop/limites/pseudocódigo |02,04,06 |E06–E09,E32 |
|6 Executor/macOS/window_changed |03,06 |E12–E16,E26 |
|7 Navegador/abas/sessão/races |03,06 |E14,E17 |
|8 Engines/seleção/contexto/tokens |04 |E25,E27,E29–E30 |
|9 Especialistas/contextos/conflitos |02,05 |E07,E08,E13 |
|10 Memória/graph/procedimento |05 |E18–E24,E28 |
|11 Observabilidade/traces |07 |E06,E24,E26,E30,E32 |
|12 Caso102s/perguntas1–8 |06 |Journal estrutural+E07,E13–E15 |
|13 Segurança/isolamento |03,06,07 |E12–E15,E32–E34 |
|14 Testes/evals/coverage/replay |07 |E35; cobertura operacional não verificada |
|15 Problemas P0–P3 |06:15achados, sem preencher severidades artificialmente |F01–F15/E06–E35 |
|16 Oito entregáveis/resumo<=1500palavras |01–08, índice |08:1039palavras na checagem atual |
|17 Revisores reais/final |Registro abaixo |A–E+validaçãofinal |
|18 Encerramento/gates |Este registro+08 |Condições mapeadas, lacunas explícitas |

## Revisões independentes realizadas

Os revisores são subagentes reais, somente leitura; o orquestrador é o único escritor de documentação. Nenhum modelo/GUI/instalação/teste de produto foi executado por eles nesta etapa.

| Papel | Agente real | Evidência própria/conclusão |
|---|---|---|
|A Arquitetura e loops |task_failures |Python HTTP/mailbox, limites, cancel/redirect, loops Rust e guard; implementação confirmada, processos não verificados |
|B Desktop/macOS |mac_diagnosis |Objective-C/AX/AppleScript e journal whitelisted102s/12calls/11falhas; subcausa/correlação não verificada |
|C Inferência |memory_review |Engines/parâmetros/contexto/tokens/seleção/contratos PythonvsRust; estado resident não consultado |
|D Memória/aprendizagem |voice_review |Obsidian/SQLite/vector/skills/checkpoint e gap de integração Business |
|E Segurança/testes/traces |memory_review, segunda tarefa de revisão |Capabilities/injection/confirmation/timeout/auth/trace; evidências próprias, sem execução ofensiva |
|Final, todos os relatórios contra fonte/pedido |task_failures |PASS:18itens, links/ranges, símbolos AST, JSON,08<1500; correções documentais conferidas |
|Final especializada03/06/08 |mac_diagnosis |PASS técnico com ajuste de nomenclatura MAIN; divergência keepalive confrontada com árvore atual |
|Final especializada05/06/08 |voice_review |PASS técnico com correção de responsabilidade de escrita TOML |

A–E são cinco papéis, exercidos por quatro subagentes distintos; C/E usaram a mesma instância em tarefas separadas. Não alegar cinco instâncias independentes. Revisor final A é independente do autor dos relatórios.

## Correções documentais feitas no gate

- Guard padrão é criado pela classe-base ToolUsingAgent; omitir configuração explícita no Business não significa ausência de guard/compressão.
- Journal não persiste session; há um `.previous.jsonl`, dois arquivos no total.
- Exemplo JSON foi validado com parser; não é um prompt pessoal capturado.
- Redirect tem máximo20complementos/tarefa; ausência de orçamento agregado não significa redirecionamentos ilimitados.
- Especialista SUBAGENT_MAIN escolhe passo; principal conversacional delega objetivo.
- SkillDiscovery retorna candidatos; SkillManager escreve TOML.
- keep_alive5m está explícito nos três payloads Ollama Python da árvore atual (163/287/387); comparar somente HEAD produziria conclusão incorreta.
- Intervalos de quatro arquivos no índice foram corrigidos conforme comprimento real; AST complementa símbolos centrais.

## Verificação e limites

Checagem por SHA-256 do baseline de2122 arquivos de produto/testes: zero alterações e zero novos arquivos de produto na comparação realizada. Só relatórios e memória documental escritos. Validação de links/ranges/JSON/limite08 e gate final independente: PASS. Revisor final task_failures não encontrou falha documental material remanescente.

Não foram rodadas suítes de produto nesta auditoria: escopo de leitura e ausência de necessidade de tocar runtime. Resultados históricos permanecem em docs/anotations/validation.md. Não inventar porcentagem de cobertura nem sucesso real de4Bvs9B. A análise do102s usa eventos estruturais, sem abrir cofre/conta ou anexar logs brutos. Dados faltantes e reproduções futuras seguras constam em06/07. Nenhum redesenho foi implementado.

Fingerprint SHA-256 do mapa ordenado de2122paths/hashes baseline: `c65297d0d0ec67f47d3323b6fb8a682913c6828ea7507b0355556cae56ab5c07`. Nova comparação final:2122preservados, zeroarquivosproduto novos. Esta prova cobre arquivos do workspace, não estado de processo/RAM/dados externos.
