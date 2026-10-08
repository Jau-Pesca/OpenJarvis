# Atualização do runtime local

`preparar_modelos.py` é o checker leve dos atalhos: verifica Ollama e modelos
instalados, sem download ou inferência. `install_lazy_startup.py --install` aplica
essa cópia com checksum/backup, preservando configurações e helper.

`validate_lazy_models.py` verifica em Chrome isolado que abertura/seleção não
carrega modelos e que o primeiro envio real carrega o escolhido. A opção
`--prepare-cold` libera somente Qwen9b/4b residentes depois de verificar Jarvis
ocioso; não apaga arquivos nem libera modelos de terceiros.

`install_runtime.py` atualiza somente `chamada_continua.py`, a fonte `mac-control/control.m` e o aplicativo `JarvisMacControl.app`. Configuração, dados, arquivos e cofre Obsidian ficam preservados.

Por padrão, o script mostra hashes e audita a assinatura, sem alterar arquivos:

```sh
.venv/bin/python scripts/local/install_runtime.py
```

Depois de encerrar a chamada e a interface, aplique com:

```sh
.venv/bin/python scripts/local/install_runtime.py --install
```

`--voice-only` ou `--native-only` limitam a atualização. `--check` importa `native('status')` do projeto e usa o mesmo transporte do runtime: aplicativo por LaunchServices quando `request_file_supported=true`, com arquivos privados de pedido/resposta. Não move o cursor nem exibe diálogo de configuração. Essa opção requer acesso à sessão gráfica, mesmo em dry-run.

O instalador recusa mudanças concorrentes nos arquivos externos, compila com o SDK macOS 26.5, preserva `Info.plist` e mantém a assinatura ad hoc existente. Reconstrução muda o hash de identidade e pode exigir reabilitar Acessibilidade e Gravação de Tela no macOS. Não há promessa de estabilidade TCC entre reconstruções.

Backups ficam em `~/OpenJarvis-local/backups/runtime-<data UTC>`. Falhas durante substituição restauram os arquivos e o aplicativo anteriores. Falha do diagnóstico opcional após instalação não provoca rollback.

O helper aceita stdin JSON ou `--request-file PATH --response-file PATH`. No segundo modo, ambos os arquivos precisam estar no mesmo diretório privado, pertencente ao usuário e sem acesso de grupo/outros. A resposta é gravada atomicamente. Esse modo permite ao Python lançar o aplicativo por LaunchServices sem exibir o diálogo de configuração por operação.
