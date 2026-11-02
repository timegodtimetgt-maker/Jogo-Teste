import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { CATEGORIES, baseLetter, createRound, giveHint, guess, isComplete, keyboardFor } from '../src/game.js';

const words = JSON.parse(await readFile(new URL('../public/content/words.json', import.meta.url), 'utf8'));

test('banco tem exatamente 100 palavras únicas, distribuídas em 40/35/25', () => {
  assert.equal(words.length, 100);
  assert.equal(new Set(words.map(w => w.word)).size, 100);
  assert.deepEqual([1, 2, 3].map(level => words.filter(w => w.level === level).length), [40, 35, 25]);
});

test('tamanho, grafia, categoria e metadados são válidos para todas as palavras', () => {
  const lengths = { 1: [3, 4], 2: [4, 5], 3: [5, 6] };
  for (const w of words) {
    assert.match(w.word, /^[A-ZÁÀÂÃÉÊÍÓÔÕÚÜÇ]+$/u, w.word);
    assert.ok(lengths[w.level].includes([...w.word].length), `${w.word}: tamanho do nível ${w.level}`);
    if (w.level === 1) assert.match(w.word, /^[A-Z]+$/, `${w.word}: primeiro nível sem acentos`);
    assert.ok(Object.hasOwn(CATEGORIES, w.category), w.word);
    assert.ok(typeof w.clue === 'string' && w.clue.length >= 10, `${w.word}: pista`);
    assert.ok(typeof w.audio === 'string' && w.audio.length >= 3, `${w.word}: áudio`);
    assert.match(w.image, /^\/images\/[a-z0-9-]+\.png$/, `${w.word}: imagem local PNG`);
  }
});

test('cada palavra tem uma imagem PNG válida de dimensões confortáveis', async () => {
  assert.equal(new Set(words.map(w => w.image)).size, 100);
  for (const w of words) {
    const png = await readFile(new URL(`../public${w.image}`, import.meta.url));
    assert.equal(png.subarray(0, 8).toString('hex'), '89504e470d0a1a0a', w.word);
    assert.ok(png.readUInt32BE(16) >= 300 && png.readUInt32BE(20) >= 200, w.word);
  }
});

test('todas as 100 palavras podem ser concluídas pelas teclas disponíveis e por ajuda', () => {
  for (const w of words) {
    const keys = keyboardFor(w, () => .37);
    if (w.level === 1) assert.ok(keys.length >= 6 && keys.length <= 8, w.word);
    for (const letter of [...w.word].map(baseLetter)) assert.ok(keys.includes(letter), `${w.word}: ${letter}`);
    const manual = createRound(w);
    for (const key of keys) guess(manual, key);
    assert.equal(isComplete(manual), true, w.word);
    const assisted = createRound(w);
    for (let i = 0; i < w.word.length + 3 && !isComplete(assisted); i++) giveHint(assisted, keys);
    assert.equal(isComplete(assisted), true, `${w.word}: ajuda`);
    assert.equal(assisted.helped, true);
  }
});
