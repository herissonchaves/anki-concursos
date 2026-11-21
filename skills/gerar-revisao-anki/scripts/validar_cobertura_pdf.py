#!/usr/bin/env python3
"""Confere a cobertura total de um lote feito a partir de PDF; NÃO julga a qualidade dos cards.

Uso: python validar_cobertura_pdf.py DIRETORIO_DO_LOTE_OU_ZIP
(o diretório é a pasta `lote/`, com os TSVs e `relatorios/cobertura_pdf.json`).

Falha se alguma unidade de conteúdo ou questão do PDF não tiver card, se apontar para linha
inexistente, se algum card do lote não cobrir nenhuma unidade, ou se faltar ao card a tag
`Pagina_NN` de uma página que ele cobre. Só texto que não é conteúdo de estudo pode ficar sem
card (`excluir: "nao_conteudo: motivo"`). Sem `cobertura_pdf.json`, informa e retorna 0
(lote que não veio de PDF). Retorna 0 (ok), 1 (falha) ou 2 (erro de leitura).
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

ARQUIVOS = ('anki_certo_errado.tsv', 'anki_cloze.tsv')
REGISTRO = 'relatorios/cobertura_pdf.json'


def ler(origem: Path) -> dict[str, bytes | None]:
    nomes = ARQUIVOS + (REGISTRO,)
    if origem.is_dir():
        return {n: (origem / n).read_bytes() if (origem / n).exists() else None for n in nomes}
    with zipfile.ZipFile(origem) as z:
        presentes = set(z.namelist())
        return {n: z.read(n) if n in presentes else None for n in nomes}


def linhas(dados: bytes | None) -> list[list[str]]:
    if not dados:
        return []
    return [l.split('\t') for l in dados.decode('utf-8').splitlines() if l.strip()]


def validar(arquivos: dict[str, bytes | None]) -> list[str]:
    registro = json.loads(arquivos[REGISTRO].decode('utf-8'))
    tsv = {n: linhas(arquivos[n]) for n in ARQUIVOS}
    erros, cobertos = [], {}
    unidades = registro.get('unidades')
    if registro.get('schema_version') != 1 or not isinstance(unidades, list) or not unidades:
        return ['cobertura_pdf.json: schema_version 1 e lista de unidades não vazia']
    for un in unidades:
        u, cartoes = un.get('u', '?'), un.get('cartoes') or []
        if un.get('excluir'):
            if not str(un['excluir']).startswith('nao_conteudo') or cartoes:
                erros.append(f'{u}: exclusão só para texto que não é conteúdo de estudo, sem cards')
            continue
        if not cartoes:
            erros.append(f'{u} (p. {un.get("pag")}): sem card')
        pags = un.get('pag') or []
        if not pags:
            erros.append(f'{u}: sem página')
        for ident in cartoes:
            nome, _, n = str(ident).partition(':')
            if nome not in tsv or not n.isdigit() or not 1 <= int(n) <= len(tsv[nome]):
                erros.append(f'{u}: card {ident} inexistente')
                continue
            cobertos.setdefault(ident, set()).update(int(p) for p in pags)
    for nome, rows in tsv.items():
        for n, row in enumerate(rows, 1):
            ident = f'{nome}:{n}'
            if ident not in cobertos:
                erros.append(f'{ident}: card sem unidade de cobertura')
                continue
            tags = set(row[2].split()) if len(row) == 3 else set()
            faltam = [f'Pagina_{p:02d}' for p in sorted(cobertos[ident]) if f'Pagina_{p:02d}' not in tags]
            if faltam:
                erros.append(f'{ident}: faltam as tags {", ".join(faltam)}')
    return erros


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('origem', type=Path)
    a = ap.parse_args(argv)
    try:
        arquivos = ler(a.origem)
        if arquivos[REGISTRO] is None:
            print('SEM cobertura_pdf.json: lote não declarado como revisão de PDF (nada a conferir)')
            return 0
        erros = validar(arquivos)
    except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        print(f'ERRO DE LEITURA: {exc}')
        return 2
    if erros:
        print('COBERTURA INCOMPLETA:\n  ' + '\n  '.join(erros))
        return 1
    n = len(json.loads(arquivos[REGISTRO].decode('utf-8'))['unidades'])
    print(f'COBERTURA COMPLETA: {n} unidade(s) do PDF com card e tags de página. Não certifica a qualidade dos cards.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
