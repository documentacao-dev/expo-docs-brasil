#!/usr/bin/env python3
"""Confere as páginas traduzidas da documentação do Expo contra o inglês.

Para cada docs/pages/**/*.mdx (fora de pages/ja/ e pages/versions/) cuja ÚLTIMA
linha é `{/* ia-translate: true */}`, compara com o inglês do commit em
tool/traducao/ultimo-sync-upstream.txt (`git show`):

- blocos de código cercados idênticos e na mesma ordem;
- linhas de import idênticas;
- tags JSX de componentes (<Maiuscula ...>, </Maiuscula>) idênticas, exceto o
  texto de atributos visíveis (title, description, label, sidebar_title, summary,
  header, alt, caption), que pode ser traduzido;
- URLs de links markdown idênticas;
- mesmo número (e nível) de títulos #;
- frontmatter com as mesmas chaves; title/description/sidebar_title podem ser
  traduzidos, o resto fica idêntico;
- comentários {/* */} idênticos (exceto o marcador);
- título traduzido termina com ` \\{#id}` igual ao slug do título em inglês (ancorar_titulos.py grava);
- código inline que não existe no inglês vira AVISO.

Uso: python3 tool/traducao/verificar.py [caminhos .mdx...]
Saída: `ERRO arquivo: ...` e `N arquivo(s) traduzido(s), M erro(s)`; exit 1 se houver erro.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

from slugger import SUFIXO, slugs_do_ingles, texto_do_titulo, titulos as titulos_md

GIT_ROOT = Path(__file__).resolve().parents[2]
ROOT = Path(os.environ.get('VERIFICAR_RAIZ') or Path(__file__).resolve().parents[2])
PAGES = ROOT / 'docs' / 'pages'
MARCADOR = '{/* ia-translate: true */}'
EXCLUIDOS = ('ja', 'versions')
ATTR_TRADUZIVEIS = ('title', 'description', 'label', 'sidebar_title', 'summary', 'header', 'alt', 'caption')
FRONTMATTER_TRADUZIVEL = ('title', 'description', 'sidebar_title')


def paginas():
    for p in sorted(PAGES.rglob('*.mdx')):
        partes = p.relative_to(PAGES).parts
        if partes[0] in EXCLUIDOS:
            continue
        yield p


def traduzido(texto):
    linhas = [l for l in texto.splitlines() if l.strip()]
    return bool(linhas) and linhas[-1].strip() == MARCADOR


def commit_upstream():
    return (Path(__file__).parent / 'ultimo-sync-upstream.txt').read_text().strip()


def ingles(p, commit):
    rel = p.resolve().relative_to(ROOT).as_posix()
    r = subprocess.run(['git', '-C', str(GIT_ROOT), 'show', f'{commit}:{rel}'],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def separar_frontmatter(t):
    m = re.match(r'---\n(.*?)\n---\n?', t, re.S)
    return (m.group(1), t[m.end():]) if m else ('', t)


def chaves_frontmatter(fm):
    """Devolve {chave: bloco de texto} (inclui linhas de continuação)."""
    out, atual = {}, None
    for linha in fm.splitlines():
        m = re.match(r'([A-Za-z_][\w-]*):(.*)$', linha)
        if m:
            atual = m.group(1)
            out[atual] = linha
        elif atual:
            out[atual] += '\n' + linha
    return out


def extrair_codigo(t):
    """Separa blocos cercados (``` ou ~~~). Devolve (blocos, texto sem os blocos)."""
    blocos, resto, dentro, cerca = [], [], None, None
    for linha in t.split('\n'):
        m = re.match(r'^\s*(`{3,}|~{3,})', linha)
        if dentro is None:
            if m:
                cerca, dentro = m.group(1), [linha]
            else:
                resto.append(linha)
        else:
            dentro.append(linha)
            if m and m.group(1)[0] == cerca[0] and len(m.group(1)) >= len(cerca) and linha.strip() == m.group(1):
                blocos.append('\n'.join(dentro))
                dentro = None
    if dentro is not None:
        blocos.append('\n'.join(dentro))
    return blocos, '\n'.join(resto)


