# Riscos e questões abertas

## 2026-10-08 — Riscos identificados pela auditoria R-025

Registro prioritário e reprodução segura em [06-FALHAS-E-RISCOS](../auditoria/2026-10-08/06-FALHAS-E-RISCOS.md). Confirmadas lacunas: piso de capabilities perdido por wrappers desktop/planilha; confirmação sensível por prompt; scanner non-local não inspeciona observação desktop; efeito pode continuar após timeout; window_changed não terminal; conclusão por recibo genérico/revisor; navegação não vira procedimento Business; redirect reinicia sem checkpoint; journal não reconstitui fila/contexto. Não houve ataque, ação perigosa ou correção nesta auditoria.

Subcausa do102s permanece aberta: primeira falha após click retornado; dez seguintes antesTEMP na localização; necessários motivo do guard/identidade aba/bounds/transições redigidos em fixture. Não confundir11erros com11cliques. Configuração/backend/binário/proteções ativas e benchmark4Bvs9B não verificados nesta etapa.

## 2026-10-08 — Latência, decisão e voz

- Modelo pode formular reply incorreto como se tivesse executado. Teste reproduziu; promptreforçado/protocolo coerente corrigiram revalidação, mas não garantem semântica perfeita. Não alegar eliminação absoluta de alucinações. Nova proteção semântica adicional porIA custaria chamadaextra; não introduzida semnecessidade comprovada apóscorreção.
- Exemplo real Qwen4b precisou6inferências embackground,28.2s na tarefa/32.3s total, cerca7.7s na ação nativa de navegação; há latência residual real. Removeu-se extração duplicada, não promessa de execuçãoinstantânea.
- Alto-falante não permite interrupção porvoz durantea resposta; fones permitem. Gate+.5s não é AEC completo; reverberação comcaudamaior/hardware específico exige validação acústica real. Nunca filtrar usuário por texto parecido.
- Logs têm metadados, retenção2arquivos~5MiBcada/200eventosporconsulta; arquivo não recupera tarefa para reexecutar. Falha escritavisível trace_error não falhaação; leitura corrupta ignora linha, erroIO/Unicode→503.
- Verificação real independente detectou movimentojanela apósnavigate. Ordem de leitura corrigida sem rebuild/TCC; última repetição PASS sem falha,30,2s/24,7background, mas mudanças reais de janela ainda devem bloquear cliques por segurança.

## 2026-10-08 — Artefatos de migração

- GPToss original e convertido são blobs distintos de tamanho lógico≈12,85GiB; alias llamacpp compartilha blob com convertido. Espaço físico APFS não medido. Não remover variantes/alias para corrigir UI; gerenciador pode depender deles.
- Migração também explica uma recarga observada; não houve evidência de unload repetido do mesmo GPT em mensagens consecutivas sem alternância. RAMtotal24GiB, limite2modelos é máximo, não garantia de coexistência.

## 2026-10-08 — Cache e capacidade de RAM

- R-020: Jarvis solicita keep_alive5m por inferência e não descarrega na seleção. Não é garantia de residência sob pressão: Ollama registrou evicções com previsto13,1GiB e disponível9,5/3,6GiB ao carregar gpt-oss20b (ps cerca11,86GiB).
- Principal gpt-oss20b + TEMP4b podem competir pela mesma RAM. Não trocar modelo escolhido nem remover TEMP silenciosamente; se recargas persistirem, avaliar capacidade/modelos com usuário.
- TEMP usa contextos4096 sem imagem/8192 com imagem; principal8192. Mudanças de contexto podem causar recarga, mas logs inspecionados confirmam memória como motivo dos eventos acima; hipótese de contexto não comprovada.
- `retained` na resposta de seleção indica apenas anterior não descarregado por essa operação; não é inventário residente. Use /api/ps.
- RAM não possui desgaste por gravação comparável a flash; motivação é latência/recursos. Expiração efetiva após cinco minutos não foi cronometrada nesta rodada.

Atualizado em 2026-10-07 (America/Sao_Paulo).

| Item | Estado | Impacto | Responsável / condição |
|---|---|---|---|
| Modelo `gpt-5.6-terra` solicitado pelo harness não disponível | Limitação confirmada | Configuração exata não pode ser garantida | Orquestrador: declarar uso do modelo herdado |
| Alterações preexistentes não auditadas | Inspeção autorizada pela retomada | Preservar autoria e dados | Agentes investigam áreas delimitadas |
| Controle Mac e acesso local ao Ollama | Comprovados nesta sessão | Navegação e clique reais passaram com modelos configurados | Manter observação de resultado e testes de regressão |
| Arquivos operacionais fora da raiz gravável | Restrição confirmada | Alterar scripts/app em OpenJarvis-local ou Applications exige escalation | Preparar correção revisável antes da operação |
| TCC da versão reconstruída | Resolvido: AX1, screen=true, posting_events=true via LaunchServices | Reconstrução futura ad hoc pode exigir nova concessão manual | Evitar rebuild desnecessário; não limpar permissões já válidas |
| Latência qwen3.5:9b | ~6,3s em validação focal; fluxo completo: confirmação24,14s, tarefa80,22s | Não equivale a conversa instantânea; correção funcional não resolve toda a latência | Avaliar etapa por etapa sem trocar modelos escolhidos silenciosamente |
| Eco/entrada de voz reais | Não comprovados | Interrupção sintética não prova cancelamento de eco acústico | Validação com usuário e microfone |

Não há autorização de permissões pendente para o helper atual. O espaço final
foi validado nesta navegação; observação da URL continua necessária porque um
teste não garante comportamento de todas as versões/configurações do Chrome.

## 2026-10-08 — Seletor

- Tradução automática causando removeChild: hipótese forte, não comprovada no
  Chrome pessoal. Proteção e tradução nativa aplicadas ao seletor; emulação e
  alternância real de abas passaram. Não traduzida toda a aplicação neste escopo.
- Failed to fetch original: configuração persistida do navegador pessoal não foi
  lida. URL loopback obsoleta reproduzida em contexto isolado e corrigida no modo
  gerenciado; outros erros de rede permanecem possíveis e têm diagnóstico visível.
- D-008 substitui comportamento anterior: novas chamadas recebem modelo da UI;
  seleção não reconfigura chamada já ativa nem configuração externa.
- Descarga protege mailbox e inferência non-stream pelo lock compartilhado;
  não é gerenciador de memória para clientes externos independentes do Ollama.
  Modelos em uso são retidos; redução observada3,68GiB refere-se ao /api/ps.

## 2026-10-08 — Política sob demanda (D-010)

- Abertura/seleção não carregam LLM. Primeira resposta pode demorar mais pela
  carga inicial, aceita como consequência do pedido de economizar RAM.
- Modelos usados anteriormente podem ficar residentes até vencimento no Ollama;
  essa residência não demonstra aquecimento na nova abertura.
- Tarefas agendadas existentes podem gerar independentemente de envio manual;
  não foram desativadas. Áudio Whisper/Kokoro inicializa por necessidade da chamada.
