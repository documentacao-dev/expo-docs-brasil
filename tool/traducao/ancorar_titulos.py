#!/usr/bin/env python3
"""Acrescenta ` \\{#id}` (id em inglês) aos títulos das páginas traduzidas.

Para cada .mdx com o marcador `{/* ia-translate: true */}` na última linha, lê o
inglês do commit em ultimo-sync-upstream.txt, calcula o slug de cada título # do
inglês (mesmo algoritmo do site, com -1, -2 para repetidos) e grava no título
traduzido correspondente (na mesma ordem) o sufixo ` \\{#slug}`; se já houver, corrige.
A barra é necessária porque `{...}` solto é uma expressão no MDX; o site remove o
sufixo do texto e usa o id no `<h2 id>` e no sumário lateral.

Uso: python3 tool/traducao/ancorar_titulos.py [caminhos .mdx...]
"""
import sys
from pathlib import Path

from slugger import SUFIXO, slugs_do_ingles, titulos
from verificar import commit_upstream, ingles, paginas, traduzido


def ancorar(p, commit):
    en = ingles(p, commit)
    if en is None:
        print(f'ERRO {p}: não existe no upstream')
        return False
    pt = p.read_text()
    te, tp = slugs_do_ingles(en), titulos(pt)
    if len(te) != len(tp):
        print(f'ERRO {p}: {len(te)} títulos no inglês, {len(tp)} na tradução')
        return False
    linhas = pt.split('\n')
    for slug_en, (_, i, bruto) in zip(te, tp):
        linhas[i] = linhas[i].replace(bruto, SUFIXO.sub('', bruto) + ' \\{#' + slug_en + '}', 1)
    novo = '\n'.join(linhas)
    if novo != pt:
        p.write_text(novo)
        print(f'ancorado {p}')
    return True


def main():
    commit = commit_upstream()
    args = sys.argv[1:]
    arquivos = [Path(a).resolve() for a in args] if args else [p for p in paginas() if traduzido(p.read_text())]
    ok = all([ancorar(p, commit) for p in arquivos])
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
