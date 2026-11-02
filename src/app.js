import { ALPHABET, LEVELS, CATEGORIES, DEFAULT_PREFS, baseLetter, keyboardFor, createRound, guess, giveHint, isComplete, WordDeck, loadSaved, saveState } from './game.js';

const app = document.querySelector('#app');
let deviceStorage;
try { deviceStorage = window.localStorage; } catch { deviceStorage = { getItem: () => null, setItem: () => { throw new Error('Armazenamento indisponível'); } }; }
const saved = loadSaved(deviceStorage);
let prefs = saved.prefs, history = saved.history, words = [], deck, round, keys = [], screen = 'welcome';
let message = 'Cada letrinha é uma descoberta!', celebrating = false, storageOkay = true, voice = null, voicesLoaded = false;
const icons = {
  sound: '<path d="m11 5-6 4H2v6h3l6 4V5Z"/><path d="M15 8a6 6 0 0 1 0 8m3-11a10 10 0 0 1 0 14"/>',
  mute: '<path d="m11 5-6 4H2v6h3l6 4V5Z"/><path d="m16 9 6 6m0-6-6 6"/>',
  arrow: '<path d="M4 12h15m-6-6 6 6-6 6"/>',
  heart: '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z"/>',
  help: '<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z"/>',
  settings: '<path d="M12 3v2m0 14v2M3 12h2m14 0h2M5.6 5.6 7 7m10 10 1.4 1.4M5.6 18.4 7 17M17 7l1.4-1.4"/><circle cx="12" cy="12" r="5"/>',
  home: '<path d="m3 10 9-7 9 7v11h-7v-7h-4v7H3V10Z"/>',
  close: '<path d="m6 6 12 12M6 18 18 6"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  leaf: '<path d="M20 3C5 1 1 9 5 16s17 2 15-13ZM5 20 16 9"/>',
  eye: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
};
const icon = name => `<svg class="icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${icons[name] || icons.leaf}</svg>`;
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const mascot = (className = '') => `<img class="mascot ${className}" src="/icons/icon.svg" alt="Lili, uma flor sorridente, sua companheira de aventura">`;
const garden = `<svg class="garden-art" viewBox="0 0 1200 140" preserveAspectRatio="xMidYMax slice" aria-hidden="true"><path d="M0 95Q200 50 400 100T800 85T1200 90V140H0Z" fill="#dbe7bc"/><path d="M0 120Q300 80 550 120T1000 110T1200 115V140H0Z" fill="#c8dba5"/><g fill="#88a76d"><path d="M80 140V83Q48 85 47 63Q79 58 80 83Q82 48 110 53Q112 79 80 86M1060 140V89Q1028 89 1029 64Q1059 58 1060 89Q1061 60 1086 65Q1088 90 1060 91"/></g><g fill="#f4cf77"><circle cx="193" cy="112" r="6"/><circle cx="931" cy="110" r="6"/><circle cx="1140" cy="112" r="6"/></g><g fill="#fff9ea"><circle cx="186" cy="109" r="5"/><circle cx="199" cy="108" r="5"/><circle cx="192" cy="119" r="5"/><circle cx="925" cy="105" r="5"/><circle cx="938" cy="106" r="5"/><circle cx="931" cy="117" r="5"/></g></svg>`;

