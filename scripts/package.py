#!/usr/bin/env python3
"""Package tested web, native APK and sources without caches or private keys."""
import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts'
APK = ROOT / 'android/app/build/outputs/apk/debug/aventura-das-letras-debug.apk'
OUT.mkdir(exist_ok=True)
if not APK.is_file() or not (ROOT / 'dist/index.html').is_file():
    raise SystemExit('Primeiro execute npm run build e bash scripts/build-android.sh.')

words = json.loads((ROOT / 'public/content/words.json').read_text())
with ZipFile(APK) as archive:
    for relative in ['content/words.json'] + [w['image'].lstrip('/') for w in words]:
        if archive.read('assets/' + relative) != (ROOT / 'public' / relative).read_bytes():
            raise SystemExit('APK desatualizado: recompile antes de empacotar.')

shutil.copyfile(APK, OUT / 'aventura-das-letras-android.apk')
with ZipFile(OUT / 'aventura-das-letras-web.zip', 'w', ZIP_DEFLATED) as archive:
    for file in sorted((ROOT / 'dist').rglob('*')):
        if file.is_file(): archive.write(file, file.relative_to(ROOT))
    archive.write(ROOT / 'scripts/serve.mjs', 'scripts/serve.mjs')
    archive.writestr('package.json', json.dumps({'name':'aventura-das-letras-web','private':True,'type':'module','scripts':{'start':'node scripts/serve.mjs --dist'},'engines':{'node':'>=20'}}, indent=2))
    archive.writestr('LEIA-ME.txt', 'AVENTURA DAS LETRAS — VERSÃO WEB\n\nRequer Node.js 20+. Extraia toda a pasta, abra um terminal nela e execute:\n\nnpm start\n\nAbra http://localhost:5173 no navegador. Não precisa de npm install.\nPara publicar, hospede o conteúdo de dist/ na raiz de um domínio HTTPS.\nO modo offline exige a primeira visita online e o cache completo.\nA fala depende da disponibilidade de voz pt-BR no dispositivo.\n')

with ZipFile(OUT / 'aventura-das-letras-fontes.zip', 'w', ZIP_DEFLATED) as archive:
    selected = ['src','public','scripts','tests','android']
    ignored = {'build','.gradle','__pycache__'}
    for folder in selected:
        for file in sorted((ROOT / folder).rglob('*')):
            relative = file.relative_to(ROOT)
            if file.is_file() and not any(part in ignored for part in relative.parts) and file.name != 'local.properties':
                archive.write(file, relative)
    for file in ['README.md','VALIDACAO.md','package.json','.gitignore','index.html']:
        archive.write(ROOT / file, file)

files = [OUT / name for name in ['aventura-das-letras-android.apk','aventura-das-letras-web.zip','aventura-das-letras-fontes.zip']]
checksums = '\n'.join(hashlib.sha256(file.read_bytes()).hexdigest() + '  ' + file.name for file in files) + '\n'
(OUT / 'SHA256SUMS.txt').write_text(checksums)
for file in files:
    if file.suffix == '.zip':
        with ZipFile(file) as archive:
            assert archive.testzip() is None
    print(f'{file.name}: {file.stat().st_size:,} bytes')
