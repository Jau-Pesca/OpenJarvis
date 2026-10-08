# Preferências do usuário

## 2026-10-08 — Auditoria antes de evolução

Pedido explícito: investigar profundamente sem alterar código/configuração/dependências/runtime, produzir oito relatórios com evidências e subagentes validadores antes da entrega. Distinguir implementação real de conceitos e registrar dados ausentes. O documento anexado é o contrato da auditoria; nenhuma implementação das direções de melhoria está autorizada nesta etapa.

## 2026-10-08 — Transparência e desempenho

- Usuário precisa ver em qual etapa a tarefa está e onde falhou, por exemplo localizando navegador, e quer entender por que há demora mesmo com ferramentasPython.
- Autoescuta do Jarvis como usuário foi relatada; proteger contra eco, diferenciando alto-falante de uso com fones para interrupção.
- Não substituir ação por resposta de intenção ou alegação de sucesso sem execução verificada.

## 2026-10-08 — Permanência na RAM

- Manter modelo por aproximadamente cinco minutos após o último uso; evitar carga/descarga entre respostas. Continuar carregando somente quando houver primeiro envio.

## 2026-10-07 — Orientações explícitas

- Usar `docs/prompts/PROMPT_HARNESS_CODEX.md` como orientação de execução.
- Registrar em documentação tudo que for relevante nas conversas: pontos
  importantes, o que será feito, por que será feito, quando foi decidido,
  exemplos e motivos, para servir de contexto a outros agentes de IA.
- Aplicar a memória local versionável em `docs/anotations/`, conforme o harness.
- Registrar pedidos, correções, aprovações e recusas no arquivo apropriado;
  produzir sínteses rastreáveis, datadas e sanitizadas.

Origem: mensagem do usuário nesta sessão e harness explicitamente indicado.
Comunicação atual em português, acompanhando a mensagem do usuário; não houve
uma declaração de preferência permanente de idioma.

## Retomada em 2026-10-07

- `PROMPT_MEMORIA.md` estabelece português brasileiro para interface/conversa
  do assistente e para a comunicação desta entrega.
- Preferir comprovação real à afirmação de conclusão baseada só em testes
  simulados. Uso do Chrome pessoal visível e cursor real é requisito explícito.
- Pedido de navegação autoriza passos necessários; não pedir segunda autorização
  de navegador. Aprovações técnicas do macOS/sandbox continuam obrigatórias.
- Principal deve conversar/delegar/redirecionar pela IA, sem classificação de
  frases por listas de palavras. Falhas faladas devem ser breves; detalhes na UI.
- Usuário informou troca de esforço light para medium; não alegar configuração
  programaticamente comprovada ou trocar modelos sem capacidade real.
- Usuário confirmou configuração de Acessibilidade (com imagem) e inclusão em
  Gravação de Tela. Após reconstrução assinada, foi solicitada nova autorização
  da versão atualizada, porque o status real voltou a negar ambas.
- Após teste físico, usuário confirmou que mouse/teclado funcionaram muito bem,
  mas o autocomplete do Chrome completou a URL com um anúncio antigo. Instrução
  explícita: acrescentar um espaço após a URL digitada na barra de endereço;
  exemplo `mercadolivre.com` → `mercadolivre.com `.

## 2026-10-08 — Reafirmação do harness e da memória documental

Origem: mensagem atual do usuário, com referência a `docs/prompts/PROMPT_HARNESS_CODEX.md`. Reafirmada a orientação de registrar os pontos relevantes de toda conversa: decisões, datas, ações previstas, motivos e exemplos, para contexto de futuros agentes. Aplicar como síntese rastreável em `docs/anotations/`, antes de avançar com implementação relevante. O harness orienta a execução dentro das instruções superiores e capacidades reais da sessão; não muda a hierarquia de instruções nem configura o modelo.