function refreshVoice() {
  if (!('speechSynthesis' in window)) { voicesLoaded = true; return; }
  const voices = speechSynthesis.getVoices();
  voice = voices.find(v => /^pt[-_]BR$/i.test(v.lang)) || null;
  voicesLoaded = voices.length > 0;
  const status = document.querySelector('#voice-status');
  if (status) status.textContent = voiceStatus();
}
function voiceStatus() {
  return voice ? `Voz em português brasileiro disponível: ${voice.name}. A voz pode depender do sistema e de conexão.` : !voicesLoaded && 'speechSynthesis' in window ? 'Voz pt-BR ainda não disponível neste navegador. Se o sistema não fornecer essa voz, o jogo continua com imagens e pistas visuais.' : 'Este dispositivo não disponibilizou voz pt-BR. O jogo continua com imagens e pistas visuais. Instale uma voz em português brasileiro nas configurações de fala do dispositivo.';
}
function stopSpeech() { if ('speechSynthesis' in window) speechSynthesis.cancel(); }
function speak(text) {
  stopSpeech(); refreshVoice();
  if (!prefs.sound || !voice) return false;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.voice = voice; utterance.lang = 'pt-BR'; utterance.rate = 0.82; utterance.pitch = 1.05;
  utterance.onerror = () => { const status = document.querySelector('#voice-status'); if (status) status.textContent = 'A voz não conseguiu falar. Confira a voz pt-BR do dispositivo; o apoio visual continua disponível.'; };
  speechSynthesis.speak(utterance); return true;
}
function persist() { storageOkay = saveState(deviceStorage, prefs, history); }
function recordPractice() {
  const item = history.find(h => h.word === round.entry.word);
  if (item) { item.practices = (item.practices || 1) + 1; item.lastSeen = Date.now(); }
  else history.push({ word: round.entry.word, level: round.entry.level, practices: 1, completed: 0, helped: 0, lastSeen: Date.now() });
  persist();
}
function finishIfNeeded() {
  if (!isComplete(round) || round.recorded) return;
  round.recorded = true; celebrating = true;
  const item = history.find(h => h.word === round.entry.word);
  if (item) { item.completed = (item.completed || 0) + 1; if (round.helped) item.helped = (item.helped || 0) + 1; }
  persist(); message = round.helped ? 'Descobrimos juntos! Cada letra conta.' : 'Você descobriu! Que linda conquista!';
  speak(`Muito bem! ${round.entry.audio}. Você descobriu a palavra!`);
}
function nextWord() {
  stopSpeech(); celebrating = false;
  const entry = deck.next(prefs);
  if (!entry) { screen = 'sequence'; round = null; render(); return; }
  round = createRound(entry); keys = keyboardFor(entry); screen = 'game';
  message = entry.level === 3 ? 'Uma pista para começar. Vamos descobrir?' : 'Toque nas letras para descobrir a palavra!';
  recordPractice(); render();
  if (entry.level === 1) speak(entry.audio);
}
function applyGuess(letter) {
  if (screen !== 'game' || !round || !keys.includes(baseLetter(letter))) return;
  const result = guess(round, letter); if (result.ignored) return;
  celebrating = false;
  if (result.correct) message = 'Essa letra está na palavra!';
  else message = 'Vamos tentar outra letra?';
  if (result.offerHelp && prefs.hints) {
    round.autoOffered = true;
    message = 'Vamos tentar outra letra? A Lili pode ajudar: toque em “Uma ajudinha”.';
    speak('Vamos tentar outra letra? Toque em Uma ajudinha para descobrir comigo.');
  }
  finishIfNeeded(); render();
}
function applyHint() {
  if (!prefs.hints || !round || isComplete(round)) return;
  const result = giveHint(round, keys);
  if (result === 'listen') { const spoken = speak(round.entry.audio); message = spoken ? 'Veja a imagem e ouça a palavra. Vamos juntos!' : 'Olhe a imagem. Toque de novo em “Uma ajudinha” para destacar letras.'; }
  if (result === 'highlight') message = 'Uma das letras com estrelinha está na palavra!';
  if (result === 'reveal') message = 'Uma letrinha apareceu! Podemos descobrir juntos.';
  finishIfNeeded(); render();
}
function header() {
  return `<header class="header"><button class="brand" id="home" aria-label="Voltar ao início"><span class="brand-mark">${icon('leaf')}</span><span>aventura<span class="brand-sub">DAS LETRAS</span></span></button><nav aria-label="Opções"><button class="icon-button" id="sound-toggle" aria-label="${prefs.sound ? 'Desligar' : 'Ligar'} sons" aria-pressed="${prefs.sound}" title="${prefs.sound ? 'Desligar' : 'Ligar'} sons">${icon(prefs.sound ? 'sound' : 'mute')}</button><button class="parent-button" id="parents">${icon('settings')}<span>Responsáveis</span></button></nav></header>`;
}
function welcome() {
  return `<main class="welcome"><div class="eyebrow">UM JARDIM CHEIO DE DESCOBERTAS</div><h1>Descubra<br>a <span>Palavra<span class="title-spark">✦</span></span></h1><p class="lead">Pequenas letras.<br>Grandes descobertas.</p><div class="welcome-card"><div class="welcome-picture">${mascot('welcome-mascot')}<span class="floating-letter letter-a" aria-hidden="true">A</span><span class="floating-letter letter-b" aria-hidden="true">B</span><span class="floating-letter letter-c" aria-hidden="true">C</span><span class="deco-star" aria-hidden="true">✦</span></div><div class="welcome-copy"><span class="mini-label">OI, EU SOU A LILI!</span><h2>Vamos brincar<br>com as letras?</h2><p>Veja, ouça e descubra uma palavra por vez. Eu ajudo você!</p><button class="primary" id="start">Vamos brincar ${icon('arrow')}</button><button class="text-button" id="instructions">${icon('sound')} Ouvir como brincar</button></div></div><div class="welcome-bottom"><span>${icon('heart')} Aqui, a gente aprende sem pressa.</span><button class="level-pill" id="choose-level">${icon('leaf')} ${LEVELS[prefs.level].name} <span>${icon('arrow')}</span></button></div></main>`;
}
function gameView() {
  const entry = round.entry, complete = isComplete(round);
  const used = new Set([...entry.word].map(baseLetter));
  return `<main class="game"><div class="game-top"><div><div class="eyebrow">A CADA LETRA, UMA DESCOBERTA</div><h1>Qual é a palavra?</h1></div><span class="level-pill">${icon('leaf')} ${LEVELS[prefs.level].name}</span></div><section class="play-card" aria-label="Descobrir uma palavra"><div class="picture-panel"><div class="category-label">${esc(CATEGORIES[entry.category])}</div><div class="picture-frame ${round.imageVisible || complete ? '' : 'hidden-picture'}">${round.imageVisible || complete ? `<img class="word-image" src="${esc(entry.image)}" alt="${complete ? esc(entry.word) : esc(entry.clue)}">` : `<div class="mystery" aria-label="Imagem disponível como ajuda">? <span>Um novo desafio!</span></div>`}</div>${entry.level === 3 && !complete ? `<p class="clue">${esc(entry.clue)}</p><div class="clue-buttons"><button class="text-button" id="hear-clue">${icon('sound')} Ouvir pista</button>${!round.imageVisible ? `<button class="text-button" id="show-image">${icon('eye')} Ver imagem</button>` : ''}</div>` : `<p class="picture-caption">${complete ? 'Olha só o que você descobriu!' : 'Olhe a imagem. Que palavra será?'}</p>`}<span class="picture-spark spark-one" aria-hidden="true">✦</span><span class="picture-spark spark-two" aria-hidden="true">✧</span></div><div class="letters-panel"><div class="round-label">${complete ? `${icon('check')} PALAVRA DESCOBERTA` : `${entry.word.length} LETRAS PARA DESCOBRIR`}</div><div class="word-slots ${complete ? 'complete' : ''} ${celebrating ? 'celebrate' : ''}" aria-label="${complete ? `Palavra completa: ${esc(entry.word)}` : 'Letras descobertas'}">${[...entry.word].map((letter, i) => `<span class="letter-slot ${round.guessed.has(baseLetter(letter)) ? 'revealed' : ''}" style="--letter-index:${i}" aria-label="${round.guessed.has(baseLetter(letter)) ? esc(letter) : 'letra ainda não descoberta'}">${round.guessed.has(baseLetter(letter)) ? esc(letter) : '<span aria-hidden="true">&nbsp;</span>'}</span>`).join('')}</div><div class="word-actions"><button class="secondary" id="hear-word">${icon('sound')} Ouvir palavra</button><button class="secondary hint-button ${round.autoOffered && round.hintStep === 0 ? 'offered' : ''}" id="hint" ${!prefs.hints || complete ? 'disabled' : ''}>${icon('help')} Uma ajudinha</button></div><div class="keyboard ${prefs.level === 1 ? 'small-keyboard' : ''}" role="group" aria-label="Letras para escolher">${keys.map(l => { const chosen = round.guessed.has(l), correct = used.has(l); return `<button class="key ${chosen ? correct ? 'correct' : 'tried' : ''} ${round.highlighted.includes(l) && !chosen ? 'highlighted' : ''}" data-letter="${l}" ${chosen || complete ? 'disabled' : ''} aria-label="Letra ${l}${chosen ? correct ? ', encontrada' : ', já tentamos' : round.highlighted.includes(l) ? ', pista' : ''}"><span>${l}</span><small aria-hidden="true">${chosen ? correct ? '✓' : '·' : round.highlighted.includes(l) ? '★' : ''}</small></button>`; }).join('')}</div>${complete ? `<button class="primary next-button" id="next">Próxima palavra ${icon('arrow')}</button>` : `<p class="keyboard-note">${prefs.level === 1 ? 'Toque em uma letrinha para começar.' : 'Toque nas letras ou use o teclado.'}</p>`}</div></section><div class="companion">${mascot()}<div><strong>${complete ? 'Uma descoberta para guardar!' : 'Estou aqui com você!'}</strong><p id="game-message" role="status" aria-live="polite">${esc(message)}</p></div>${complete ? '<span class="celebration-star" aria-hidden="true">✦</span>' : ''}</div><div class="game-foot"><span>${icon('heart')} No seu tempo, do seu jeitinho.</span><span>${deck.remaining(prefs)} ${deck.remaining(prefs) === 1 ? 'palavra esperando' : 'palavras esperando'}</span></div></main>`;
}
function sequenceView() {
  const hasWords = deck.eligible(prefs).length > 0;
  return `<main class="sequence">${mascot()}<div class="eyebrow">${hasWords ? 'UM JARDIM DE CONQUISTAS' : 'VAMOS ESCOLHER OUTRA CATEGORIA?'}</div><h1>${hasWords ? 'Que aventura linda!' : 'Mais descobertas esperam.'}</h1><p>${hasWords ? 'Você explorou todas as palavras desta seleção.<br>Vamos embaralhar e brincar mais um pouquinho?' : 'Este nível ainda não tem palavras nessa categoria. Escolha outra categoria na área dos responsáveis.'}</p>${hasWords ? `<button id="restart-sequence" class="primary">Brincar de novo ${icon('arrow')}</button>` : ''}<button id="sequence-settings" class="secondary">${icon('settings')} Escolher nível e categorias</button></main>`;
}
function render() {
  document.documentElement.dataset.reducedMotion = prefs.reducedMotion;
  app.innerHTML = header() + (screen === 'welcome' ? welcome() : screen === 'game' ? gameView() : sequenceView()) + `<footer class="footer"><span>Descubra a Palavra <span class="footer-dot">·</span> Aventura das Letras</span><span>Feito para aprender brincando</span></footer>` + garden;
  bind('parents', openParents); bind('choose-level', openParents); bind('sequence-settings', openParents);
  bind('home', () => { stopSpeech(); screen = 'welcome'; render(); });
  bind('sound-toggle', () => { prefs.sound = !prefs.sound; stopSpeech(); persist(); render(); });
  bind('start', () => { refreshVoice(); if (round && !isComplete(round)) { screen = 'game'; render(); if (round.entry.level === 1) speak(round.entry.audio); } else nextWord(); });
  bind('instructions', () => { openInstructions(); speak('Vamos brincar! Olhe a imagem. Toque nas letras para descobrir a palavra. Você pode ouvir a palavra ou pedir uma ajudinha. Não tem pressa!'); });
  bind('hear-word', () => { if (round.entry.level === 3 && !isComplete(round)) round.helped = true; const spoken = speak(round.entry.audio); if (!spoken) { message = prefs.sound ? 'A voz pt-BR não está disponível. A imagem ajuda você a descobrir!' : 'Os sons estão desligados. Use o botão de som para ligar.'; render(); } });
  bind('hear-clue', () => { if (!speak(round.entry.clue)) { message = prefs.sound ? 'A voz pt-BR não está disponível. A pista está escrita abaixo da imagem.' : 'Os sons estão desligados. Use o botão de som para ligar.'; render(); } });
  bind('show-image', () => { round.imageVisible = true; round.helped = true; message = 'Uma imagem para ajudar na descoberta!'; render(); });
  bind('hint', applyHint); bind('next', nextWord);
  bind('restart-sequence', () => { deck.restart(prefs); nextWord(); });
  document.querySelectorAll('[data-letter]').forEach(button => button.addEventListener('click', () => applyGuess(button.dataset.letter)));
}
function bind(id, fn) { document.getElementById(id)?.addEventListener('click', fn); }

