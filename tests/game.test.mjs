import test from 'node:test';
import assert from 'node:assert/strict';
import { ALPHABET, DEFAULT_PREFS, baseLetter, createRound, giveHint, guess, isComplete, keyboardFor, loadSaved, missingLetters, saveState, shuffle, WordDeck } from '../src/game.js';

const entry = (word = 'BANANA', level = 3, category = 'alimentos') => ({ word, level, category });
const fixedRandom = () => 0.37;

test('normaliza acentos sem confundir C e Ç', () => {
  for (const letter of ['a', 'Á', 'Ã', 'Â']) assert.equal(baseLetter(letter), 'A');
  assert.equal(baseLetter('ç'), 'Ç');
  assert.equal(baseLetter('C'), 'C');
});

test('revela todas as ocorrências de letras repetidas e ignora a segunda tentativa', () => {
  const round = createRound(entry());
  assert.equal(guess(round, 'A').correct, true);
  assert.deepEqual(missingLetters(round), ['B', 'N']);
  assert.equal([...round.entry.word].filter(l => round.guessed.has(baseLetter(l))).length, 3);
  assert.deepEqual(guess(round, 'a'), { ignored: true });
  assert.equal(round.guessed.size, 1);
  assert.equal(round.wrong, 0);
});

test('oferece apoio após três erros sem encerrar a rodada ou contar erros repetidos', () => {
  const round = createRound(entry());
  assert.equal(guess(round, 'X').offerHelp, false);
  assert.equal(guess(round, 'Y').offerHelp, false);
  assert.equal(guess(round, 'Z').offerHelp, true);
  assert.deepEqual(guess(round, 'Z'), { ignored: true });
  assert.equal(round.wrong, 3);
  assert.equal(isComplete(round), false);
  round.autoOffered = true;
  assert.equal(guess(round, 'Q').offerHelp, false);
  for (const l of ['B', 'A', 'N']) guess(round, l);
  assert.equal(isComplete(round), true);
  assert.deepEqual(guess(round, 'K'), { ignored: true });
});

test('pistas são graduais e permitem concluir com ajuda sem fim por erros', () => {
  const round = createRound(entry());
  const keys = keyboardFor(round.entry);
  assert.equal(round.imageVisible, false);
  assert.equal(giveHint(round, keys, fixedRandom), 'listen');
  assert.equal(round.imageVisible, true);
  assert.equal(round.helped, true);
  assert.equal(round.guessed.size, 0);
  assert.equal(giveHint(round, keys, fixedRandom), 'highlight');
  assert.ok(round.highlighted.some(l => missingLetters(round).includes(l)));
  assert.ok(round.highlighted.length <= 3);
  assert.equal(giveHint(round, keys, fixedRandom), 'reveal');
  assert.equal(round.guessed.size, 1);
  for (let i = 0; i < 10 && !isComplete(round); i++) giveHint(round, keys, fixedRandom);
  assert.equal(isComplete(round), true);
  assert.equal(giveHint(round, keys), 'complete');
});

test('letra-base revela acentos enquanto Ç tem sua própria tecla', () => {
  const round = createRound(entry('MAÇÃ', 2));
  const keys = keyboardFor(round.entry);
  assert.ok(keys.includes('Ç'));
  guess(round, 'A');
  assert.equal(round.guessed.has(baseLetter('Ã')), true);
  assert.equal(guess(round, 'C').correct, false);
  guess(round, 'M');
  assert.equal(isComplete(round), false);
  guess(round, 'Ç');
  assert.equal(isComplete(round), true);
});

test('primeiro nível tem 6–8 teclas distintas e todas as letras necessárias', () => {
  for (const word of ['UVA', 'OVO', 'LUA', 'BOLA', 'CASA', 'GATO', 'PATO', 'SAPO']) {
    const keys = keyboardFor(entry(word, 1), fixedRandom);
    assert.ok(keys.length >= 6 && keys.length <= 8);
    assert.equal(new Set(keys).size, keys.length);
    for (const letter of word) assert.ok(keys.includes(letter));
  }
  assert.deepEqual(keyboardFor(entry('GATO', 2)), [...ALPHABET]);
});

test('fila nunca repete antes de esgotar e só recomeça explicitamente', () => {
  const words = [entry('UVA', 1), entry('OVO', 1), entry('GATO', 1, 'animais'), entry('BANANA', 3)];
  const prefs = { ...DEFAULT_PREFS, categories: ['alimentos'] };
  const deck = new WordDeck(words, fixedRandom);
  const first = deck.next(prefs), second = deck.next(prefs);
  assert.notEqual(first.word, second.word);
  assert.equal(deck.next(prefs), null);
  assert.equal(deck.remaining(prefs), 0);
  const animals = { ...prefs, categories: ['animais'] };
  assert.equal(deck.next(animals).word, 'GATO');
  assert.equal(deck.next(prefs), null, 'trocar e voltar mantém a sequência esgotada');
  deck.restart(prefs);
  assert.equal(deck.remaining(prefs), 2);
  assert.ok(deck.next(prefs));
});

test('ordem de categorias não reinicia a fila e embaralhar não altera original', () => {
  const deck = new WordDeck([], fixedRandom);
  assert.equal(deck.key({ level: 1, categories: ['animais', 'casa'] }), deck.key({ level: 1, categories: ['casa', 'animais'] }));
  const original = ['A', 'B', 'C'];
  assert.equal(shuffle(original, fixedRandom).length, 3);
  assert.deepEqual(original, ['A', 'B', 'C']);
});

test('trocar filtros sobrepostos preserva palavras já praticadas na sessão', () => {
  const deck = new WordDeck([entry('UVA', 1), entry('OVO', 1), entry('GATO', 1, 'animais')], fixedRandom);
  const food = { ...DEFAULT_PREFS, categories: ['alimentos'] };
  const all = { ...DEFAULT_PREFS, categories: ['alimentos', 'animais'] };
  const first = deck.next(food);
  const following = [deck.next(all), deck.next(all)];
  assert.ok(following.every(w => w.word !== first.word));
  assert.equal(new Set([first.word, ...following.map(w => w.word)]).size, 3);
  assert.equal(deck.next(all), null);
  deck.restart(food);
  assert.equal(deck.remaining(food), 2);
  assert.equal(deck.remaining(all), 2, 'reinício de alimentos não repete animal já praticado');
});

test('preferências e histórico sobrevivem ao armazenamento e dados inválidos têm fallback', () => {
  let stored;
  const storage = { getItem: () => stored, setItem: (_, value) => { stored = value; } };
  const prefs = { ...DEFAULT_PREFS, level: 3, sound: false, reducedMotion: true };
  const history = [{ word: 'BANANA', level: 3, completed: 1, helped: 1 }];
  assert.equal(saveState(storage, prefs, history), true);
  assert.deepEqual(loadSaved(storage), { prefs, history });
  stored = '{invalid';
  assert.deepEqual(loadSaved(storage).prefs, DEFAULT_PREFS);
  stored = JSON.stringify({ prefs: { level: 100, categories: ['invalid'] }, history: [] });
  assert.equal(loadSaved(storage).prefs.level, 1);
  assert.deepEqual(loadSaved(storage).prefs.categories, DEFAULT_PREFS.categories);
  assert.equal(saveState({setItem: () => {throw Error('blocked');}}, prefs, history), false);
});
