# 05 — Agentes, memória e aprendizagem

Data:2026-10-08. Evidências E05,E07,E18–E24,E28 em [EVIDENCIAS.md](EVIDENCIAS.md). Não foram lidos cofre pessoal, notas de usuário, cookies ou registros brutos de bancos.

## Especialistas e comunicação

**CONFIRMADO:** planner escolhe1–3 papéis definidos em `_ROLES`: pesquisa/vendas/fiscal/operacoes. Business cria novas instâncias de Orchestrator Python, com mesmo engine/modelo principal, prompts diferentes e wrappers de ferramentas. Elas recebem JSON com pedido, memória recuperada, objetivo delegado e até dois resultados anteriores. Retornam AgentResult com conteúdo/turns/tool_results/metadata. São independentes como objetos/contextos, mas compartilham engine, desktop, ambiente, política e bus; não são processos/LLMs físicos separados. E05,E07.

**CONFIRMADO:** especialistas executam sequencialmente, parallel_toolsFalse; worker pesado único e lock desktop serializam o caminho. TEMP não é agente persistente com histórico: é uma chamada de dois messages nova por computer_step. Sua tarefa deve conter os dados necessários, pois não recebe histórico do MAIN. Nenhum especialista tem grafo próprio separado nesse fluxo; Business passa recuperação no payload. Sem isolamento entre tarefas no sistema de arquivos/Chrome, sessão autenticada continua comum. Conflitos com usuário/outro processo continuam possíveis. E06,E07,E13.

Registro da plataforma admite outros agentes, manager, skills/workflow/A2A; não comprova que todos participem do fluxo local. Raciocínio repetido é verificável pela sequência conversa→plano→especialista→TEMP→revisor e eventual corretivo/síntese; não se deve contar concordância desses objetos como validação independente do mundo.

## Memória efetiva do Business

| Aspecto | Implementação confirmada |
|---|---|
| Backend | `BusinessGraph` escolhe Obsidian por default e SQLite explicitamente por sufixo |
| Armazenamento Obsidian | Markdown/frontmatter, declarações e temas, wikilinks, hub usuário |
| O que grava | Citação literal do usuário, kind/topic/origem/status user_statement, external_factFalse |
| Extração | IA propõe declaração, código exige trecho contido na mensagem; instruções de tarefa excluídas por prompt |
| Identidade | hash da citação casefold; não é histórico de versões |
| Segurança do arquivo | lockfcntl, escrita temporária+replace, checa symlinks/raiz/tamanho, filtro limitado de segredos |
| Recuperação | palavras>=4 caracteres, bônus kind, top4 e dois saltos por temas;<=6 notas/3000 caracteres |
| SQLite alternativo | entidades/relações SQL e recall lexical semelhante |

E18–E19: `obsidian_memory.py remember:123–156,recall:182–204`; `business.py _extract:326–340,BusinessGraph:232–238`. **CONFIRMADO:** persistência semântica de declarações pessoais e relações; não é atualização de pesos, nem busca vetorial nesse caminho. Memória é explicitamente pessoal/não verificada, não fonte de fatos externos.

**NÃO ENCONTRADO no fluxo Business:** reconciliação sistemática de correção vs declaração antiga, expiração/versionamento de crenças, memória episódica completa de ações/resultados ou receita procedural adquirida ao navegar. Timestamp/dedup não equivalem a versionamento. **INFERIDO:** similaridade lexical pode perder sinônimos ou favorecer preferência pouco relacionada; coexistência de declarações contraditórias pode contaminar recuperação. Limites de inventário3000 arquivos/1000 notas também afetam alcance. E18.

## Memória e aprendizagem da plataforma: existem, mas integração importa

**CONFIRMADO:** KnowledgeGraphMemory armazena entidades/relações SQLite e busca LIKE textual. FactStore tem trust/origem/persistência e serviço automático condicionado à configuração; FAISSMemory usa embeddings+IndexFlatIP. Routes pode injetar facts/documentos em mensagens system, mas `_converse` TaskManager mantém apenas user/assistant. Business usa próprio grafo. Logo a injeção genérica não comprova que facts/vector cheguem ao principal Business. E19–E21,E04,E06.

**CONFIRMADO:** SkillManager descobre sequências de ferramentas em TraceStore; SkillDiscovery minera subsequências2–4 com frequência/outcome e retorna candidatos; SkillManager escreve os arquivos TOML. Serializer grava cada arguments_template como `{}`: nomes repetidos de computer_step não preservam instrução, seletor, pós-condição ou recuperação. CLI permite mineração explícita. Builder conecta skills em outros caminhos; `_tools` Business restringe lista e não inclui SkillTool. LearningOrchestrator/spec-search possuem otimização/treinamento condicionais, sem conexão comprovada ao mailbox Business. E22–E24,E07,E28.

Recipes carregam composição de agente/configuração, não constituem descoberta automática da navegação. Checkpoint Git do spec-search guarda configuração/agentes/tools para rollback, não janela/aba/estado de execução. TraceStore guarda execução genérica; JSONL Business guarda somente estrutura/tempos/tokens/códigos, sem arguments/resultados. Journal lê histórico, não reconstrói fila nem macro executável. E06,E22–E24.

## Central de Vendedores amanhã

**CONFIRMADO pelo caminho examinado:** `_run` planeja/delega novamente; não grava o percurso validado como procedimento recuperável. Pode reutilizar preferência/fato pessoal explicitamente lembrado, não há comprovação de menos raciocínio amanhã. **NÃO VERIFICADO:** experiência de outros agentes/configurações de learning fora desse caminho.

Faltam conexões comprovadas entre sucesso verificado → representação de procedimento com parâmetros/condições → armazenamento/proveniência → recuperação aplicável ao objetivo → execução sob estado atual → confirmação/atualização. Isso descreve a lacuna atual, não implementa uma arquitetura futura. Também falta checkpoint executável do mailbox para “continue depois de reiniciar”; complementos durante execução reiniciam fluxo, não retomam de um cursor de procedimento.
