#!/usr/bin/env python3
"""Exporta um lote para `output/` e revalida o ZIP final em uma chamada, com saída curta.

Uso (na raiz do repositório; genanki é necessário para o .apkg):

  uv run --no-project --with genanki python -I -X utf8 \
      skills/automacao-anki-python/scripts/finalizar_lote.py lotes/PRF/Missao_08_Tema --baralho "Legislação de Trânsito"

Destino: `output/<CONCURSO>_<Tema>/<CONCURSO>_<Tema>.zip|.apkg`, com <CONCURSO> = pasta acima
do lote e <Tema> = nome do lote sem o prefixo `Missao_NN_`. Nunca sobrescreve entregáveis
que ainda estejam em `output/`: usa sufixo `_2`, `_3`... Executa o exportador (que já roda os
validadores no diretório e no ZIP) e, no ZIP final, `validar_anki.py --new`,
`validar_calibracao_cebraspe.py` e `validar_revisao_pedagogica.py`, imprimindo só o resumo.
Os validadores checam estrutura e documentos; não certificam conteúdo.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve()
REPO = AQUI.parents[3]
GERAR = REPO / 'skills' / 'gerar-revisao-anki' / 'scripts'


def destino(lote: Path, nome: str | None) -> Path:
    concurso = lote.parent.name
    tema = nome or re.sub(r'^Missao_\d+_', '', lote.name)
    base = f'{concurso}_{tema}'
    pasta = REPO / 'output' / base
    alvo, n = pasta / base, 1
    while alvo.with_suffix('.zip').exists() or alvo.with_suffix('.apkg').exists():
        n += 1
        alvo = pasta / f'{base}_{n}'
    return alvo


def rodar(args: list[str]) -> tuple[int, str]:
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8', *args], capture_output=True, text=True, encoding='utf-8')
    return r.returncode, (r.stdout + r.stderr).strip()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('lote', type=Path, help='pasta do lote (contém lote/ com os TSVs e relatorios/)')
    ap.add_argument('--baralho', required=True)
    ap.add_argument('--nome', help='tema do arquivo final (padrão: nome do lote sem Missao_NN_)')
    ap.add_argument('--sem-apkg', action='store_true', help='gera só o ZIP (sem genanki)')
    ap.add_argument('--profile', choices=('mixed', 'focused'))
    ap.add_argument('--exception-reason')
    ap.add_argument('--max-cards')
    a = ap.parse_args(argv)
    lote = (a.lote if a.lote.is_absolute() else Path.cwd() / a.lote).resolve()
    dados = lote / 'lote'
    if not (dados / 'anki_certo_errado.tsv').exists() or not (dados / 'anki_cloze.tsv').exists():
        print(f'ERRO: {dados} sem anki_certo_errado.tsv/anki_cloze.tsv; rode fonte/gerar_lote.py antes')
        return 1
    alvo = destino(lote, a.nome)
    alvo.parent.mkdir(parents=True, exist_ok=True)
    perfil = []
    for opcao, valor in (('--profile', a.profile), ('--exception-reason', a.exception_reason),
                         ('--max-cards', a.max_cards)):
        if valor:
            perfil += [opcao, valor]
    exportar = [str(AQUI.parent / 'exportar_anki.py'), '--ce', str(dados / 'anki_certo_errado.tsv'),
                '--cloze', str(dados / 'anki_cloze.tsv'), '--relatorios', str(dados / 'relatorios'),
                '-o', str(alvo.with_suffix('.zip')), '--baralho', a.baralho, *perfil]
    if not a.sem_apkg:
        exportar += ['--apkg', str(alvo.with_suffix('.apkg'))]
    codigo, saida = rodar(exportar)
    if codigo:
        print('ERRO na exportação:\n' + saida[-3000:])
        return codigo
    zipado = str(alvo.with_suffix('.zip'))
    checagens = [
        ('validar_anki --new', [str(GERAR / 'validar_anki.py'), '--new', zipado, *perfil]),
        ('calibração', [str(GERAR / 'validar_calibracao_cebraspe.py'), zipado]),
        ('revisão de recuperação', [str(GERAR / 'validar_revisao_pedagogica.py'), zipado]),
    ]
    falhas = 0
    for nome, args in checagens:
        codigo, saida = rodar(args)
        linhas = [l for l in saida.splitlines() if l.strip()]
        resumo = ' | '.join(l for l in linhas if re.search(r'Notas:|Modalidades:|total_cartoes|CONSISTENTE|ERRO|FALHA', l))
        print(f'{"OK " if codigo == 0 else "FALHOU"} {nome}: {resumo or (linhas[-1] if linhas else "")}')
        if codigo:
            falhas += 1
            print('\n'.join(linhas[-15:]))
    print(f'ZIP:  {alvo.with_suffix(".zip")}')
    if not a.sem_apkg:
        print(f'APKG: {alvo.with_suffix(".apkg")}  (duplo clique com o Anki aberto)')
    return 1 if falhas else 0


if __name__ == '__main__':
    sys.exit(main())
