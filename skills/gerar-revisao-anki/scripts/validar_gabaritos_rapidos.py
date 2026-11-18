#!/usr/bin/env python3
"""Audita a divisão C/E separadamente em rápidos e desafiadores.

Uso: python3 validar_gabaritos_rapidos.py pacote.zip
     python3 validar_gabaritos_rapidos.py anki_certo_errado.tsv
     python3 validar_gabaritos_rapidos.py pasta_do_pacote/

Integra a norma de equilíbrio de references/matriz_tipos_quantidades.md. Verifica *contagens*, não a
verdade jurídica, histórica ou científica das proposições.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import zipfile

ARQUIVO = 'anki_certo_errado.tsv'
TAG = 'Tipo_Revisao_Rapida'
HARD = 'Tipo_Desafiadora_Cebraspe'


def contar_rapidos(conteudo: bytes, strict_balance: bool = False, tag: str = TAG) -> tuple[dict, list[str]]:
    erros: list[str] = []
    try:
        linhas = conteudo.decode('utf-8-sig').splitlines()
    except UnicodeDecodeError:
        return {'rapidos': 0, 'certos': 0, 'errados': 0, 'percentual_certos': 0.0, 'percentual_errados': 0.0, 'excecao_impar': False}, ['TSV não é UTF-8 válido']

    certos = errados = 0
    for i, linha in enumerate(linhas, start=1):
        if not linha.strip():
            continue
        partes = linha.split('\t')
        if len(partes) != 3:
            erros.append(f'Linha {i}: quantidade incorreta de campos TSV')
            continue
        frente, verso, tags_texto = partes
        tags = set(tags_texto.split())
        if tag not in tags:
            continue  # contar cada modalidade separadamente
        if HARD in tags and TAG in tags:
            erros.append(f'Linha {i}: tags contraditórias rápida/desafiadora')
        if not frente.strip():
            erros.append(f'Linha {i}: frente vazia')
        if verso.startswith('✅ Certo<br><br>'):
            certos += 1
        elif verso.startswith('❌ Errado<br><br>'):
            errados += 1
        else:
            erros.append(f'Linha {i}: cartão C/E sem gabarito ✅ Certo ou ❌ Errado padronizado no início do verso')

    r = certos + errados
    if strict_balance and r and certos != errados:
        erros.append(f'Distribuição incorreta ({tag}): Certo={certos}, Errado={errados}; com R={r}, exigido 50% Certo e 50% Errado exatos')
    retorno = {'rapidos': r, 'certos': certos, 'errados': errados,
               'percentual_certos': round(100 * certos / r, 1) if r else 0.0,
               'percentual_errados': round(100 * errados / r, 1) if r else 0.0,
               'excecao_impar': bool(r % 2)}
    return retorno, erros


def contar_modos(conteudo: bytes, strict_balance: bool = False) -> tuple[dict, list[str]]:
    resultados, erros = {}, []
    for nome, tag in (('rapidos', TAG), ('desafiadores', HARD)):
        contagem, falhas = contar_rapidos(conteudo, strict_balance, tag)
        resultados[nome] = contagem
        erros.extend(falhas)
    return resultados, list(dict.fromkeys(erros))


def ler(path: Path) -> bytes:
    if path.is_dir():
        return (path / ARQUIVO).read_bytes()
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            if z.testzip() is not None:
                raise ValueError('CRC do pacote ZIP falhou')
            return z.read(ARQUIVO)
    if path.is_file() and path.name == ARQUIVO:
        return path.read_bytes()
    raise ValueError('Informe um ZIP, a pasta do pacote ou anki_certo_errado.tsv')


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('path', type=Path)
    p.add_argument('--strict-balance', action='store_true', help='Exigir 50/50 exato separadamente em rápidos e desafiadores')
    args = p.parse_args()
    try:
        counts, errors = contar_modos(ler(args.path), args.strict_balance)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f'REPROVADO: {exc}', file=sys.stderr)
        return 1
    for modo, dados in counts.items():
        print(f"{modo}: Certo={dados['certos']}; Errado={dados['errados']}")
    if errors:
        for error in errors:
            print('REPROVADO:', error, file=sys.stderr)
        return 1
    print('APROVADO NA CONTAGEM — não comprova a veracidade das afirmações')
    return 0


if __name__ == '__main__':
    sys.exit(main())