def tags_jsx(t):
    """Tags JSX com maiúscula (abertura e fechamento), inteiras, normalizadas."""
    tags, i, n = [], 0, len(t)
    while i < n:
        m = re.compile(r'</?[A-Z]').search(t, i)
        if not m:
            break
        j, prof, aspas = m.end(), 0, None
        while j < n:
            c = t[j]
            if aspas:
                if c == '\\':
                    j += 1
                elif c == aspas:
                    aspas = None
            elif c in '"\'`':
                aspas = c
            elif c == '{':
                prof += 1
            elif c == '}':
                prof -= 1
            elif c == '>' and prof <= 0:
                break
            j += 1
        tags.append(re.sub(r'\s+', ' ', t[m.start():j + 1]))
        i = j + 1
    return tags


ELEMENTO_INLINE = re.compile(r'<([A-Za-z][\w.]*)\b[^>]*?/>|<([A-Za-z][\w.]*)\b[^>]*>.*?</\2>', re.S)


def _fim_da_chave(t, i):
    """Índice da `}` que fecha a `{` em t[i] (ignora chaves dentro de aspas)."""
    prof, aspas = 0, None
    for j in range(i, len(t)):
        c = t[j]
        if aspas:
            if c == '\\':
                continue
            if c == aspas:
                aspas = None
        elif c in '"\'`':
            aspas = c
        elif c == '{':
            prof += 1
        elif c == '}':
            prof -= 1
            if prof == 0:
                return j
    return -1


def neutralizar_atributos(tag):
    """Esvazia o texto dos atributos visíveis. Aceita "..." e {<>...</>}; no caso da
    expressão só os elementos internos (<CODE>@</CODE>) são comparados, o texto solto muda."""
    nomes = '|'.join(ATTR_TRADUZIVEIS)
    tag = re.sub(rf'\b({nomes})="[^"]*"', r'\1=""', tag)
    tag = re.sub(rf"\b({nomes})='[^']*'", r"\1=''", tag)
    out, pos = [], 0
    for m in re.finditer(rf'\b({nomes})=\{{', tag):
        if m.start() < pos:
            continue
        ini = m.end() - 1
        fim = _fim_da_chave(tag, ini)
        if fim < 0:
            continue
        inner = tag[ini + 1:fim].strip()
        if inner.startswith('<>') and inner.endswith('</>'):
            # Código (<CODE>, <A ...>) conta inteiro; formatação (<span>, <i>, <b>, <em>,
            # <strong>) é texto visível: conta só a tag, não o conteúdo.
            elementos = ' '.join(
                re.sub(r'>[^<]*<', '><', e.group(0)) if re.match(r'<(span|i|b|em|strong)\b', e.group(0)) else e.group(0)
                for e in ELEMENTO_INLINE.finditer(inner[2:-3]))
            out.append(tag[pos:m.start()] + f'{m.group(1)}={{<>{elementos}</>}}')
            pos = fim + 1
    out.append(tag[pos:])
    tag = ''.join(out)
    if tag.startswith('<FileTree'):
        # files={[['caminho', 'descrição visível'], ...]}: a descrição pode ser traduzida
        tag = re.sub(r"(\[\s*'[^']*'\s*,\s*)'[^']*'(\s*\])", r"\1''\2", tag)
        tag = re.sub(r'(\[\s*\'[^\']*\'\s*,\s*)"[^"]*"(\s*\])', r"\1''\2", tag)
    return tag


def codigo_inline(t):
    return {m.group(2).strip() for m in re.finditer(r'(`+)(.+?)\1', t, re.S)}


