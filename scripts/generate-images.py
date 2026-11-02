#!/usr/bin/env python3
"""Banco revisado e ilustrações originais. Execute com Python 3 e Inkscape.

Cada imagem é desenhada como SVG e exportada a PNG, sem fontes ou downloads.
Edite CONTENT para alterar o texto e ART para alterar o desenho correspondente.
"""
import json
import re
import subprocess
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public/images'
CONTENT = [
    ('UVA', 1, 'alimentos', 'Frutinhas que crescem juntas em um cacho.'),
    ('OVO', 1, 'alimentos', 'Tem casca por fora e uma gema por dentro.'),
    ('LUA', 1, 'natureza', 'Brilha no céu durante a noite.'),
    ('SOL', 1, 'natureza', 'Ilumina e aquece o nosso dia.'),
    ('MAR', 1, 'natureza', 'Tem água salgada e muitas ondas.'),
    ('RIO', 1, 'natureza', 'Um caminho de água que corre pela natureza.'),
    ('AVE', 1, 'animais', 'Tem penas, bico e duas asas.'),
    ('ASA', 1, 'animais', 'A parte do pássaro que se abre para voar.'),
    ('BOI', 1, 'animais', 'Animal grande da fazenda, com chifres.'),
    ('BOLA', 1, 'brinquedos', 'É redonda e podemos chutar ou jogar.'),
    ('CASA', 1, 'casa', 'Um lugar com portas e janelas onde podemos morar.'),
    ('GATO', 1, 'animais', 'Faz miau e tem bigodes.'),
    ('PATO', 1, 'animais', 'Faz quá-quá e gosta de nadar.'),
    ('SAPO', 1, 'animais', 'Pula perto da água e faz coaxo.'),
    ('RATO', 1, 'animais', 'Pequeno animal com bigodes e um rabo comprido.'),
    ('LOBO', 1, 'animais', 'Parece um cachorro e gosta de uivar.'),
    ('FOCA', 1, 'animais', 'Animal que nada no mar e tem nadadeiras.'),
    ('VELA', 1, 'casa', 'Tem um pavio e pode iluminar com sua chama.'),
    ('MESA', 1, 'casa', 'Tem um tampo onde apoiamos pratos e objetos.'),
    ('COPO', 1, 'casa', 'Usamos para beber água ou suco.'),
    ('CAMA', 1, 'casa', 'É onde deitamos para dormir.'),
    ('POTE', 1, 'casa', 'Um recipiente com tampa para guardar coisas.'),
    ('LATA', 1, 'casa', 'Uma embalagem de metal, como a de milho.'),
    ('FACA', 1, 'casa', 'Um adulto usa este talher para cortar alimentos.'),
    ('MALA', 1, 'casa', 'Guarda as roupas que levamos em uma viagem.'),
    ('BULE', 1, 'casa', 'Tem uma alça e um bico para servir chá.'),
    ('DADO', 1, 'brinquedos', 'Um cubinho com bolinhas usado em jogos.'),
    ('PIPA', 1, 'brinquedos', 'Sobe no céu presa a uma linha.'),
    ('BOTA', 1, 'casa', 'Um calçado que cobre o pé e parte da perna.'),
    ('MEIA', 1, 'casa', 'Veste o pé antes de colocar o sapato.'),
    ('LUVA', 1, 'casa', 'Veste a mão e tem lugar para os dedos.'),
    ('TUBO', 1, 'casa', 'Uma peça comprida e oca por onde pode passar água.'),
    ('CUBO', 1, 'brinquedos', 'Um bloco com seis faces quadradas.'),
    ('VACA', 1, 'animais', 'Animal da fazenda que nos dá leite.'),
    ('SUCO', 1, 'alimentos', 'Bebida que pode ser feita espremendo frutas.'),
    ('BOLO', 1, 'alimentos', 'Pode ter cobertura e velinhas no aniversário.'),
    ('COCO', 1, 'alimentos', 'Tem casca dura marrom e polpa branquinha.'),
    ('BALA', 1, 'alimentos', 'Um docinho pequeno que vem em uma embalagem torcida nas pontas.'),
    ('NAVE', 1, 'brinquedos', 'Um veículo de faz de conta para viajar no espaço.'),
    ('LUPA', 1, 'casa', 'Uma lente com cabo que faz as coisas parecerem maiores.'),
    ('PEIXE', 2, 'animais', 'Vive na água e nada com suas nadadeiras.'),
    ('URSO', 2, 'animais', 'Animal grande e peludo com orelhas redondas.'),
    ('TIGRE', 2, 'animais', 'Um grande felino alaranjado com listras escuras.'),
    ('ZEBRA', 2, 'animais', 'Parece um cavalo com listras pretas e brancas.'),
    ('COBRA', 2, 'animais', 'Animal comprido que se arrasta sem pernas.'),
    ('PORCO', 2, 'animais', 'Tem focinho redondo e faz oinc-oinc.'),
    ('BURRO', 2, 'animais', 'Tem orelhas compridas e vive na fazenda.'),
    ('GALO', 2, 'animais', 'Canta cocoricó e tem uma crista na cabeça.'),
    ('GANSO', 2, 'animais', 'Ave de pescoço comprido que gosta da água.'),
    ('POMBO', 2, 'animais', 'Ave cinzenta que costuma passear nas praças.'),
    ('ARARA', 2, 'animais', 'Ave de bico curvo e penas muito coloridas.'),
    ('PERA', 2, 'alimentos', 'Fruta mais fina em cima e arredondada embaixo.'),
    ('MANGA', 2, 'alimentos', 'Fruta doce com um caroço grande no meio.'),
    ('LIMÃO', 2, 'alimentos', 'Fruta azedinha usada para fazer limonada.'),
    ('MELÃO', 2, 'alimentos', 'Fruta grande de casca amarela e polpa clarinha.'),
    ('MILHO', 2, 'alimentos', 'Uma espiga com muitos grãos amarelinhos.'),
    ('PUDIM', 2, 'alimentos', 'Doce macio que costuma ter uma calda de caramelo.'),
    ('PIZZA', 2, 'alimentos', 'Massa redonda com queijo, servida em fatias.'),
    ('ALHO', 2, 'alimentos', 'Tem vários dentes e dá sabor à comida.'),
    ('MAÇÃ', 2, 'alimentos', 'Fruta crocante com casca vermelha ou verde.'),
    ('BALÃO', 2, 'brinquedos', 'Cheio de ar, enfeita festas e fica preso a um fio.'),
    ('TREM', 2, 'brinquedos', 'Tem vagões e anda sobre trilhos.'),
    ('CARRO', 2, 'brinquedos', 'Tem quatro rodas e pode ser um brinquedo de dirigir.'),
    ('ROBÔ', 2, 'brinquedos', 'Um boneco de máquina com braços e antena.'),
    ('PORTA', 2, 'casa', 'Abrimos para entrar e fechamos ao sair.'),
    ('BALDE', 2, 'casa', 'Tem uma alça e pode carregar água.'),
    ('LIVRO', 2, 'casa', 'Tem páginas cheias de histórias e desenhos.'),
    ('GARFO', 2, 'casa', 'Um talher com pontinhas para pegar comida.'),
    ('PRATO', 2, 'casa', 'É onde colocamos a comida para comer.'),
    ('FOGÃO', 2, 'casa', 'Um adulto usa para cozinhar e aquecer a comida.'),
    ('CHAVE', 2, 'casa', 'Pequena peça que abre uma fechadura.'),
    ('FOLHA', 2, 'natureza', 'Parte verde que cresce nos galhos das plantas.'),
    ('NUVEM', 2, 'natureza', 'Parece algodão e fica lá no céu.'),
    ('FLOR', 2, 'natureza', 'Tem pétalas e pode perfumar o jardim.'),
    ('PEDRA', 2, 'natureza', 'É dura e podemos encontrar no chão e no rio.'),
    ('BANANA', 3, 'alimentos', 'Fruta amarela, comprida e fácil de descascar.'),
    ('CAVALO', 3, 'animais', 'Animal da fazenda com crina que faz pocotó.'),
    ('PANELA', 3, 'casa', 'Recipiente com alças usado por adultos para cozinhar.'),
    ('TOMATE', 3, 'alimentos', 'Vermelho e redondinho, aparece muito na salada.'),
    ('COELHO', 3, 'animais', 'Tem orelhas compridas e um rabinho fofo.'),
    ('MACACO', 3, 'animais', 'Sobe em árvores e se segura nos galhos.'),
    ('GIRAFA', 3, 'animais', 'Animal de pescoço bem comprido e corpo com manchas.'),
    ('CORUJA', 3, 'animais', 'Ave de olhos grandes que costuma ficar acordada à noite.'),
    ('JACARÉ', 3, 'animais', 'Tem cauda comprida, boca grande e vive perto da água.'),
    ('TUCANO', 3, 'animais', 'Ave de bico grande e colorido.'),
    ('CEBOLA', 3, 'alimentos', 'Tem várias camadas e pode fazer chorar quando cortada.'),
    ('BATATA', 3, 'alimentos', 'Cresce debaixo da terra e pode virar purê.'),
    ('PEPINO', 3, 'alimentos', 'Verde e compridinho, é usado em saladas.'),
    ('GOIABA', 3, 'alimentos', 'Fruta que pode ter polpa rosa e muitas sementinhas.'),
    ('ALFACE', 3, 'alimentos', 'Verdura de folhas verdes muito usada na salada.'),
    ('BONECA', 3, 'brinquedos', 'Um brinquedo com rosto, braços e pernas para cuidar e brincar.'),
    ('PETECA', 3, 'brinquedos', 'Tem penas e sobe no ar quando batemos com a mão.'),
    ('DOMINÓ', 3, 'brinquedos', 'Jogo com peças retangulares marcadas com bolinhas.'),
    ('JANELA', 3, 'casa', 'Deixa entrar luz e permite olhar para fora de casa.'),
    ('TAPETE', 3, 'casa', 'Fica no chão e pode deixar o cantinho mais aconchegante.'),
    ('XÍCARA', 3, 'casa', 'Tem uma alcinha e pode servir chá.'),
    ('ESCOVA', 3, 'casa', 'Tem cerdas e ajuda a arrumar o cabelo.'),
    ('ÁRVORE', 3, 'natureza', 'Tem tronco, galhos e muitas folhas.'),
    ('CHUVA', 3, 'natureza', 'Água que cai das nuvens em gotinhas.'),
    ('PRAIA', 3, 'natureza', 'Lugar com areia bem pertinho do mar.'),
]

