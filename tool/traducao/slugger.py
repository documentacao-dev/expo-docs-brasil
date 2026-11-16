"""Slug de título igual ao do site (rehype-slug / github-slugger 2.0.0).

A expressão de caracteres removidos vem de github-slugger-regex.txt (cópia de
github-slugger/regex.js, MIT). O JS trabalha em unidades UTF-16; aqui o texto é
convertido para unidades UTF-16 antes de aplicar a regex e depois recomposto.
"""
import html
import re
from pathlib import Path

_REGEX = re.compile(
    (Path(__file__).parent / 'github-slugger-regex.txt').read_text().strip().replace(r'\/', '/')
)
SUFIXO = re.compile(r'\s*\\?\{#([A-Za-z0-9_.:-]+)\}\s*$')
CERCA = re.compile(r'^\s*(`{3,}|~{3,})')


def _utf16(s):
    b = s.encode('utf-16-le', 'surrogatepass')
    return ''.join(chr(int.from_bytes(b[i:i + 2], 'little')) for i in range(0, len(b), 2))


def _de_utf16(s):
    b = b''.join(ord(c).to_bytes(2, 'little') for c in s)
    return b.decode('utf-16-le', 'surrogatepass')


def slug(texto):
    t = _utf16(texto.lower())
    t = _REGEX.sub('', t).replace(' ', '-')
    return _de_utf16(t)


class GithubSlugger:
    def __init__(self):
        self.ocorrencias = {}

    def slug(self, texto):
        original = resultado = slug(texto)
        while resultado in self.ocorrencias:
            self.ocorrencias[original] += 1
            resultado = f'{original}-{self.ocorrencias[original]}'
        self.ocorrencias[resultado] = 0
        return resultado


def _sem_marcacao(t):
    t = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', t)                       # imagens: sem texto
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)                   # links: só o texto
    t = re.sub(r'<[A-Za-z][^>]*/>|</?[A-Za-z][^>]*>', '', t)         # tags e componentes inline
    t = re.sub(r'\\([!-/:-@\[-`{-~])', lambda m: '\x00%d\x00' % ord(m.group(1)), t)  # escapes
    t = re.sub(r'(\*\*|__|\*|(?<!\w)_|_(?!\w)|~~)', '', t)           # ênfase
    t = re.sub('\x00(\\d+)\x00', lambda m: chr(int(m.group(1))), t)
    return html.unescape(t)


def texto_do_titulo(md):
    """Texto puro de um título markdown (como o hast `toString` do rehype-slug)."""
    t = SUFIXO.sub('', md).strip()
    partes, pos = [], 0
    for m in re.finditer(r'(`+)(.+?)\1', t):
        partes.append(_sem_marcacao(t[pos:m.start()]))
        c = m.group(2)
        partes.append(c.strip(' ') if c.strip() else c)
        pos = m.end()
    partes.append(_sem_marcacao(t[pos:]))
    return ''.join(partes)


def titulos(texto):
    """[(nível, linha_index, texto_bruto)] dos títulos # fora de blocos cercados."""
    out, cerca = [], None
    # comentários {/* ... */} viram linhas em branco (mantém os índices de linha)
    texto = re.sub(r'\{/\*.*?\*/\}', lambda m: '\n' * m.group(0).count('\n'), texto, flags=re.S)
    linhas = texto.split('\n')
    for i, linha in enumerate(linhas):
        m = CERCA.match(linha)
        if cerca is None:
            if m:
                cerca = m.group(1)
                continue
            h = re.match(r'^(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$', linha)
            if h:
                out.append((len(h.group(1)), i, h.group(2)))
        elif m and m.group(1)[0] == cerca[0] and len(m.group(1)) >= len(cerca) and linha.strip() == m.group(1):
            cerca = None
    return out


def slugs_do_ingles(texto):
    s = GithubSlugger()
    return [s.slug(texto_do_titulo(t)) for _, _, t in titulos(texto)]