def conferir(p, commit):
    rel = p.resolve().relative_to(ROOT).as_posix()
    en = ingles(p, commit)
    if en is None:
        return [f'{rel}: não existe no upstream ({commit[:9]})'], []
    pt = p.read_text()
    erros, avisos = [], []

    # frontmatter
    fe, corpo_en = separar_frontmatter(en)
    fp, corpo_pt = separar_frontmatter(pt)
    ke, kp = chaves_frontmatter(fe), chaves_frontmatter(fp)
    if list(ke) != list(kp):
        erros.append(f'chaves do frontmatter diferentes: inglês {list(ke)}, tradução {list(kp)}')
    else:
        for k in ke:
            if k not in FRONTMATTER_TRADUZIVEL and ke[k] != kp[k]:
                erros.append(f'frontmatter: `{k}` deve ficar idêntico ao inglês')

    # código cercado
    be, se = extrair_codigo(corpo_en)
    bp, sp = extrair_codigo(corpo_pt)
    if be != bp:
        erros.append(f'blocos de código: {len(be)} no inglês, {len(bp)} na tradução'
                     + (' (conteúdo diferente)' if len(be) == len(bp) else ''))

    # imports
    imp = lambda t: [l.strip() for l in t.splitlines() if re.match(r'import\s', l)]
    if imp(se) != imp(sp):
        erros.append('linhas de import diferentes do inglês')

    # comentários {/* */}
    com = re.compile(r'\{/\*.*?\*/\}', re.S)
    ce = com.findall(se)
    cp = [c for c in com.findall(sp) if c.strip() != MARCADOR]
    if ce != cp:
        erros.append(f'comentários {{/* */}} diferentes do inglês ({len(ce)} no inglês, {len(cp)} na tradução)')

    # texto sem comentários para o resto
    se2, sp2 = com.sub('', se), com.sub('', sp)

    # props JSX
    te = [neutralizar_atributos(x) for x in tags_jsx(re.sub(r'`[^`\n]*`', '', se2))]
    tp = [neutralizar_atributos(x) for x in tags_jsx(re.sub(r'`[^`\n]*`', '', sp2))]
    if te != tp:
        if len(te) != len(tp):
            erros.append(f'tags JSX: {len(te)} no inglês, {len(tp)} na tradução')
        else:
            for a, b in zip(te, tp):
                if a != b:
                    erros.append(f'tag JSX diferente do inglês: `{a[:80]}` -> `{b[:80]}`')
                    break

    # URLs de links markdown
    url = lambda t: re.findall(r'\]\(([^)\s]+)', re.sub(r'`[^`\n]*`', '', t))
    if url(se2) != url(sp2):
        erros.append('URLs de links markdown diferentes do inglês')

    # títulos
    tit = lambda t: [len(m.group(1)) for m in re.finditer(r'^(#{1,6})\s', t, re.M)]
    if tit(se2) != tit(sp2):
        erros.append(f'títulos #: {len(tit(se2))} no inglês, {len(tit(sp2))} na tradução (ou níveis diferentes)')

    # ids dos títulos: o título traduzido leva ` \\{#id}` com o slug do inglês
    tm_en, tm_pt, sl_en = titulos_md(en), titulos_md(pt), slugs_do_ingles(en)
    if len(tm_en) == len(tm_pt):
        for (_, _, bruto_en), (_, _, bruto_pt), slug_en in zip(tm_en, tm_pt, sl_en):
            m = SUFIXO.search(bruto_pt)
            mudou = texto_do_titulo(bruto_pt) != texto_do_titulo(bruto_en)
            if m and not re.search(r'\\\{#', bruto_pt):
                erros.append(f'título "{bruto_pt[:50]}": escreva `\\{{#{slug_en}}}` com a barra (`{{#id}}` solto quebra o MDX)')
            elif m and m.group(1) != slug_en:
                erros.append(f'título "{bruto_pt[:50]}": id `{m.group(1)}`, deveria ser `{slug_en}` (rode ancorar_titulos.py)')
            elif not m and mudou:
                erros.append(f'título "{bruto_pt[:50]}": falta ` \\{{#{slug_en}}}` (rode ancorar_titulos.py)')

    # código inline novo
    for c in sorted(codigo_inline(sp2) - codigo_inline(se2))[:5]:
        avisos.append(f'{rel}: código inline que não existe no inglês (traduzido?): `{c}`')

    return [f'{rel}: {e}' for e in erros], avisos


def main():
    args = sys.argv[1:]
    commit = commit_upstream()
    arquivos = [Path(a).resolve() for a in args] if args else [p for p in paginas() if traduzido(p.read_text())]
    todos_erros = []
    for p in arquivos:
        erros, avisos = conferir(p, commit)
        todos_erros += erros
        for a in avisos:
            print(f'AVISO {a}')
    for e in todos_erros:
        print(f'ERRO {e}')
    print(f'{len(arquivos)} arquivo(s) traduzido(s), {len(todos_erros)} erro(s)')
    sys.exit(1 if todos_erros else 0)


if __name__ == '__main__':
    main()
