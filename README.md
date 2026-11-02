# Descubra a Palavra — Aventura das Letras

Jogo de alfabetização em português brasileiro para crianças a partir de 6 anos. Um jardim, a mascote Lili e 100 palavras para descobrir sem cronômetro, punição ou limite de tentativas.

Há duas implementações: **web responsiva**, em HTML/CSS/JavaScript, e **Android nativo**, em Java e componentes do Android. O Android não usa WebView. Ambas leem o mesmo banco e as mesmas ilustrações locais.

## Downloads

- [APK Android nativo — versão de teste, Android 6.0+](https://github.com/timegodtimetgt-maker/Jogo-Teste/raw/refs/heads/main/artifacts/aventura-das-letras-android.apk)
- [Versão web pronta para executar](https://github.com/timegodtimetgt-maker/Jogo-Teste/raw/refs/heads/main/artifacts/aventura-das-letras-web.zip)
- [Código-fonte completo das duas versões](https://github.com/timegodtimetgt-maker/Jogo-Teste/raw/refs/heads/main/artifacts/aventura-das-letras-fontes.zip)
- [Checksums SHA-256](artifacts/SHA256SUMS.txt)

Para testar no celular, baixe e abra o APK. Para a web, extraia o ZIP e siga o `LEIA-ME.txt`. Veja as limitações dos testes em [VALIDACAO.md](VALIDACAO.md).

## Abrir a versão web

Requisito: Node.js 20 ou superior. Não há pacotes externos para instalar, serviços pagos ou chaves de API.

```sh
cd /workspace/Jogo-Teste
npm start
```

Abra `http://localhost:5173` no seu computador. Para outro dispositivo na mesma rede, use o IP do computador e a porta 5173, respeitando o firewall local. A voz depende de uma voz **pt-BR** instalada e disponibilizada pelo navegador. O jogo continua com imagens quando ela não estiver disponível. O botão “Ouvir como brincar” habilita a primeira interação com o áudio.

No ambiente de nuvem, o servidor pode ser validado por requisições internas; a interface de onboarding não fornece prévia web pública.

```sh
npm test                 # regras, distribuição e integridade do conteúdo
npm run build            # site estático completo em dist/
node scripts/serve.mjs --dist
```

Para publicar a versão web, envie o conteúdo de `dist/` para uma hospedagem estática **na raiz do domínio**. HTTPS habilita o service worker: depois do primeiro carregamento e do cache dos recursos, as imagens, palavras e interface ficam disponíveis sem conexão. A primeira visita e a instalação do cache precisam de conexão. Nenhum serviço de terceiros é chamado pelo código do jogo. A voz é fornecida pelo sistema e algumas vozes do navegador podem usar conexão.

## Instalar a versão Android

O APK de teste fica em `artifacts/aventura-das-letras-android.apk` depois de executar o empacotamento. Requer Android 6.0 ou superior. Transfira o APK para o aparelho e abra-o; autorize a instalação pela origem usada quando o Android solicitar. É uma versão **debug**, assinada para teste; publicação na Play Store exige uma chave de produção e os procedimentos da loja.

O app não solicita permissão de internet nem coleta dados. Para fala offline, instale uma voz de português brasileiro nas configurações de síntese de voz do Android. Sem essa voz, o jogo continua com apoio visual e informa a limitação na área dos responsáveis.

Para compilar pelo Android Studio, abra a pasta `android/` e instale o SDK indicado pelo projeto. Para compilar em Linux sem Android Studio:

```sh
bash scripts/build-android.sh
```

O script baixa ferramentas oficiais do Android SDK se necessário, verifica seus checksums e gera o APK em `android/app/build/outputs/apk/debug/`. Use Java 17+ com `keytool` e `javac` (ou o compilador Eclipse que o script prepara quando há apenas JRE). Consulte [android/README.android.md](android/README.android.md) para os detalhes.

## Como brincar e testar

1. Toque em **Vamos brincar**. O padrão é **Primeiros passos**: 40 palavras de 3–4 letras, imagem visível e oito letras para escolher.
2. Toque nas letras ou use o teclado físico. Letras repetidas aparecem juntas, e a mesma tecla não é contabilizada duas vezes.
3. Após três tentativas incorretas, a ajuda é oferecida quando habilitada. A rodada continua sem limite de erros.
4. **Uma ajudinha** mostra a imagem e repete a palavra, depois destaca opções e depois revela letras. Sem voz disponível, as etapas visuais continuam funcionando.
5. Ao completar, observe a palavra inteira. A próxima rodada só começa ao tocar em **Próxima palavra**.
6. Em **Responsáveis**, escolha **Descobrindo letras** (35 palavras de 4–5 letras) ou **Novo desafio** (25 de 5–6 letras), filtre categorias, ajuste áudio, pistas e animações, ou consulte o histórico.
7. Complete todas as palavras da seleção para iniciar uma nova sequência embaralhada explicitamente. Trocar filtros não apaga as palavras já vistas durante a sessão.
8. Recarregue o navegador ou reabra o app para verificar preferências e histórico. O conjunto de palavras já vistas é por sessão. Para apagar o histórico, use **Reiniciar progresso** e confirme; cancelar preserva os registros.

O histórico registra palavras praticadas e quantas conclusões tiveram ajuda. No terceiro nível, pedir imagem ou palavra falada conta como ajuda. O nome de uma letra não é tratado como fonema. A letra-base revela vogais acentuadas com a grafia correta; **Ç** tem tecla própria quando necessário. Não usamos separação silábica automática.

## Editar conteúdo

O arquivo [public/content/words.json](public/content/words.json) é a fonte compartilhada. Cada objeto tem:

```json
{
  "word": "BOLA",
  "level": 1,
  "category": "brinquedos",
  "image": "/images/bola.png",
  "clue": "É redonda e podemos jogar com os pés ou com as mãos.",
  "audio": "Bola"
}
```

Use maiúsculas na palavra, preserve acentos e mantenha áudio, pista e imagem correspondentes. Categorias aceitas: `animais`, `alimentos`, `brinquedos`, `casa`, `natureza`. As imagens são locais e têm estilo consistente. Os SVGs são editáveis; o Android usa os PNGs. Revise cada ilustração e a familiaridade da palavra com o adulto que acompanha a criança.

Depois de editar palavras ou imagens, rode `npm test`, `npm run build` e recompile o APK. O teste exige exatamente **100 palavras**, distribuídas em **40/35/25**, sem duplicações e com os comprimentos corretos. Para uma edição publicada do site, atualize também o identificador `CACHE` em `public/sw.js` para instalar um novo cache offline.

O gerador [scripts/generate-images.py](scripts/generate-images.py) guarda os desenhos SVG em `ART` e o conteúdo inicial em `CONTENT`. Com Python 3 e Inkscape, `python3 scripts/generate-images.py` recria o JSON e os PNGs; esse comando sobrescreve edições diretas desses arquivos. Para manter suas edições em futuras regenerações, altere também o gerador.

Em Linux, `npm run package` recompila as duas versões e produz o APK, o ZIP web e o ZIP dos fontes em `artifacts/`, com checksums SHA-256. O pacote web inclui servidor Node e instruções; não deve ser aberto diretamente por `file://`.

Consulte [VALIDACAO.md](VALIDACAO.md) para os testes executados e as verificações que ainda dependem de um aparelho Android e de uma voz pt-BR real.

## Organização

- `src/game.js`: regras da versão web, sem dependência de interface.
- `src/app.js` e `src/style.css`: interface web, acessibilidade, voz e armazenamento.
- `public/content/words.json` e `public/images/`: conteúdo compartilhado.
- `android/`: interface nativa, regras Java e testes JVM.
- `tests/`: testes de regras e conteúdo; testes de navegador quando disponíveis.
- `scripts/`: servidor, build web e build Android.

Preferências e progresso ficam apenas no armazenamento do navegador ou nas preferências privadas do app. Não há sincronização entre web e Android. Limpar dados ou desinstalar apaga o histórico local.
