export const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
export const LEVELS = {
  1: { name: 'Primeiros passos', description: '40 palavras curtinhas, imagem e voz para começar. De 6 a 8 letras para escolher.', icon: '🌱' },
  2: { name: 'Descobrindo letras', description: '35 palavras com imagem e teclado completo. Ouça sempre que quiser.', icon: '🌼' },
  3: { name: 'Novo desafio', description: '25 palavras com uma pista inicial. A imagem e a voz estão aqui para ajudar.', icon: '🦋' },
};
export const CATEGORIES = { animais: 'Animais', alimentos: 'Alimentos', brinquedos: 'Brinquedos', casa: 'Objetos de casa', natureza: 'Natureza' };
export const DEFAULT_PREFS = { level: 1, categories: Object.keys(CATEGORIES), sound: true, hints: true, reducedMotion: false };
export function baseLetter(letter) {
  return letter.toUpperCase() === 'Ç' ? 'Ç' : letter.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase();
}
export function shuffle(items, random = Math.random) {
  const result = [...items];
  for (let i = result.length - 1; i > 0; i--) { const j = Math.floor(random() * (i + 1)); [result[i], result[j]] = [result[j], result[i]]; }
  return result;
}
export function keyboardFor(entry, random = Math.random) {
  const needed = [...new Set([...entry.word].map(baseLetter))];
  if (entry.level !== 1) return [...ALPHABET, ...(needed.includes('Ç') ? ['Ç'] : [])];
  const distractors = shuffle([...ALPHABET].filter(l => !needed.includes(l)), random);
  return shuffle([...needed, ...distractors.slice(0, 8 - needed.length)], random);
}
export function createRound(entry) {
  return { entry, guessed: new Set(), wrong: 0, helped: false, hintStep: 0, highlighted: [], imageVisible: entry.level !== 3, autoOffered: false };
}
export function missingLetters(round) { return [...new Set([...round.entry.word].map(baseLetter))].filter(l => !round.guessed.has(l)); }
export function isComplete(round) { return missingLetters(round).length === 0; }
export function guess(round, letter) {
  letter = baseLetter(letter);
  if (isComplete(round) || round.guessed.has(letter) || ![...ALPHABET, 'Ç'].includes(letter)) return { ignored: true };
  round.guessed.add(letter);
  const correct = [...round.entry.word].some(l => baseLetter(l) === letter);
  if (!correct) round.wrong++;
  return { correct, complete: isComplete(round), offerHelp: !correct && round.wrong >= 3 && !round.autoOffered };
}
export function giveHint(round, keys, random = Math.random) {
  if (isComplete(round)) return 'complete';
  round.helped = true;
  round.hintStep++;
  round.imageVisible = true;
  if (round.hintStep === 1) return 'listen';
  if (round.hintStep === 2) {
    const needed = shuffle(missingLetters(round), random)[0];
    const other = shuffle(keys.filter(l => l !== needed && !round.guessed.has(l)), random).slice(0, 2);
    round.highlighted = shuffle([needed, ...other], random);
    return 'highlight';
  }
  round.guessed.add(missingLetters(round)[0]);
  round.highlighted = [];
  return 'reveal';
}
export class WordDeck {
  constructor(words, random = Math.random) { this.words = words; this.random = random; this.seen = new Set(); }
  key(prefs) { return `${prefs.level}:${[...prefs.categories].sort().join(',')}`; }
  eligible(prefs) { return this.words.filter(w => w.level === prefs.level && prefs.categories.includes(w.category)); }
  next(prefs) {
    const available = this.eligible(prefs).filter(w => !this.seen.has(w.word));
    if (!available.length) return null;
    const entry = shuffle(available, this.random)[0];
    this.seen.add(entry.word);
    return entry;
  }
  restart(prefs) { for (const word of this.eligible(prefs)) this.seen.delete(word.word); }
  remaining(prefs) { return this.eligible(prefs).filter(w => !this.seen.has(w.word)).length; }
}
export function loadSaved(storage) {
  try {
    const data = JSON.parse(storage.getItem('aventura-letras-v1') || '{}');
    const p = data.prefs || {};
    return { prefs: { ...DEFAULT_PREFS, level: [1, 2, 3].includes(p.level) ? p.level : 1,
      categories: Array.isArray(p.categories) && p.categories.some(c => CATEGORIES[c]) ? p.categories.filter(c => CATEGORIES[c]) : [...DEFAULT_PREFS.categories],
      sound: p.sound !== false, hints: p.hints !== false, reducedMotion: p.reducedMotion === true },
      history: Array.isArray(data.history) ? data.history.filter(h => typeof h.word === 'string' && [1, 2, 3].includes(h.level)) : [] };
  } catch { return { prefs: { ...DEFAULT_PREFS, categories: [...DEFAULT_PREFS.categories] }, history: [] }; }
}
export function saveState(storage, prefs, history) {
  try { storage.setItem('aventura-letras-v1', JSON.stringify({ prefs, history })); return true; } catch { return false; }
}
