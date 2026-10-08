# Memória durável do projeto

Atualização2026-10-08: auditoria R-025 somente documental em [auditoria/2026-10-08](../auditoria/2026-10-08/README.md); evidências atuais prevalecem sobre suposições de integração/recuperação em notas históricas. Nenhum redesenho implementado.

Atualização2026-10-08: execução observável R-022/023/024/D-013, histórico de etapas com duração e modoaltofalante/fones. Consulte validation/worklog para PASS e falhas reais; números32s não significam tarefa instantânea. Eventos locais sanitizados em logs/task-events.jsonl do runtime.

Atualização 2026-10-08: política vigente de RAM em D-011/R-020: carregar sob demanda e manter cache por cinco minutos após uso. Notas históricas de descarga imediata na seleção foram substituídas; evicção por pressão de memória é limitação confirmada. Evidências na validation.md.

Inicializada em 2026-10-07 (America/Sao_Paulo) por solicitação do usuário.

Esta pasta registra o contexto útil das conversas para outros agentes: pedidos,
decisões, motivos, planos, exemplos relevantes e evidências. Não é uma transcrição
integral nem contém segredos ou raciocínio interno.

## Regra de leitura e atualização

Antes de planejar, leia este índice e os arquivos pertinentes. Reconcilie as
notas com a instrução mais recente do usuário e o código verificável. Atualize a
memória quando houver informação relevante e antes de encerrar a resposta ou
iniciar a próxima implementação. Distinga fatos, propostas e questões abertas.

Fontes de verdade: instruções aplicáveis da sessão, pedidos explícitos do usuário,
[harness](../prompts/PROMPT_HARNESS_CODEX.md), código e documentação do repositório.
O harness é uma orientação de trabalho fornecida pelo usuário; não substitui as
instruções de maior prioridade nem altera o modelo efetivamente disponível.

## Índice

- [Contexto](project-context.md): objetivo, arquitetura e restrições confirmadas.
- [Preferências](user-preferences.md): orientações explícitas do usuário.
- [Decisões](decisions.md): data, contexto, motivo, alternativas e impacto.
- [Requisitos e backlog](requirements-and-backlog.md): escopo e critérios de aceite.
- [Registro de trabalho](worklog.md): ciclos, arquivos, papéis e resultados.
- [Validação](validation.md): critérios e evidências concretas.
- [Riscos e questões abertas](risks-open-questions.md): limitações e pendências.