# As formas têm contorno e cores consistentes; cada composição representa o item.
INK = '#263d3c'
def e(x,y,rx,ry,fill,extra=''):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" {extra}/>'
def c(x,y,r,fill,extra=''): return e(x,y,r,r,fill,extra)
def r(x,y,w,h,fill,rx=12,extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" {extra}/>'
def p(d,fill='none',extra=''): return f'<path d="{d}" fill="{fill}" {extra}/>'
def line(x,y,a,b,color=INK,width=5): return f'<path d="M{x} {y}L{a} {b}" stroke="{color}" stroke-width="{width}" fill="none"/>'
def eyes(x=200,y=125,gap=25):
    return c(x-gap,y,5,INK)+c(x+gap,y,5,INK)
def smile(x=200,y=151): return p(f'M{x-12} {y}Q{x} {y+14} {x+12} {y}')
def leaf(x,y,scale=1,rotate=0):
    return f'<g transform="translate({x} {y}) rotate({rotate}) scale({scale})">'+p('M0 0Q-35-42 7-55Q42-26 0 0','#6bb777')+line(0,0,7,-43,'#357b53',3)+'</g>'
def legs(color): return r(140,195,25,56,color,9)+r(235,195,25,56,color,9)
def animal(color, ears='round', snout=False):
    out=legs(color)+e(200,184,78,56,color)
    if ears=='point': out+=p('M142 102L139 42L183 81',color)+p('M217 81L261 42L258 102',color)
    elif ears=='long': out+=e(165,64,16,56,color)+e(235,64,16,56,color)
    else: out+=c(151,82,25,color)+c(249,82,25,color)
    out+=e(200,130,72,65,color)+eyes()
    if snout: out+=e(200,157,36,25,'#f3d1ac')+c(187,153,4,INK)+c(213,153,4,INK)
    else: out+=p('M192 149Q200 158 208 149L200 158Z',INK)+smile(200,166)
    return out
def bird(color,beak='#f7b644',neck=False):
    out=line(175,219,165,247)+line(225,219,235,247)+line(155,247,176,247)+line(225,247,247,247)
    out+=e(197,182,77,48,color)
    out+=p('M137 181L98 153L111 205Z',color)
    if neck: out+=p('M213 168Q240 134 229 95L256 93Q278 150 244 184',color)
    out+=c(244,103 if neck else 135,39,color)+p(f'M273 {101 if neck else 134}L312 {112 if neck else 146}L273 {126 if neck else 160}Z',beak)
    out+=c(250,98 if neck else 130,5,INK)+e(183,182,39,25,color)
    return out
def fruit(fill,kind='round'):
    if kind=='round': return e(200,170,72,72,fill)+line(200,101,210,72,'#805335',8)+leaf(211,91,.7,48)
    return p('M195 72C155 93 187 113 151 147C78 218 150 261 211 251C295 247 300 190 249 143C218 112 239 84 214 72Z',fill)+line(205,78,218,49,'#805335',8)+leaf(219,66,.6,50)
ART={}

# Primeiros passos
ART['UVA']=line(200,77,217,43,'#6a7b43',9)+leaf(210,67,1,55)+''.join(c(x,y,25,'#9760c5') for x,y in [(164,108),(207,108),(246,108),(183,148),(226,148),(202,189),(201,225)])
ART['OVO']=p('M200 51C156 51 123 152 128 197C133 264 270 264 272 197C275 152 245 51 200 51Z','#fff4d9')+p('M150 185Q143 222 171 233',extra='stroke="#ead9b8" stroke-width="10"')
ART['LUA']=p('M245 48C160 38 107 103 131 183C150 250 225 268 277 221C186 231 151 106 245 48Z','#ffd874')+c(267,84,5,'#eebf52')+p('M298 137L304 153L320 159L304 165L298 181L292 165L276 159L292 153Z','#ffd874')
ART['SOL']=''.join(line(200,149,200,42,'#f2ac40',12) if n==0 else f'<g transform="rotate({n*45} 200 150)">'+line(200,44,200,65,'#f2ac40',10)+'</g>' for n in range(8))+c(200,150,69,'#ffd365')+eyes(200,145,23)+smile(200,168)
ART['MAR']=p('M52 113Q85 80 116 113T180 113T244 113T308 113Q331 99 348 110V242H52Z','#5bbfd7')+p('M52 158Q85 125 116 158T180 158T244 158T308 158Q331 144 348 155V242H52Z','#39a2c8')+p('M52 203Q85 170 116 203T180 203T244 203T308 203Q331 189 348 200V242H52Z','#2384b2')
ART['RIO']=p('M68 233L68 97Q129 41 190 98Q239 50 333 94V244Z','#a6d185')+p('M216 79C133 126 271 147 210 176C160 200 124 209 100 255H276C281 201 320 177 268 148C218 119 259 110 249 88Z','#6acbe3')+p('M211 130Q229 135 241 144M207 206L184 224',extra='stroke="#e0f9fc" stroke-width="7"')
ART['AVE']=bird('#6dbbc2')
ART['ASA']=p('M112 216Q93 162 140 115Q192 66 290 47Q296 71 279 90L242 112Q296 82 306 99Q312 114 292 131L248 154Q299 133 302 153Q298 175 274 187L223 205Q273 192 274 213Q264 238 217 246L151 250Q123 247 112 216Z','#80bbd5')+p('M144 214Q158 171 242 112M157 230Q191 195 248 154M164 241Q191 218 223 205',extra='stroke="#367898" stroke-width="4"')+p('M128 188Q125 150 168 127',extra='stroke="#acd2df" stroke-width="9"')
ART['BOI']=animal('#ba895b','round',True)+p('M141 89Q97 76 117 42Q123 62 151 64','#fff2c9')+p('M259 89Q303 76 283 42Q277 62 249 64','#fff2c9')
ART['BOLA']=c(200,151,101,'#f5edda')+p('M174 126L224 122L241 164L206 192L164 170Z','#639b7a')+p('M149 66L165 97L133 131L103 118M262 77L246 108L272 143L299 129M286 204L249 204L234 241M139 231L150 194L118 174',extra='stroke="#639b7a" stroke-width="22"')
ART['CASA']=r(111,124,178,122,'#f2d4a4')+p('M88 129L200 44L312 129Z','#e68a73')+r(181,170,42,76,'#679ba0',3)+r(126,155,37,39,'#bce5e4',3)+r(241,155,32,39,'#bce5e4',3)+c(214,211,3,'#f5d579')
ART['GATO']=animal('#e7ac68','point')+''.join(line(x,y,a,b) for x,y,a,b in [(167,151,128,144),(167,160,125,164),(233,151,272,144),(233,160,275,164)])+p('M271 201Q334 142 305 113',extra='stroke="#e7ac68" stroke-width="19"')
ART['PATO']=bird('#f7d360')
ART['SAPO']=e(200,198,79,42,'#86c487')+e(133,230,44,19,'#78b779')+e(267,230,44,19,'#78b779')+e(200,147,87,57,'#86c487')+c(160,104,31,'#86c487')+c(240,104,31,'#86c487')+c(160,104,17,'#fffbee')+c(240,104,17,'#fffbee')+c(163,104,6,INK)+c(237,104,6,INK)+smile(200,162)
ART['RATO']=animal('#b2b8c5','round')+c(150,80,16,'#e5abb6')+c(250,80,16,'#e5abb6')+p('M275 213Q325 250 332 204Q336 176 309 175',extra='stroke="#d697a9" stroke-width="9"')+line(168,153,132,146)+line(232,153,268,146)
ART['LOBO']=animal('#9faeb4','point')+p('M154 151L181 177L200 166L219 177L246 151Q229 186 200 186Q171 186 154 151Z','#e8ece5')+c(200,153,8,INK)
ART['FOCA']=e(200,191,89,56,'#9eb8c4')+e(130,227,42,17,'#8ba8b5','transform="rotate(-25 130 227)"')+p('M281 197Q334 170 323 205Q347 224 300 231L270 226Z','#8ba8b5')+e(169,131,64,65,'#a9c4ce')+eyes(169,122,25)+e(169,150,17,11,'#334e5a')+line(147,149,105,140)+line(147,158,103,163)+line(190,149,231,142)+line(190,158,235,164)
ART['VELA']=e(200,244,65,13,'#d4d9ce')+r(164,109,72,134,'#f4c4a7',8)+p('M166 123Q176 151 190 128Q206 115 213 144Q232 161 235 124','#ffe6bd')+line(200,108,200,90)+p('M200 31Q158 83 186 102Q220 125 227 88Q226 65 200 31Z','#ffc662')+p('M201 64Q181 97 201 101Q220 99 201 64Z','#f29359')
ART['MESA']=r(102,149,25,99,'#b77d52',4)+r(272,149,25,99,'#b77d52',4)+r(98,122,204,36,'#dfae7b',9)+line(127,169,272,169,'#b77d52',12)
ART['COPO']=p('M143 74H257L241 241H160Z','#b6e2e5')+p('M150 150Q199 133 250 150L241 238H161Z','#7bc6d2')+e(200,74,57,10,'#d7f1ed')+line(163,98,171,139,'#f7fffc',8)
ART['CAMA']=r(81,159,238,65,'#c5ae8f',6)+r(81,103,20,142,'#b88e6d',6)+r(300,144,20,101,'#b88e6d',6)+r(101,149,197,45,'#dfb6c3',7)+r(105,126,75,34,'#fff1d5',11)+r(186,143,109,54,'#78b3bd',6)
ART['POTE']=r(128,101,144,141,'#c8e5dd',24)+r(121,75,158,37,'#e4a26e',11)+r(158,144,84,61,'#fff0d3',10)+leaf(196,192,.65,0)
ART['LATA']=r(135,87,130,150,'#87bab4',3)+e(200,87,65,16,'#ccd7cc')+e(200,237,65,13,'#b8d5cd')+r(138,119,124,83,'#f1d88d',0)+''.join(e(x,y,9,13,'#eebc4b') for x,y in [(176,148),(199,148),(222,148),(187,177),(211,177)])
ART['FACA']=p('M197 55Q247 64 235 162L210 177H180V77Q180 55 197 55Z','#c5d7db')+r(177,166,38,92,'#b28566',10)+c(196,186,4,'#e5c3a0')+c(196,235,4,'#e5c3a0')
ART['MALA']=p('M168 95V68Q200 47 232 68V95',extra='stroke="#a56c43" stroke-width="14"')+r(109,90,182,149,'#ddac70',20)+r(137,92,21,145,'#bc8453',1)+r(242,92,21,145,'#bc8453',1)+r(182,150,36,27,'#f8d379',5)+c(140,248,8,INK)+c(260,248,8,INK)
ART['BULE']=p('M254 123Q322 92 314 154Q310 191 266 190',extra='stroke="#759fa9" stroke-width="17"')+p('M141 142L91 96L102 158L140 196Z','#8bbec1')+e(201,178,76,63,'#9ac8c7')+e(201,117,58,12,'#8bbec1')+c(201,101,13,'#dcad7a')+p('M164 177Q200 205 238 177',extra='stroke="#edf4db" stroke-width="9"')
ART['DADO']=r(120,72,160,160,'#f5d5b5',24)+''.join(c(x,y,11,'#71698c') for x,y in [(153,105),(247,105),(200,152),(153,199),(247,199)])
ART['PIPA']=p('M200 39L272 118L200 207L128 118Z','#f5d17c')+p('M200 39L200 207L128 118Z','#83bccb')+line(128,118,272,118,'#fff2cf',3)+p('M200 207Q158 229 205 249Q230 262 198 279')+p('M185 222L166 211L165 235Z','#e69a99')+p('M209 249L230 235L231 262Z','#e69a99')
ART['BOTA']=p('M148 53H239L231 174L286 196Q307 208 298 237H126Q110 231 121 211L146 186Z','#dfad66')+r(122,231,178,17,'#9b7350',5)+r(145,53,97,26,'#f3d38b',5)
ART['MEIA']=p('M178 56H252V155Q248 197 193 225L159 243Q110 256 102 219Q96 191 136 174L178 155Z','#e9b9b1')+r(175,53,81,30,'#8bbdb5',4)+p('M178 155Q198 185 171 209',extra='stroke="#f5e8ce" stroke-width="20"')
ART['LUVA']=p('M154 241L146 183L113 136Q104 113 122 104Q137 98 155 128V80Q156 55 173 63L180 112V58Q184 38 200 52L204 108L211 61Q217 40 231 55L231 113L242 78Q249 60 262 73Q275 86 256 164L245 241Z','#a3c7bb')+r(147,225,107,29,'#5b9e93',5)
ART['TUBO']=p('M139 84L247 53L281 201L173 235Z','#a7c6cc')+e(156,160,25,78,'#79a3af','transform="rotate(-14 156 160)"')+e(156,160,13,61,'#405e6a','transform="rotate(-14 156 160)"')+p('M185 94L250 76',extra='stroke="#d9ece9" stroke-width="7"')
ART['CUBO']=p('M112 104L200 56L288 104L200 154Z','#f4cf81')+p('M112 104L200 154V251L112 201Z','#8abca9')+p('M200 154L288 104V201L200 251Z','#75a5b9')
ART['VACA']=animal('#f8f2de','round',True)+p('M141 89Q97 76 117 42Q123 62 151 64','#edc995')+p('M259 89Q303 76 283 42Q277 62 249 64','#edc995')+p('M157 110Q159 86 180 85Q205 88 184 119Q169 136 157 110Z','#5c665e')+e(240,192,23,20,'#5c665e')
ART['SUCO']=p('M140 87H260L243 238H158Z','#ffcd70')+e(200,87,60,11,'#ffdf89')+p('M216 172L235 44L264 35',extra='stroke="#e3948a" stroke-width="12"')+c(132,183,37,'#edb05d')+c(132,183,27,'#ffe0a0')+line(132,157,132,209,'#f4bc6a',3)+line(107,183,157,183,'#f4bc6a',3)
ART['BOLO']=e(200,243,120,14,'#c8ddd7')+r(102,133,196,105,'#dca77f',8)+r(102,131,196,40,'#f2c5c7',9)+p('M103 155Q120 188 136 158Q150 142 165 173Q185 201 200 163Q219 148 229 173Q244 195 260 161Q280 150 297 166','#f2c5c7')+r(194,82,12,48,'#84b8b9',3)+p('M200 51Q181 75 200 81Q219 75 200 51Z','#ffc55b')
ART['COCO']=c(178,168,83,'#a47650')+c(178,168,63,'#fff0cf')+c(178,168,34,'#d0c6a3')+p('M240 108Q299 111 304 179Q302 238 257 244L246 210Q270 167 240 108Z','#a47650')+p('M270 126L286 202M154 105L136 119',extra='stroke="#805b42" stroke-width="6"')
ART['BALA']=p('M141 124L79 91L86 147L69 193L143 179Z','#b8d5c4')+p('M259 124L321 91L314 147L331 193L257 179Z','#b8d5c4')+p('M141 124L119 114M142 150L105 149M141 178L116 180M259 124L281 114M258 150L295 149M259 178L284 180',extra='stroke="#7ca797" stroke-width="4"')+r(132,103,136,95,'#df9ba5',31)+p('M170 107L154 194M210 106L194 196M250 108L234 195',extra='stroke="#f2c9bd" stroke-width="17"')
ART['NAVE']=p('M169 166L126 224L172 215M231 166L274 224L228 215','#d49089')+p('M200 38Q144 100 160 201H240Q256 100 200 38Z','#e1e8dc')+p('M200 38Q177 62 171 86H229Q223 62 200 38Z','#d49089')+c(200,132,25,'#82bfc8')+p('M177 213Q171 250 200 270Q229 250 223 213Z','#f5c76d')
ART['LUPA']=p('M226 190L280 249',extra='stroke="#b98763" stroke-width="25"')+c(174,124,73,'#81b6bb')+c(174,124,59,'#d8eeea')+p('M134 125Q135 88 171 82',extra='stroke="#fff9e8" stroke-width="8"')

# Descobrindo letras
ART['PEIXE']=p('M260 148L322 93V207Z','#e9af65')+e(186,150,95,61,'#f4c678')+p('M157 96Q184 56 211 96M157 204Q185 240 213 204','#e9af65')+c(133,136,7,INK)+p('M101 159Q112 166 119 159')+p('M194 123Q168 151 196 174',extra='stroke="#d99553" stroke-width="7"')
ART['URSO']=animal('#b88b62','round')+e(200,170,34,24,'#ecd5b4')+c(200,158,9,INK)+smile(200,173)
ART['TIGRE']=animal('#e9ad61','round')+''.join(p(d,INK) for d in ['M143 95L171 119L158 90Z','M257 95L229 119L242 90Z','M184 67L194 97L200 66Z','M208 67L212 95L221 70Z','M131 142L155 150L134 157Z','M269 142L245 150L266 157Z'])+e(182,162,19,15,'#fff0d5')+e(218,162,19,15,'#fff0d5')+c(200,153,7,INK)
ART['ZEBRA']=animal('#f6f3e7','point',True)+''.join(p(d,'#506369') for d in ['M143 91L172 110L157 76Z','M257 91L228 110L243 76Z','M179 66L187 106L197 65Z','M207 66L214 108L225 70Z','M129 131L155 142L132 153Z','M271 131L245 142L268 153Z','M146 190L163 225L175 194Z','M220 190L236 226L250 194Z'])
ART['COBRA']=p('M109 215Q177 167 242 214Q295 240 296 185Q293 156 240 162Q192 165 197 119Q199 77 248 80',extra='stroke="#7db581" stroke-width="39"')+e(258,81,45,33,'#91c48a')+c(274,75,5,INK)+p('M298 89H318M318 89L326 82M318 89L326 96',extra='stroke="#d48e8d" stroke-width="4"')
ART['PORCO']=animal('#e8adaf','point')+e(200,158,37,27,'#d98e97')+c(186,158,6,'#9e5d70')+c(214,158,6,'#9e5d70')+p('M278 198Q316 172 320 195Q319 211 307 203')
ART['BURRO']=animal('#abb4b1','long',True)+e(165,60,7,35,'#deb9ad')+e(235,60,7,35,'#deb9ad')+p('M187 77L192 57L203 73L213 56L223 83Z','#536267')
ART['GALO']=bird('#d3a570')+p('M220 106Q200 77 215 67Q227 62 233 80Q234 48 250 51Q265 56 257 82Q281 61 287 79Q291 99 271 108Z','#da8276')+p('M125 170Q64 96 79 83Q102 83 129 134Q80 55 106 53Q140 62 152 140','#6ca49c')+e(269,173,10,18,'#da8276')
ART['GANSO']=bird('#f7f2df','#e4a15b',True)
ART['POMBO']=bird('#a9b8c3','#ad907b')+p('M218 154Q245 164 272 149L263 178L224 181Z','#79a8a7')+e(182,180,37,26,'#829eae')
ART['ARARA']=bird('#de897f')+p('M273 126Q319 125 310 166Q295 150 277 159Z','#d0be8e')+p('M144 188L114 261L167 218Z','#7aabc8')+e(182,185,38,27,'#7faeca')+p('M151 178Q186 153 218 183L205 200Q179 179 151 195Z','#f2cf75')
ART['PERA']=fruit('#bed176','pear')
ART['MANGA']=e(201,166,81,94,'#f4bd6d','transform="rotate(22 201 166)"')+p('M205 73Q273 89 281 169Q240 153 219 106Z','#e9a36f')+line(223,78,236,52,'#8d7047',7)+leaf(236,66,.8,70)
ART['LIMÃO']=p('M108 168Q110 101 151 108Q201 63 247 104Q289 108 291 153Q293 209 248 215Q200 251 151 217Q109 224 108 168Z','#a0c365')+leaf(236,91,.8,45)+p('M146 147Q158 122 179 125',extra='stroke="#d1df8d" stroke-width="8"')
ART['MELÃO']=e(200,162,100,84,'#efce75')+p('M154 91Q110 164 154 233M200 78Q162 162 200 245M248 91Q210 164 248 233',extra='stroke="#d3b465" stroke-width="4"')+line(199,78,213,55,'#8e985e',7)
ART['MILHO']=e(200,138,45,94,'#f4c76b')+''.join(e(x,y,7,9,'#f9db87') for x in (177,200,223) for y in (83,108,133,158,183))+p('M197 246Q106 224 112 111Q169 134 201 228Q225 130 287 98Q299 207 197 246Z','#7eb77e')+p('M197 246Q156 202 137 151M197 246Q242 203 265 143',extra='stroke="#4c9267" stroke-width="5"')
ART['PUDIM']=e(200,239,123,20,'#d4e5de')+p('M134 97H266L292 218Q200 253 108 218Z','#f6d294')+e(200,97,66,26,'#b98450')+e(200,97,27,10,'#fff0c9')+p('M139 115Q154 154 166 128Q179 110 187 139Q202 167 216 130Q235 114 247 140Q263 149 263 118','#b98450')
ART['PIZZA']=c(200,150,104,'#dfaf75')+c(200,150,90,'#e3a075')+c(200,150,81,'#f2d18a')+''.join(c(x,y,13,'#c77e6e') for x,y in [(169,101),(232,111),(154,170),(209,160),(234,208)])+''.join(leaf(x,y,.25,35) for x,y in [(207,94),(261,157),(173,215)])+line(200,150,200,47,'#d2a367',3)+line(200,150,110,202,'#d2a367',3)+line(200,150,289,202,'#d2a367',3)
ART['ALHO']=p('M199 47Q169 73 182 101C110 111 100 189 147 226Q200 260 253 226C300 189 290 111 218 101Q231 73 201 47Z','#f3e9d8')+p('M191 108Q150 175 180 238M209 108Q249 175 219 238',extra='stroke="#d9c4b7" stroke-width="5"')+p('M178 240L166 257M195 242L192 262M210 242L214 261M223 241L237 256',extra='stroke="#a89d7f" stroke-width="4"')
ART['MAÇÃ']=p('M201 102C147 68 108 105 115 172C122 235 163 266 201 242C239 266 280 235 287 172C294 105 255 68 201 102Z','#dc8c80')+line(201,103,212,57,'#926e47',8)+leaf(211,84,.8,60)+p('M142 138Q131 165 145 190',extra='stroke="#f8c9ae" stroke-width="10"')
ART['BALÃO']=e(200,126,73,91,'#db9ca8')+p('M196 214L190 228H210L204 214Z','#db9ca8')+p('M200 229Q220 246 198 265Q182 280 207 292')+p('M151 109Q155 68 185 61',extra='stroke="#f2d2d4" stroke-width="9"')
ART['TREM']=line(69,247,329,247,'#9c8467',8)+r(87,136,116,79,'#9dbbaa',8)+r(201,164,113,51,'#7ca5b2',7)+r(214,108,82,75,'#7ca5b2',6)+r(210,99,92,17,'#e6ad77',4)+r(97,115,30,36,'#e6ad77',3)+r(232,122,43,36,'#d8e6df',3)+''.join(c(x,217,24,'#5b777c')+c(x,217,9,'#ebcc98') for x in (114,178,241,291))+c(107,89,16,'#d4ddcf')+c(127,62,20,'#d4ddcf')
ART['CARRO']=p('M85 173L120 162L156 105H240L285 162L316 173V217H84Z','#8fb8aa')+p('M167 115H196V160H139Z','#d7e9e2')+p('M209 115H232L268 160H209Z','#d7e9e2')+c(140,215,29,'#4f6770')+c(265,215,29,'#4f6770')+c(140,215,13,'#d3c7a9')+c(265,215,13,'#d3c7a9')+r(85,175,20,19,'#f3d68f',4)+r(300,176,15,17,'#cf877c',4)
ART['ROBÔ']=line(200,58,200,36,'#9a9d92',5)+c(200,30,9,'#e5a27b')+r(136,61,128,81,'#95b9bc',15)+r(126,151,148,84,'#a9c5be',10)+r(111,85,20,33,'#dfb784',5)+r(269,85,20,33,'#dfb784',5)+r(92,160,26,67,'#dfb784',9)+r(282,160,26,67,'#dfb784',9)+r(148,233,33,30,'#779ba4',5)+r(219,233,33,30,'#779ba4',5)+eyes(200,95,30)+line(176,119,224,119)+c(177,181,10,'#e4a48a')+r(201,173,45,16,'#f3d48c',3)
ART['PORTA']=r(123,47,154,213,'#c0b193',3)+r(137,60,126,200,'#d5a979',3)+r(153,79,94,64,'#e2be94',3)+r(153,171,94,71,'#e2be94',3)+c(244,157,7,'#826e4c')
ART['BALDE']=p('M124 106Q114 18 200 30Q286 18 276 106',extra='stroke="#8b9e93" stroke-width="10"')+p('M113 104H287L265 244H135Z','#8ab9bd')+e(200,104,87,17,'#cce5dc')+p('M143 130L155 215',extra='stroke="#cce5dc" stroke-width="10"')
ART['LIVRO']=p('M84 76Q140 55 200 84Q260 55 316 76V235Q260 218 200 247Q140 218 84 235Z','#f8ebce')+p('M84 76V235Q140 218 200 247Q260 218 316 235V248Q260 231 200 260Q140 231 84 248H76V76Z','#81aaa3')+line(200,84,200,245,'#bba78a',4)+''.join(p(f'M{x} {y}Q{x+32} {y-8} {x+62} {y+2}',extra='stroke="#d6c7a9" stroke-width="4"') for x in (108,225) for y in (117,143,169,195))
ART['GARFO']=p('M174 43V105Q174 127 190 133V247Q201 262 212 247V133Q228 127 228 105V43H216V98H207V43H195V98H186V43Z','#adc7ce')
ART['PRATO']=e(200,151,123,100,'#a8ccca')+e(200,151,104,82,'#f4efdb')+e(200,151,78,59,'#e6ead6')+p('M112 147Q118 105 158 92',extra='stroke="#fcf7e5" stroke-width="7"')
ART['FOGÃO']=r(113,66,174,185,'#afc9c6',9)+r(111,86,178,31,'#e4dfcc',3)+r(131,139,138,91,'#607d87',8)+r(141,152,118,64,'#92afba',4)+line(153,146,247,146,'#d7e2d7',6)+c(148,102,7,'#8d9b95')+c(180,102,7,'#8d9b95')+c(220,102,7,'#8d9b95')+c(252,102,7,'#8d9b95')+e(156,69,27,7,'#637d7c')+e(244,69,27,7,'#637d7c')
ART['CHAVE']=c(158,113,61,'#e3bb71')+c(158,113,31,'#f8ecd2')+p('M196 153L283 240L310 214L284 188L269 204L253 188L268 173L238 143L222 159L214 151Z','#e3bb71')
ART['FOLHA']=p('M114 229Q82 77 288 52Q320 230 114 229Z','#8bbc78')+p('M114 229L265 77M160 184L151 127M160 184L223 188M205 137L201 93M205 137L266 141',extra='stroke="#559969" stroke-width="6"')
ART['NUVEM']=p('M105 220C49 217 48 146 100 138C87 81 157 49 192 89C229 38 301 75 293 132C356 131 358 216 300 220Z','#dbe9e6')+p('M107 190Q83 187 88 168',extra='stroke="#fdf8e8" stroke-width="9"')
ART['FLOR']=line(200,159,200,260,'#70a373',12)+leaf(194,238,.8,-48)+leaf(206,220,.7,65)+''.join(f'<g transform="rotate({n*60} 200 126)">'+e(200,74,27,40,'#df9dab')+'</g>' for n in range(6))+c(200,126,34,'#f2cd73')
ART['PEDRA']=p('M102 218L86 171L125 100L191 65L266 95L309 166L288 221L208 249Z','#a7b3b4')+p('M125 100L169 157L102 218M169 157L266 95M169 157L208 249M169 157L309 166',extra='stroke="#859a9f" stroke-width="5"')

# Novo desafio
ART['BANANA']=p('M104 74Q150 226 284 118L305 97L319 109Q286 239 187 250Q91 242 87 97Z','#f4ce75')+p('M108 104Q139 248 299 137',extra='stroke="#d6aa4f" stroke-width="5"')+p('M87 97L83 66L102 61L109 82Z','#a59157')+p('M306 99L321 83L331 92L318 110Z','#a59157')
ART['CAVALO']=r(133,192,19,65,'#bb895f',6)+r(171,194,19,63,'#bb895f',6)+r(232,192,19,65,'#bb895f',6)+r(266,187,19,70,'#bb895f',6)+p('M130 155Q88 129 91 208',extra='stroke="#805e48" stroke-width="21"')+e(204,170,83,45,'#bb895f')+p('M227 155Q215 90 243 68L273 71Q262 101 282 150Z','#bb895f')+p('M239 69Q213 80 220 132L231 154L242 145L232 128L245 119L237 104L252 94Z','#805e48')+p('M249 77L246 38L264 62L280 46L282 82Z','#bb895f')+p('M249 72Q281 58 290 85L318 112Q333 137 309 146Q286 145 273 123L245 106Z','#bb895f')+e(306,131,20,14,'#d8b18a')+c(277,89,5,INK)+c(317,126,3,INK)+''.join(r(x,247,22,13,'#805e48',3) for x in (131,169,230,264))
ART['PANELA']=r(119,107,162,131,'#93b5b7',27)+p('M118 134H85V174H119M282 134H315V174H281',extra='stroke="#688b94" stroke-width="16"')+e(200,107,85,18,'#bacfc9')+p('M119 107Q132 63 200 63Q268 63 281 107Z','#afc8c6')+r(177,49,46,18,'#708e94',5)+p('M148 146V189',extra='stroke="#d8e4d9" stroke-width="9"')
ART['TOMATE']=e(200,174,91,75,'#df8b78')+p('M200 118L171 81L186 111L149 104L182 132L156 149L201 134L238 150L222 127L256 107L215 111L224 78Z','#79a16c')+line(201,114,203,71,'#729a65',7)+p('M135 170Q137 145 151 142',extra='stroke="#f3b5a0" stroke-width="9"')
ART['COELHO']=animal('#e1d5c3','long')+e(165,60,7,35,'#e6b6b0')+e(235,60,7,35,'#e6b6b0')+r(188,161,24,19,'#fff7e7',2)+line(200,163,200,178,'#b0a79b',2)+e(200,149,9,6,'#d79798')
ART['MACACO']=animal('#a9815f','round')+c(151,82,14,'#ddbc93')+c(249,82,14,'#ddbc93')+e(179,130,30,37,'#dfbf97')+e(221,130,30,37,'#dfbf97')+e(200,160,39,28,'#dfbf97')+eyes()+c(200,153,5,INK)+smile(200,165)+p('M275 202Q331 154 328 224Q322 254 299 240',extra='stroke="#a9815f" stroke-width="15"')
ART['GIRAFA']=r(146,116,55,114,'#e8c47f',16)+e(218,208,77,35,'#e8c47f')+r(167,227,18,35,'#e8c47f',4)+r(258,227,18,35,'#e8c47f',4)+e(183,97,56,39,'#e8c47f')+p('M145 78L119 54L121 89M204 72L227 48L225 86','#e8c47f')+line(162,62,157,42,'#b98c5c',7)+line(192,60,197,40,'#b98c5c',7)+c(157,38,7,'#b98c5c')+c(198,36,7,'#b98c5c')+c(169,91,5,INK)+e(217,105,27,19,'#f0d8a8')+''.join(e(x,y,12,10,'#b48b58') for x,y in [(164,137),(179,170),(165,201),(217,192),(253,215)])
ART['CORUJA']=line(121,252,287,252,'#a78762',11)+e(200,161,80,90,'#aa8e74')+p('M123 123L119 56L166 87M277 123L281 56L234 87','#aa8e74')+e(126,182,20,49,'#8f796a','transform="rotate(15 126 182)"')+e(274,182,20,49,'#8f796a','transform="rotate(-15 274 182)"')+c(164,133,36,'#f4e6c5')+c(236,133,36,'#f4e6c5')+c(164,133,14,'#485a55')+c(236,133,14,'#485a55')+p('M188 158L212 158L200 177Z','#e3b25d')+p('M174 203L186 214L198 203M204 203L216 214L228 203',extra='stroke="#d0b799" stroke-width="5"')
ART['JACARÉ']=e(200,190,104,42,'#89b384')+p('M104 186L60 149L69 206L111 214Z','#89b384')+p('M129 168L143 146L159 166L175 145L190 163L207 146L221 165L237 148L249 169Z','#6d9b73')+r(234,119,100,60,'#9cc18b',24)+c(257,115,18,'#9cc18b')+c(289,115,18,'#9cc18b')+c(259,113,5,INK)+c(291,113,5,INK)+p('M264 155H329M289 155L295 165L302 155M309 155L316 165L323 155',extra='stroke="#3a6050" stroke-width="4"')+r(151,213,29,32,'#89b384',7)+r(235,213,29,32,'#89b384',7)
ART['TUCANO']=bird('#526b6e')+p('M267 113Q320 82 341 117L333 151L278 153Z','#edbd6f')+p('M323 102Q349 111 335 147L319 147Z','#d88f70')+e(257,139,20,27,'#f4df9d')+c(249,129,5,INK)+e(183,182,39,25,'#405d62')
ART['CEBOLA']=p('M200 52Q182 87 174 107C107 118 100 185 135 223Q201 269 266 223C302 185 293 118 226 107Q218 87 200 52Z','#d7a39d')+p('M183 111Q138 175 172 238M200 108Q185 174 200 247M218 111Q263 175 229 238',extra='stroke="#b88082" stroke-width="5"')+p('M180 245L166 261M199 250L199 268M218 246L231 261',extra='stroke="#9f8867" stroke-width="4"')
ART['BATATA']=e(202,159,103,73,'#c8a976','transform="rotate(-26 202 159)"')+''.join(e(x,y,5,3,'#9e835a','transform="rotate(-26 %s %s)"'%(x,y)) for x,y in [(143,158),(178,119),(225,180),(253,130),(187,191)])
ART['PEPINO']=p('M113 237C59 191 179 75 257 58C318 44 335 95 295 126C222 182 159 276 113 237Z','#81a56a')+p('M126 218Q201 120 278 82',extra='stroke="#a4c485" stroke-width="8"')+''.join(c(x,y,3,'#567d52') for x,y in [(138,204),(164,196),(177,150),(212,153),(229,109),(269,110),(284,88)])
ART['GOIABA']=e(248,142,68,81,'#b9c884')+line(252,66,266,48,'#8e7855',7)+leaf(263,65,.6,72)+c(167,174,77,'#a7bd78')+c(167,174,66,'#e9a6a1')+c(167,174,35,'#f4c3ae')+''.join(c(x,y,3,'#efe0ae') for x,y in [(153,159),(171,151),(184,164),(178,181),(157,188),(145,176),(166,174),(177,195)])
ART['ALFACE']=e(200,229,72,23,'#b7ce8f')+''.join(c(x,y,48,col) for x,y,col in [(133,139,'#87af76'),(185,105,'#92bb7b'),(244,117,'#9bc382'),(273,164,'#87af76'),(134,190,'#a2c78b'),(195,178,'#b2ce93'),(229,207,'#a2c78b')])+p('M200 236Q152 193 133 139M200 236Q180 158 185 105M200 236Q237 171 244 117M200 236L273 164',extra='stroke="#d1ddac" stroke-width="5"')
ART['BONECA']=p('M156 154L123 205M244 154L277 205',extra='stroke="#e7ba91" stroke-width="20"')+r(159,215,25,53,'#e7ba91',9)+r(216,215,25,53,'#e7ba91',9)+p('M166 136H234L264 228H136Z','#dca3ad')+c(200,91,51,'#a67e57')+c(144,108,24,'#a67e57')+c(256,108,24,'#a67e57')+e(200,103,42,44,'#edc59e')+p('M160 90Q167 48 207 54Q245 57 244 92Q221 74 204 70Q190 88 160 90Z','#a67e57')+eyes(200,103,17)+smile(200,120)+r(150,252,35,20,'#8dabb2',7)+r(215,252,35,20,'#8dabb2',7)
ART['PETECA']=p('M174 188L137 54Q158 43 172 61L198 176Z','#f3d58f')+p('M188 183L187 36Q206 24 217 43L211 185Z','#99c1b4')+p('M207 185L238 51Q261 46 268 67L232 196Z','#d8a2af')+p('M220 189L279 99Q300 103 294 124L238 211Z','#8fb6c9')+e(200,220,57,32,'#d1ab78')+e(200,207,55,22,'#e5c398')
ART['DOMINÓ']=f'<g transform="rotate(-13 166 154)">'+r(113,57,90,183,'#f2e6cc',11)+line(117,148,199,148)+''.join(c(x,y,7,'#657d7b') for x,y in [(136,82),(180,123),(136,174),(180,174),(136,215),(180,215)])+'</g>'+f'<g transform="rotate(13 254 176)">'+r(217,99,85,166,'#d1e0d1',11)+line(220,180,299,180)+c(258,139,7,'#657d7b')+c(240,204,7,'#657d7b')+c(278,240,7,'#657d7b')+'</g>'
ART['JANELA']=r(104,56,192,188,'#d1ae86',6)+r(118,69,164,160,'#b9dfe0',2)+c(246,105,21,'#f4d17b')+p('M120 208L166 152L206 195L245 157L281 202V228H120Z','#a0c18b')+line(200,68,200,230,'#f4e6cc',10)+line(119,149,282,149,'#f4e6cc',10)+r(93,239,214,15,'#bd956e',4)
ART['TAPETE']=p('M111 75L314 122L288 241L85 194Z','#d79b94')+p('M124 96L293 135L275 219L106 180Z','#e8c4a4')+p('M137 117L271 147L262 193L127 163Z','#85ac9c')+''.join(line(x,y,x-11,y+21,'#cfbd9a',4) for x,y in [(91,99),(88,123),(84,147),(80,171),(305,148),(300,171),(296,194),(291,218)])
ART['XÍCARA']=e(200,241,111,16,'#d5ddd0')+p('M258 123Q328 98 319 162Q314 201 262 190',extra='stroke="#8caeb3" stroke-width="17"')+p('M125 109H276L262 210Q201 254 140 210Z','#a4c9c4')+e(200,109,75,17,'#dfe9db')+e(200,110,58,9,'#b99a74')+p('M176 80Q156 60 176 39M220 80Q200 60 220 39',extra='stroke="#c4d4c9" stroke-width="6"')
ART['ESCOVA']=f'<g transform="rotate(-24 200 150)">'+r(180,162,40,110,'#c79770',14)+r(140,39,120,150,'#dfba8b',47)+r(151,49,98,125,'#a68f78',38)+''.join(line(x,y,x+4,y-13,'#f1dcc0',5) for x in (169,190,211,232) for y in (78,104,130,156))+'</g>'
ART['ÁRVORE']=p('M178 244L180 127H220L226 244L245 261H154Z','#ae835e')+c(138,123,59,'#8cb57b')+c(206,81,66,'#94bd7d')+c(267,127,58,'#84ad76')+c(201,153,66,'#a1c787')+p('M201 224V157M201 193L169 169M201 183L239 159',extra='stroke="#9e7957" stroke-width="9"')
ART['CHUVA']=ART['NUVEM'].replace('220','172').replace('217','169').replace('190','142')+''.join(p(f'M{x} {y}L{x-12} {y+27}',extra='stroke="#7eafb9" stroke-width="8"') for x,y in [(115,195),(175,195),(235,195),(295,195),(146,240),(207,240),(267,240)])
ART['PRAIA']=p('M65 125H335V248H65Z','#80c4d0')+p('M65 223Q150 161 335 211V260H65Z','#ebd3a1')+p('M75 193Q140 160 198 184Q260 211 330 181',extra='stroke="#d9eee2" stroke-width="8"')+line(233,233,253,110,'#ae8b66',7)+p('M173 125Q196 56 267 72Q321 80 327 144L289 128L253 137L219 119Z','#df9e8c')+p('M253 137L267 72Q222 79 219 119Z','#f1cb80')+c(108,74,25,'#f4d17b')

def slug(word):
    return ''.join(c for c in unicodedata.normalize('NFD', word.lower()) if unicodedata.category(c) != 'Mn')

def main():
    assert len(CONTENT) == 100
    assert len({row[0] for row in CONTENT}) == 100
    assert [sum(row[1] == level for row in CONTENT) for level in (1,2,3)] == [40,35,25]
    assert all((3 <= len(w) <= 4) if l==1 else (4<=len(w)<=5) if l==2 else (5<=len(w)<=6) for w,l,_,_ in CONTENT)
    assert set(ART) == {row[0] for row in CONTENT}, set(ART) ^ {row[0] for row in CONTENT}
    OUT.mkdir(parents=True, exist_ok=True)
    words=[]
    for word,level,category,clue in CONTENT:
        name=slug(word)
        svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">'
             f'<title>{word}</title><g stroke="{INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">'
             +ART[word]+'</g></svg>')
        (OUT/f'{name}.svg').write_text(svg)
        words.append(dict(word=word,level=level,category=category,image=f'/images/{name}.png',clue=clue,audio=word.lower()))
    (ROOT/'public/content/words.json').write_text(json.dumps(words,ensure_ascii=False,indent=2)+'\n')
    def export(row):
        name=slug(row[0])
        subprocess.run(['inkscape',str(OUT/f'{name}.svg'),'--export-type=png',f'--export-filename={OUT/name}.png'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(export,CONTENT))
    print('100 palavras e 100 ilustrações exportadas: 40 / 35 / 25.')

if __name__=='__main__': main()
