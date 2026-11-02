"""Functional browser checks. Run with: python tests/browser_smoke.py

Requires Playwright and Chromium. The speech API is mocked only to verify call
order and mute behavior; this does not validate a real installed pt-BR voice.
"""
import json
import os
import unicodedata
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = os.environ.get('GAME_URL', 'http://127.0.0.1:5173')
OUT = Path('artifacts')
OUT.mkdir(exist_ok=True)

MOCK_VOICE = """
window.__speech = [];
window.__cancel = 0;
window.__speechOrder = [];
window.SpeechSynthesisUtterance = class { constructor(text) { this.text = text; } };
Object.defineProperty(window, 'speechSynthesis', {value: {
  getVoices() { return [{lang:'pt-BR', name:'Voz de teste', localService:true}]; },
  cancel() { window.__cancel++; window.__speechOrder.push('cancel'); },
  speak(utterance) { window.__speech.push(utterance.text); window.__speechOrder.push('speak'); },
  addEventListener() {},
}});
"""

def base_letter(letter):
    if letter == 'Ç':
        return letter
    return ''.join(c for c in unicodedata.normalize('NFD', letter) if not unicodedata.combining(c))

def current_word(page):
    return page.evaluate("JSON.parse(localStorage.getItem('aventura-letras-v1')).history.reduce((a,b)=>a.lastSeen>b.lastSeen?a:b).word")

def state(page):
    return page.evaluate("JSON.parse(localStorage.getItem('aventura-letras-v1'))")

def choose_level(page, level):
    page.locator('#parents').click()
    page.locator(f'input[name=level][value="{level}"]').check()
    page.get_by_role('button', name='Salvar preferências').click()

def complete_manually(page):
    word = current_word(page)
    for letter in dict.fromkeys(base_letter(l) for l in word):
        key = page.locator(f'[data-letter="{letter}"]')
        if key.is_enabled():
            key.click()
    assert page.locator('.word-slots').inner_text().replace('\n', '') == word
    assert page.locator('#next').is_visible()
    return word

def assert_no_overflow(page, label):
    metrics = page.evaluate("({page:document.documentElement.scrollWidth,viewport:innerWidth})")
    assert metrics['page'] <= metrics['viewport'], (label, metrics)

