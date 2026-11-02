# Android nativo — Aventura das Letras

Este aplicativo usa telas Android nativas em Java (`Activity`, `ImageView`, botões e `TextToSpeech`). Não há WebView, servidor ou navegador embutido. Todo o conteúdo acompanha o APK; não há permissão de Internet, cadastro, anúncios ou compras. Requer Android 6.0 (API 23) ou superior.

## Gerar e instalar

Na raiz do repositório, com Java 17 ou superior, `curl`, `unzip` e `zip` disponíveis (se houver apenas o JRE, o script baixa o compilador Eclipse ECJ verificado do Maven Central):

```sh
bash scripts/build-android.sh
```

O script usa o SDK apontado por `ANDROID_SDK_ROOT`/`ANDROID_HOME`, ou `/workspace/.android-sdk`. Se necessário, baixa a plataforma 35 e build-tools 35.0.0 oficiais do Google e confere os checksums publicados. TLS e verificações permanecem habilitados. O APK universal fica em `android/app/build/outputs/apk/debug/aventura-das-letras-debug.apk`.

Transfira o APK ao celular e abra-o. Autorize a instalação por essa fonte quando o Android pedir. É uma compilação de desenvolvimento, assinada com chave de depuração local, adequada para testes. Para instalar com um computador e depuração USB habilitada:

```sh
adb install -r android/app/build/outputs/apk/debug/aventura-das-letras-debug.apk
```

O projeto também pode ser aberto no Android Studio (`android/`), usando Gradle 8.9, JDK 17+ e Android SDK 35. O SDK fica fora do controle de versão. A publicação na Play Store exige compilação de lançamento e uma chave de assinatura do responsável pelo aplicativo; a chave de desenvolvimento não serve para produção.

## Conteúdo e privacidade

`public/content/words.json` e `public/images/` são os mesmos arquivos da versão web, empacotados como assets. Edite o JSON e as imagens e gere um novo APK para atualizar o conteúdo. O aplicativo mantém preferências e histórico em `SharedPreferences`, apenas neste aparelho, com backup desativado. A área dos responsáveis permite apagar o progresso mediante confirmação. Desinstalar também remove esses dados.

A voz usa o mecanismo de síntese do Android com uma voz **pt-BR local**, sem dependência de rede. Se o aparelho não tiver essa voz instalada, o jogo continua com apoio visual e informa a limitação na área dos responsáveis. Instale a voz nas configurações de texto para fala do sistema. Uma nova fala cancela a anterior. Os acentos são preservados na palavra e revelados pela vogal-base; Ç tem tecla própria. Letras repetidas são reveladas juntas. Não há cronômetro nem limite de erros.

## Verificações

Para executar os testes das regras sem SDK Android:

```sh
mkdir -p /tmp/aventura-native-tests
javac -encoding UTF-8 -d /tmp/aventura-native-tests android/app/src/main/java/br/com/aventuradasletras/app/GameEngine.java android/tests/GameEngineTest.java
java -cp /tmp/aventura-native-tests GameEngineTest
```

No aparelho, verifique: toque e teclado físico, áudio ligado/desligado, letras repetidas, ajuda automática depois de três erros, conclusão assistida, próximo item somente após concluir, filtros de nível/categoria, sequência sem repetição, histórico após fechar/abrir, exclusão confirmada e telas pequenas. A validação de compilação e assinatura não substitui esse teste em aparelho.