function createDialog(content, label) {
  stopSpeech();
  const previousFocus = document.activeElement;
  const dialog = document.createElement('dialog'); dialog.className = 'modal'; dialog.setAttribute('aria-label', label);
  dialog.innerHTML = content;
  document.body.append(dialog);
  const close = () => { stopSpeech(); dialog.close(); };
  dialog.addEventListener('close', () => { dialog.remove(); previousFocus?.focus(); });
  dialog.addEventListener('click', event => { if (event.target === dialog) close(); });
  dialog.querySelectorAll('[data-close]').forEach(b => b.addEventListener('click', close));
  dialog.showModal(); return dialog;
}
function openInstructions() {
  createDialog(`<button class="modal-close icon-button" data-close aria-label="Fechar">${icon('close')}</button><div class="eyebrow">VAMOS JUNTOS</div><h2>É hora de descobrir!</h2><ol class="instructions"><li>Olhe a imagem ou a pista.</li><li>Toque nas letras que você acha que estão na palavra.</li><li>Ouça a palavra ou peça uma ajudinha.</li><li>Descobriu? Observe a palavra e toque em “Próxima palavra”.</li></ol><p>Se errar, tudo bem. A Lili está aqui para ajudar!</p><button class="primary" data-close>Entendi ${icon('check')}</button>`, 'Como brincar');
}
function openParents() {
  const complete = history.reduce((sum, h) => sum + (h.completed || 0), 0);
  const helped = history.reduce((sum, h) => sum + (h.helped || 0), 0);
  const dialog = createDialog(`<button class="modal-close icon-button" data-close aria-label="Fechar área dos responsáveis">${icon('close')}</button><div class="eyebrow">CUIDADO EM CADA DESCOBERTA</div><h2>Área dos responsáveis</h2><p class="modal-intro">Ajuste a aventura ao ritmo da criança. Sem mudança automática de nível.</p><form id="settings-form"><fieldset><legend>Nível da aventura</legend><div class="level-options">${Object.entries(LEVELS).map(([n,l]) => `<label class="level-option"><input type="radio" name="level" value="${n}" ${prefs.level === Number(n) ? 'checked' : ''}><span><strong>${l.icon} ${l.name}</strong><small>${l.description}</small></span></label>`).join('')}</div></fieldset><fieldset><legend>Categorias</legend><div class="category-options">${Object.entries(CATEGORIES).map(([value, label]) => `<label><input type="checkbox" name="category" value="${value}" ${prefs.categories.includes(value) ? 'checked' : ''}> ${label}</label>`).join('')}</div><p id="settings-error" class="form-error" role="alert"></p></fieldset><fieldset class="switches"><legend>Apoio e conforto</legend><label><span><strong>Áudio</strong><small>Palavras e instruções faladas</small></span><input type="checkbox" name="sound" ${prefs.sound ? 'checked' : ''}></label><label><span><strong>Pistas graduais</strong><small>Ouvir, destacar opções e revelar letras</small></span><input type="checkbox" name="hints" ${prefs.hints ? 'checked' : ''}></label><label><span><strong>Reduzir animações</strong><small>Uma experiência ainda mais tranquila</small></span><input type="checkbox" name="reducedMotion" ${prefs.reducedMotion ? 'checked' : ''}></label></fieldset><button type="submit" class="primary save-settings">Salvar preferências ${icon('check')}</button></form><section class="parent-section"><h3>O jardim de descobertas</h3><div class="stats"><div><strong>${history.length}</strong><span>palavras praticadas</span></div><div><strong>${complete}</strong><span>conclusões</span></div><div><strong>${helped}</strong><span>com ajuda</span></div></div>${history.length ? `<details><summary>Ver palavras praticadas</summary><ul class="history">${[...history].sort((a,b) => b.lastSeen - a.lastSeen).map(h => `<li><strong>${esc(h.word)}</strong><span>${h.completed ? `${h.completed} ${h.completed === 1 ? 'conclusão' : 'conclusões'}${h.helped ? ` · ${h.helped} com ajuda` : ''}` : 'Em descoberta'}</span></li>`).join('')}</ul></details>` : '<p>As primeiras descobertas vão aparecer aqui.</p>'}<button class="danger-button" id="reset-progress">Reiniciar progresso</button><div id="reset-confirm" hidden><p>Apagar todas as palavras praticadas e conclusões? As preferências serão mantidas.</p><div class="confirm-actions"><button class="danger-button" id="confirm-reset">Sim, apagar progresso</button><button class="secondary" id="cancel-reset">Cancelar</button></div></div><p id="reset-status" role="status"></p></section><section class="parent-section"><h3>Sobre o áudio e a escrita</h3><p id="voice-status">${esc(voiceStatus())}</p><button class="text-button" id="test-voice">${icon('sound')} Testar voz em português</button><p>O nome de uma letra é diferente dos sons que ela pode representar. O jogo fala as palavras inteiras e não apresenta nomes de letras como fonemas.</p><p>No primeiro nível, usamos palavras sem acentos. Nos demais, a letra-base revela a grafia correta: A revela Á, Ã ou Â; C não revela Ç, que tem uma tecla própria. Não usamos divisão silábica automática.</p><p>“Uma ajudinha”, a imagem e o áudio do nível 3 contam como ajuda. As pistas automáticas só são oferecidas se as pistas graduais estiverem ativadas. Imagem e voz continuam disponíveis como apoio no nível 3.</p></section><section class="parent-section"><h3>Privacidade e armazenamento</h3><p>Sem conta, anúncios, compras ou envio de progresso. Preferências e descobertas ficam neste navegador. Limpar os dados do navegador apaga esse registro. A voz é fornecida pelo sistema; algumas vozes precisam de internet.</p>${!storageOkay ? '<p class="form-error">O navegador bloqueou o salvamento. O jogo funciona, mas o progresso desta visita pode não ser mantido.</p>' : ''}</section>`, 'Área dos responsáveis');
  dialog.querySelector('#settings-form').addEventListener('submit', event => {
    event.preventDefault(); const form = new FormData(event.target);
    const categories = form.getAll('category');
    if (!categories.length) { dialog.querySelector('#settings-error').textContent = 'Escolha pelo menos uma categoria.'; return; }
    const changed = Number(form.get('level')) !== prefs.level || [...categories].sort().join() !== [...prefs.categories].sort().join();
    prefs = { level: Number(form.get('level')), categories, sound: form.has('sound'), hints: form.has('hints'), reducedMotion: form.has('reducedMotion') };
    stopSpeech(); persist();
    if (!prefs.hints && round) round.highlighted = [];
    dialog.close(); if (changed && screen !== 'welcome') nextWord(); else render();
  });
  dialog.querySelector('#test-voice').addEventListener('click', () => { speak('Olá! Vamos descobrir uma palavra juntos?'); });
  dialog.querySelector('#reset-progress').addEventListener('click', () => { dialog.querySelector('#reset-confirm').hidden = false; });
  dialog.querySelector('#cancel-reset').addEventListener('click', () => { dialog.querySelector('#reset-confirm').hidden = true; });
  dialog.querySelector('#confirm-reset').addEventListener('click', () => { history = []; persist(); deck = new WordDeck(words); round = null; screen = 'welcome'; dialog.close(); render(); openParents(); });
}

document.addEventListener('keydown', event => {
  if (document.querySelector('dialog[open]') || event.altKey || event.ctrlKey || event.metaKey || event.repeat || event.key.length !== 1) return;
  if ([...ALPHABET, 'Ç'].includes(baseLetter(event.key))) { event.preventDefault(); applyGuess(event.key); }
});
if ('speechSynthesis' in window) speechSynthesis.addEventListener('voiceschanged', refreshVoice);
refreshVoice();
try {
  const response = await fetch('/content/words.json');
  if (!response.ok) throw new Error('Não foi possível carregar as palavras.');
  words = await response.json(); deck = new WordDeck(words); render();
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {});
} catch {
  app.innerHTML = `<main class="sequence"><h1>O jardim está quase pronto.</h1><p>Não foi possível carregar as palavras. Confira a conexão na primeira visita e tente de novo.</p><button class="primary" id="retry">Tentar novamente</button></main>`;
  bind('retry', () => location.reload());
}