checks = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
    context = browser.new_context(viewport={'width':1280, 'height':900}, locale='pt-BR', reduced_motion='reduce')
    context.add_init_script(MOCK_VOICE)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(BASE, wait_until='networkidle')
    assert page.locator('#start').is_visible()
    page.screenshot(path=str(OUT/'web-inicio.png'), full_page=True)
    assert_no_overflow(page, 'desktop início')
    checks.append('Tela inicial desktop sem overflow')

    page.locator('#instructions').click()
    assert page.get_by_role('dialog').is_visible()
    assert page.evaluate('window.__speechOrder.slice(-1)[0]') == 'speak', 'Instruções não podem ser canceladas pela abertura do modal'
    assert 'Vamos brincar' in page.evaluate('window.__speech.at(-1)')
    page.get_by_role('button', name='Entendi').click()
    checks.append('Instruções faladas após abrir modal (síntese simulada)')

    page.locator('#start').click()
    assert page.locator('.key').count() == 8
    assert page.locator('.word-image').is_visible()
    assert page.locator('#next').count() == 0
    assert page.evaluate('window.__speech.length') >= 2
    word = current_word(page)
    needed = {base_letter(l) for l in word}
    available = page.locator('.key').evaluate_all('(keys)=>keys.map(k=>k.dataset.letter)')
    wrong = [l for l in available if l not in needed]
    for letter in wrong[:3]:
        page.locator(f'[data-letter="{letter}"]').click()
    assert page.locator('.key.tried').count() == 3
    assert 'Uma ajudinha' in page.locator('#game-message').inner_text()
    page.keyboard.press(wrong[0].lower())
    assert page.locator('.key.tried').count() == 3
    checks.append('Primeiro nível: 8 teclas, bloqueio de repetição e apoio após 3 erros')

    page.locator('#hint').click()
    assert page.locator('.key.highlighted').count() == 0
    page.locator('#hint').click()
    assert 1 <= page.locator('.key.highlighted').count() <= 3
    for _ in range(8):
        if page.locator('#next').count():
            break
        page.locator('#hint').click()
    assert page.locator('#next').is_visible()
    assert page.locator('.word-slots').inner_text().replace('\n','') == word
    page.wait_for_timeout(500)
    assert current_word(page) == word, 'Não deve avançar automaticamente'
    assert state(page)['history'][0]['completed'] == 1
    assert state(page)['history'][0]['helped'] == 1
    page.screenshot(path=str(OUT/'web-desktop.png'), full_page=True)
    checks.append('Pistas graduais, conclusão assistida e espera por Próxima palavra')

    for width in [390, 320]:
        page.set_viewport_size({'width':width, 'height':844 if width == 390 else 740})
        assert_no_overflow(page, f'mobile {width}')
        if width == 390:
            page.screenshot(path=str(OUT/'web-celular.png'), full_page=True)
    checks.append('Tela de jogo em 390 e 320 px sem overflow horizontal')

    page.reload(wait_until='networkidle')
    assert state(page)['history'][0]['completed'] == 1
    assert state(page)['history'][0]['helped'] == 1
    checks.append('Persistência do progresso após recarregar')

    choose_level(page, 3)
    page.locator('#start').click()
    assert page.locator('.mystery').is_visible()
    assert page.locator('.clue').inner_text().strip()
    assert page.locator('.key').count() in [26, 27]
    page.locator('#show-image').click()
    assert page.locator('.word-image').is_visible()
    page.set_viewport_size({'width':390, 'height':844})
    assert_no_overflow(page, 'mobile nível 3')
    page.screenshot(path=str(OUT/'web-celular-nivel3.png'), full_page=True)
    page.locator('#hear-clue').click()
    assert page.evaluate('window.__speechOrder.slice(-2)') == ['cancel', 'speak']
    calls = page.evaluate('window.__speech.length')
    page.locator('#sound-toggle').click()
    page.locator('#hear-word').click()
    assert page.evaluate('window.__speech.length') == calls
    assert state(page)['prefs']['sound'] is False
    checks.append('Nível 3: pista, imagem como ajuda, stop antes de fala e silenciar')

    page.locator('#parents').click()
    page.locator('input[name=hints]').uncheck()
    page.locator('input[name=reducedMotion]').check()
    page.get_by_role('button', name='Salvar preferências').click()
    assert page.locator('#hint').is_disabled()
    assert page.locator('html').get_attribute('data-reduced-motion') == 'true'
    checks.append('Preferências de pistas e animações aplicadas')

    complete_manually(page)
    page.locator('#parents').click()
    page.locator('#reset-progress').click()
    page.locator('#cancel-reset').click()
    assert len(state(page)['history']) >= 2
    page.locator('#reset-progress').click()
    page.locator('#confirm-reset').click()
    assert state(page)['history'] == []
    assert state(page)['prefs']['level'] == 3
    assert state(page)['prefs']['sound'] is False
    checks.append('Reinício exige confirmação e mantém preferências')
    page.get_by_role('button', name='Fechar área dos responsáveis').click()

    # Category form must reject an empty selection.
    page.locator('#parents').click()
    for checkbox in page.locator('input[name=category]').all():
        checkbox.uncheck()
    page.get_by_role('button', name='Salvar preferências').click()
    assert 'pelo menos uma' in page.locator('#settings-error').inner_text()
    page.locator('input[name=category][value=animais]').check()
    page.get_by_role('button', name='Salvar preferências').click()
    page.locator('#start').click()
    assert page.locator('.category-label').inner_text().casefold() == 'animais'
    assert current_word(page)
    checks.append('Seleção de categorias validada e aplicada')

    page.evaluate('navigator.serviceWorker.ready')
    context.set_offline(True)
    page.reload(wait_until='networkidle')
    assert page.locator('#start').is_visible()
    page.locator('#start').click()
    assert page.locator('.key').count() in [26, 27]
    assert page.locator('.clue').inner_text()
    context.set_offline(False)
    checks.append('Web offline após cache completo da primeira visita')
    assert not errors, errors

    # Real system voice availability is recorded, not asserted or fabricated.
    real = browser.new_context(viewport={'width':390, 'height':844}, locale='pt-BR')
    real_page = real.new_page()
    real_page.goto(BASE, wait_until='networkidle')
    real_page.locator('#parents').click()
    voice_note = real_page.locator('#voice-status').inner_text()
    real.close()

    no_voice = browser.new_context(viewport={'width':320, 'height':740}, locale='pt-BR')
    no_voice.add_init_script("Object.defineProperty(window, 'speechSynthesis', {value:{getVoices:()=>[],cancel(){},speak(){throw Error('Não deve falar sem voz pt-BR');},addEventListener(){}}});")
    no_voice_page = no_voice.new_page()
    no_voice_page.goto(BASE, wait_until='networkidle')
    no_voice_page.locator('#start').click()
    no_voice_page.locator('#hear-word').click()
    assert 'não está disponível' in no_voice_page.locator('#game-message').inner_text()
    assert no_voice_page.locator('.word-image').is_visible()
    complete_manually(no_voice_page)
    assert_no_overflow(no_voice_page, 'sem voz em 320 px')
    no_voice.close()
    checks.append('Sem voz pt-BR: aviso visual, imagem, teclas e conclusão continuam funcionando')
    browser.close()

report = {'passed':len(checks), 'checks':checks, 'real_voice_status':voice_note,
          'audio_test_note':'Chamadas de síntese simuladas verificam lógica, não reprodução de voz real.'}
(OUT/'browser-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False, indent=2))
