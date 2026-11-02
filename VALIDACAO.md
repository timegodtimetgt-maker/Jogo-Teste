# Validação da entrega

Validação executada em 2 de novembro de 2026.

| Verificação | Resultado |
| --- | --- |
| Regras e conteúdo web (`npm test`) | 14 testes passaram; nenhum ignorado |
| Navegador Chromium (`python tests/browser_smoke.py`) | 12 fluxos passaram; nenhum erro JavaScript |
| Desktop 1280 px e celular 390/320 px | Sem transbordamento horizontal |
| Conteúdo | Exatamente 100 palavras únicas, 40/35/25, limites de letras e 100 PNGs válidos |
| Conclusão de conteúdo | Todas as 100 palavras concluíveis manualmente e com ajuda |
| Repetição e filtros | Letras repetidas reveladas juntas; cliques repetidos ignorados; palavras não repetidas na sessão, inclusive com filtros sobrepostos |
| Preferências e histórico | Persistência, pistas desligadas, animações reduzidas e exclusão confirmada verificados |
| Web offline | Interface e conteúdo disponíveis após instalação completa do cache na primeira visita |
| Voz web | Cancelamento, chamadas e silenciamento verificados com síntese simulada; fallback sem pt-BR validado |
| Build web (`npm run build`) | Site estático gerado em `dist/` |
| Regras Android (JVM) | 15 verificações passaram |
| APK Android | Compilado com SDK 35; assinaturas v1, v2 e v3 verificadas |
| Conteúdo no APK | JSON e 100 PNGs conferidos byte a byte com a versão entregue |

O Chromium deste ambiente não disponibilizou uma voz pt-BR. Portanto, **reprodução de áudio real não foi validada**. A interface informa a limitação e o jogo continua utilizável visualmente. A fala depende de uma voz instalada e disponibilizada pelo dispositivo; o Android seleciona uma voz pt-BR offline.

**Não havia emulador nem aparelho Android conectado.** As regras, a compilação, os assets e a assinatura foram validados; a interação visual nativa, a instalação em aparelho e o áudio real ainda precisam de verificação no dispositivo. O APK entregue é uma compilação debug para teste, não uma publicação na Play Store.

Os cinco avisos de compilação Android referem-se a APIs de `Locale`/`WindowInsets` marcadas como obsoletas no SDK recente. São usadas para manter compatibilidade com Android 6.0 e não impediram a compilação.

Para reproduzir as regras nativas com o JRE e o compilador preparado neste ambiente:

```sh
mkdir -p /tmp/aventura-native-tests
java -jar /workspace/.android-sdk/ecj-3.38.0.jar -8 -proc:none -encoding UTF-8 -d /tmp/aventura-native-tests android/app/src/main/java/br/com/aventuradasletras/app/GameEngine.java android/tests/GameEngineTest.java
java -cp /tmp/aventura-native-tests GameEngineTest
```

Com JDK, use a alternativa `javac` documentada em `android/README.android.md`. Os testes de navegador usam Playwright e Chromium, ferramentas de desenvolvimento; não são dependências de execução do jogo. Relatório e capturas estão em `artifacts/` após o teste.
