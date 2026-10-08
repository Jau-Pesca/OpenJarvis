# Fixtures do controle nativo

Execute a partir da raiz do repositório. Esses testes compilam a fonte versionada por inclusão relativa, sem instalar ou reassinar o aplicativo:

```sh
xcrun clang -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk -fobjc-arc -framework Cocoa -framework ApplicationServices -framework ImageIO tests/local/native/test_resize.m -o /private/tmp/openjarvis-test-resize
/private/tmp/openjarvis-test-resize
xcrun clang -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk -fobjc-arc -framework Cocoa -framework ApplicationServices -framework ImageIO tests/local/native/test_keyboard.m -o /private/tmp/openjarvis-test-keyboard
/private/tmp/openjarvis-test-keyboard
```

O SDK 26.5 foi necessário porque o linker disponível rejeitou `arm64e.x1` nos arquivos `.tbd` do SDK padrão 27.0.

`test_resize.m` cria um PNG RGB `220,40,20`, reproduz a conversão antiga com `NSImage.drawInRect` e verifica a conversão CoreGraphics/JPEG, dimensões e erro de arquivo ausente. Na execução de 07/10/2026, o caminho antigo retornou `0,0,0`; o atual preservou `221,40,21`. A saída antiga é evidência de reprodução, enquanto a asserção exige preservação de cor pelo código atual. Não captura a tela nem usa imagens pessoais.

`test_keyboard.m` intercepta **todos** os `CGEventPost` e confere os códigos/flags dos eventos, a liberação de Command, Unicode por caractere com surrogate pair e Enter sem modificadores. Não publica eventos físicos. A criação da fonte privada CoreGraphics pode exigir execução fora do sandbox; se ocorrer essa restrição, solicite a autorização apropriada antes de executar fora dele.

Essas fixtures comprovam conversão da imagem e construção dos eventos. Recepção pelo Chrome, permissões TCC e navegação real precisam de validação na sessão gráfica.
