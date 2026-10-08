# 03 — Computer Use, macOS e navegador

Data:2026-10-08. Evidências E12–E17 e E26, detalhadas em [EVIDENCIAS.md](EVIDENCIAS.md). Auditoria não moveu mouse, abriu navegador, capturou tela ou executou modelo.

## Executor real

**CONFIRMADO:** Python chama helper Objective-C `JarvisMacControl.app`, com CoreGraphics/Quartz, Accessibility e LaunchServices; AppleScript separado consulta/ativa Chrome. Não é apenas executar um script Python predefinido: SUBAGENT_MAIN/especialista escolhe o passo e TEMP escolhe uma ação local. O helper recebe JSON por arquivos privados/request-response ou stdin legado; subprocessos possuem timeout. Permissões AX, captura e publicação de eventos são verificadas. Fonte repo e fonte do runtime têm hash igual; correspondência entre fonte e binário instalado **NÃO VERIFICADA**.

`ComputerStepTool.execute:335–390` aceita instrução<=1500 caracteres, apps Chrome/Numbers/Excel/Finder e ações navigate/observe/click/move/type/key/scroll. Sob lock global: checa cancelamento → observa → envia dois contextos novos ao TEMP → parseia JSON → valida parâmetros/coordenadas → executa → observa novamente → ToolResult. Contexto TEMP não contém o grafo pessoal/histórico inteiro. App arbitrary não é permitido por este contrato. E13, E15.

| Capacidade | Caminho confirmado | Garantia prática |
|---|---|---|
| Screenshot | `control.m:28–41,111–121`, screencapture monitor1, CoreGraphics/ImageIO, JPEG<=1280px | Janela deve caber no monitor capturado; não é captura exclusiva do conteúdo Chrome |
| Elementos | AX walk:profundidade12,500 visitados,100 emitidos; Python40 nós | Inclui títulos/descrições/valores; sem AXSecureTextField; página longa fica parcial |
| Janela | ID AppleScript+PID em lease; AXFocusedWindow no helper atual | Correlação por título/bounds; não identidade estável da aba/DOM |
| Foco | ativa janela pelo ID, AXRaise e foreground | Resultado AXRaise não é confirmado diretamente |
| Mouse/clique | CGWarpMouseCursorPosition gradual; eventos HID down/up | Mede cursor; dispatch declara posted_not_confirmed |
| Teclado | fonte privada, flags explícitos, solta Command, Unicode/caractere | Postagem não comprova recebimento de texto pelo campo |
| Scroll/atalhos | eventos CoreGraphics; action/key validado | Efeito funcional depende de foco/estado atual |
| Resultado | nova observação; URL verificada para navigate | Não há pós-condição de negócio universal para click/type |

Com imagem, qualquer ponto dentro de window_bounds pode passar; sem imagem, proximidade<=3 pontos de um nó AX. Conversão pixel→ponto global fica a cargo do modelo, não de função geométrica determinística. E13–E15.

## `window_changed`: causa, propagação e repetição

**CONFIRMADO:** helper compara título e quatro bounds observados, tolerância de um ponto, em `control.m main:143–149`. `DesktopSessions.chrome_view:181–204` correlaciona AX/AppleScript e tenta até3 observações. Mensagens de título, posição ou correspondência viram `error_code=window_changed` em `ComputerStepTool.execute:388–390`; `_GuardedTool` registra falha e UI `TaskTrace` traduz para “Janela mudou durante a etapa”. A frase agrupa causas; não significa necessariamente movimento pelo usuário. E13–E15, E26.

**CONFIRMADO:** permissões negadas são retryableFalse, mudança de janela não. Especialista recebe erro e pode repetir; não há política determinística que mude estratégia ou encerre após N vezes desse código. A correlação tenta observar novamente, mas não substitui sistematicamente lease de janela/aba nova. E07, E13.

**INFERIDO:** mudança legítima de título durante carregamento, popup mudando AXFocusedWindow, geometria/foco ou observações sequenciais em instantes diferentes podem invalidar guard. Também pode haver ação executada e falha apenas no observe posterior; ToolResult então não é recibo de sucesso. Guard de título/bounds pode rejeitar mudança legítima ou deixar passar mudança de conteúdo mantendo título/bounds. Lock Python não bloqueia usuário/outro processo. **NÃO VERIFICADO:** qual dessas subcausas ocorreu no caso102s. Reprodução futura segura e dados necessários estão em06/07; não foi realizada aqui.

## Navegação e sessão

**CONFIRMADO:** Chrome pessoal existente conserva autenticação/cookies porque o executor opera sua UI. `ensure/_acquire` mantém lease de janela, verifica Chrome, recupera processo sem janela reabrindo uma vez e ativa pelo ID; não usa ID estável de aba. Abrir site via `navigate` cria nova guia por AX ou Cmd+T, localiza barra AX, clica, seleciona, digita URL com espaço final, Enter e verifica URL até40 polls com .2s. Isso explica criação de aba mesmo com site aberto. E13–E14.

**CONFIRMADO:** confirmação exige hostname/path/query iguais; não inclui scheme/porta/fragmento. Redirect legítimo para domínio/caminho/query distinto pode ser relatado como falha. Não equivale a estado network-idle ou página funcionalmente pronta. Sem necessidade de nova URL, menus são ações coordenadas escolhidas usando screenshot/AX; o modelo decide se explorar botão/scroll/observe. Não há procedimento específico da Central de Vendedores implementado.

**NÃO ENCONTRADO no caminho nativo:** escolha automática de aba pelo domínio com inventário completo/ID persistente; tratamento geral de abertura/fechamento/redirect de abas; DOM/CDP, OCR dedicado ou extração tabular nativa garantida. Há textos AX e URL, suficientes em alguns cenários sem imagem, mas sem garantia de acessibilidade completa. A captura é enviada ao modelo de visão quando presente; suporte real de cada modelo/backend **NÃO VERIFICADO** nesta auditoria.

**CONFIRMADO — caminho alternativo Playwright:** `browser.py:_ensure_browser:23–44` inicia Chromium com perfil próprio/headless configurável, não conecta ao Chrome pessoal. `BrowserNavigateTool` faz page.goto; click/type usam seletores; extract consulta DOM. Quando desktop está ativo, `_tools` Business exclui browser_*; não existe fallback automático nativo→Playwright no fluxo examinado. Playwright permanece disponível em outras configurações. PyAutoGUI/Selenium não foram encontrados como executor deste caminho; presença em todo ecossistema não foi presumida. E17.

## Aplicativos fora do Chrome e limite de privacidade

**CONFIRMADO:** `app_observe/app_act:220–260` identificam Numbers/Excel/Finder por bundle/PID, abrem se necessário e mantêm lease de título; ação reobserva, aplica guard de título/bounds e atualiza título após retorno. Não aceitam navigate URL. Mudança espontânea do título entre passos pode impedir observação por ValueError (não recebe necessariamente o rótulo window_changed de Chrome). Não é controle genérico de todos os aplicativos; lease de app não equivale a isolamento de documento.

**CONFIRMADO:** exclusão de AXSecureTextField limita nós textuais, mas screenshot do monitor ainda pode conter dados visíveis; não foi encontrado redator visual obrigatório antes da inferência. Não houve captura durante a auditoria. Operação em modelo local não elimina necessidade de limitar conteúdo em eventual trace/engine remoto configurado. E13–E15,E33–E34.
