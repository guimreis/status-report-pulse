"""A marca de quem assina o relatório: logo (ou a provisória com as iniciais), foto e fonte.

Tudo vai embutido em base64, e nada por URL. Material que baixa imagem da web depende de
internet na hora de imprimir e do site no ar na hora de abrir, e o do cliente não pode
depender de nenhum dos dois.

A marca vem do campo `marca` do registro (veja `references/formato.md`):

    {"nome": "Sua Empresa", "logo": "caminho/da/logo.png", "site": "suaempresa.com.br",
     "slogan": "O que a empresa faz, em poucas palavras", "foto": "mesa"}

Sem `logo`, sai a logo provisória: as iniciais do nome num quadrado, e o nome ao lado.

Os arquivos que vêm com a skill moram em `assets/`:

    fontes/schibsted-grotesk.css   a fonte em base64, pesos 400 a 900 (OFL, em fontes/OFL.txt)
    fotos/unsplash-*.jpg           as fotos de capa, já recortadas e em preto e branco
"""
import base64
import html
import os

ASSETS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       '..', '..', 'assets'))
FOTOS = {'mesa': 'fotos/unsplash-OqxPH8c1UFE.jpg',
         'reuniao': 'fotos/unsplash-1RT4txDDAbM.jpg',
         'montanha': 'fotos/unsplash-roZgc7SXXmI.jpg'}

_MIME = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
         '.svg': 'image/svg+xml', '.webp': 'image/webp'}

# a marca em uso; `definir` troca, e o deck lê daqui
MARCA = {'nome': '', 'logo': '', 'iniciais': '', 'site': '', 'slogan': '', 'foto': ''}
BASE = ''   # pasta do registro: caminho relativo de logo e foto é lido a partir dela


def caminho(nome):
    """Arquivo da skill (em `assets/`), ou caminho de quem usa (absoluto ou relativo ao registro)."""
    if os.path.isabs(nome) and os.path.isfile(nome):
        return nome
    if BASE and os.path.isfile(os.path.join(BASE, nome)):
        return os.path.join(BASE, nome)
    return os.path.join(ASSETS, nome)


def embutir(nome, mime=None):
    """A imagem como data URI, pronta para `src`."""
    mime = mime or _MIME.get(os.path.splitext(nome)[1].lower(), 'application/octet-stream')
    with open(caminho(nome), 'rb') as f:
        dados = base64.b64encode(f.read()).decode()
    return f'data:{mime};base64,{dados}'


def definir(marca=None, base=''):
    """Troca a marca em uso pela do registro. Campo ausente fica vazio."""
    global BASE
    BASE = base or ''
    MARCA.clear()
    MARCA.update({'nome': '', 'logo': '', 'iniciais': '', 'site': '', 'slogan': '', 'foto': ''})
    MARCA.update({k: str(v) for k, v in (marca or {}).items() if v})
    if MARCA['logo'] and not os.path.isfile(caminho(MARCA['logo'])):
        print(f'aviso: logo "{MARCA["logo"]}" não encontrada; saiu a logo provisória')
        MARCA['logo'] = ''


def iniciais():
    """Iniciais para a logo provisória: 'Sua Marca' -> 'SM'. `iniciais` na marca manda."""
    if MARCA.get('iniciais'):
        return MARCA['iniciais'][:3].upper()
    palavras = [p for p in MARCA.get('nome', '').replace('&', ' ').split()
                if p.lower() not in ('de', 'da', 'do', 'das', 'dos', 'e')]
    if not palavras:
        return 'SR'
    if len(palavras) == 1:
        return palavras[0][:2].upper()
    return (palavras[0][0] + palavras[-1][0]).upper()


def logo(escuro=False, classe='logo'):
    """A logo de quem assina. Sobre fundo escuro, a imagem sai em branco."""
    nome = html.escape(MARCA.get('nome') or '')
    if MARCA.get('logo'):
        filtro = ' style="filter:brightness(0) invert(1)"' if escuro else ''
        return f'<img class="{classe}" src="{embutir(MARCA["logo"])}"{filtro} alt="{nome}">'
    return (f'<span class="{classe} provisoria"><span class="mono">{html.escape(iniciais())}</span>'
            f'{f"<b>{nome}</b>" if nome else ""}</span>')


def foto_capa():
    """A foto da capa: uma das que vêm com a skill (`mesa`, `reuniao`, `montanha`) ou o
    caminho de uma foto de quem usa. `nenhuma` tira a foto."""
    f = MARCA.get('foto') or 'mesa'
    if f == 'nenhuma':
        return ''
    return FOTOS.get(f, f)


def fontes():
    """Schibsted Grotesk embutida, em `@font-face` com base64.

    O `<link>` do Google Fonts nem sempre chega a tempo na impressão, e quando não chega o
    PDF sai em Helvetica sem avisar ninguém.
    """
    with open(caminho('fontes/schibsted-grotesk.css'), encoding='utf-8') as f:
        return f.read()
