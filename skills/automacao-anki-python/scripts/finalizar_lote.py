#!/usr/bin/env python3
"""Valida um lote pronto em `output/` em uma chamada, com saída curta. A entrega são os TSVs.

Uso (na raiz do repositório):

  uv run --no-project python -I -X utf8 skills/automacao-anki-python/scripts/finalizar_lote.py \
      output/PRF_Normas_Circulacao --baralho "Legislação de Trânsito"

Desde a 2.30 não grava ZIP nem APKG: confere a pasta `<lote>/lote/` (os relatórios obrigatórios,
`validar_anki.py --new`, `validar_calibracao_cebraspe.py`, `validar_revisao_pedagogica.py`, a cobertura
do PDF quando houver `cobertura_pdf.json` e `referencias.py validar`) e imprime o caminho dos dois TSVs a
importar. Avisa, sem bloquear, frentes parecidas com notas da coleção viva (`duplicatas_colecao.txt` na
pasta do lote) e `selecao_e_fontes.txt` sem a linha "Banco consultado:". Com tudo aprovado, grava (ou
substitui) a linha do lote em `referencias/historico_lotes.tsv`. Os validadores checam estrutura e
documentos; não certificam conteúdo. Pacote ZIP/APKG (ex.: lote com imagens) continua possível com
`exportar_anki.py`/`exportar_anki_visual.py`, fora deste fluxo.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve()
REPO = AQUI.parents[3]
GERAR = REPO / 'skills' / 'gerar-revisao-anki' / 'scripts'
REFERENCIAS = REPO / 'skills' / 'referencias-questoes' / 'scripts' / 'referencias.py'
HISTORICO = REPO / 'referencias' / 'historico_lotes.tsv'
TAB = '\t'
COLUNAS = ['data', 'lote', 'baralho', 'rapidos', 'desafiadores', 'cloze', 'ids_banco']


def contar(dados: Path) -> dict:
    tipos = {'rapidos': 0, 'desafiadores': 0, 'cloze': 0}
    for arq, chave in (('anki_certo_errado.tsv', None), ('anki_cloze.tsv', 'cloze')):
        with (dados / arq).open(encoding='utf-8-sig', newline='') as f:
            for row in csv.reader(f, delimiter=TAB):
                if len(row) < 3 or row[0].strip().lower() in ('frente', 'texto'):
                    continue
                tags = row[2].split()
                tipos[chave or ('desafiadores' if 'Tipo_Desafiadora_Cebraspe' in tags else 'rapidos')] += 1
    return tipos


def registrar_historico(lote: Path, baralho: str, dados: Path, historico: Path = HISTORICO) -> dict:
    """Uma linha por lote (substitui a anterior do mesmo lote): o que fica no Git do lote."""
    sys.path.insert(0, str(REFERENCIAS.parent))
    import referencias
    rotulo = lote.name
    ids = sorted(q.id for q in referencias.carregar()[0]
                 if any(str(u).startswith(f'{rotulo}#') for u in q.meta.get('usado_em', [])))
    linha = {'data': dt.date.today().isoformat(), 'lote': rotulo, 'baralho': baralho,
             **{k: str(v) for k, v in contar(dados).items()}, 'ids_banco': ';'.join(ids)}
    linhas = []
    if historico.exists():
        with historico.open(encoding='utf-8', newline='') as f:
            linhas = [l for l in csv.DictReader(f, delimiter=TAB) if l['lote'] != rotulo]
    linhas.append(linha)
    with historico.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, COLUNAS, delimiter=TAB, lineterminator='\n')
        w.writeheader()
        w.writerows(linhas)
    return linha


def avisos(lote: Path, dados: Path, colecao: str | None = None) -> list[str]:
    """Checagens que não bloqueiam: banco consultado (selecao_e_fontes.txt) e duplicatas na coleção viva."""
    saida = []
    selecao = dados / 'relatorios' / 'selecao_e_fontes.txt'
    texto = selecao.read_text(encoding='utf-8') if selecao.exists() else ''
    if not re.search(r'^\s*-?\s*Banco consultado:\s*\S', texto, flags=re.M | re.I):
        saida.append('banco: selecao_e_fontes.txt sem a linha "Banco consultado: <comandos ou IDs>"; '
                     'registre o que foi buscado em referencias/ antes da internet.')
    sys.path.insert(0, str(AQUI.parent))
    try:
        import colecao_anki
        with colecao_anki.Colecao(colecao_anki.find_collection(caminho=colecao)) as col:
            todos = []
            for arq in ('anki_certo_errado.tsv', 'anki_cloze.tsv'):
                if (dados / arq).stat().st_size:
                    achados = colecao_anki.duplicatas(col, dados / arq)['possiveis_duplicatas']
                    todos += [f'{arq}:{x["novo"]} ~ {x["comparado_com"]} ({x["similaridade_textual"]}%)' for x in achados]
        total, exemplos = len(todos), todos[:3]
        if todos:  # fica na pasta do lote (fora do Git), para conferir antes de importar
            (lote / 'duplicatas_colecao.txt').write_text('\n'.join(todos) + '\n', encoding='utf-8')
        if total:
            saida.append(f'duplicatas: {total} frente(s) parecida(s) com notas da coleção (ex.: {"; ".join(exemplos[:3])}). '
                         f'Semelhança de texto não prova redundância: confira com colecao_anki.py buscar.')
        else:
            print('OK  duplicatas: nenhuma frente parecida com notas da coleção viva')
    except SystemExit as exc:  # coleção ausente neste computador
        saida.append(f'duplicatas: coleção não lida ({exc}); compare com a coleção antes de importar.')
    except Exception as exc:
        saida.append(f'duplicatas: checagem falhou ({exc}).')
    return saida


def rodar(args: list[str]) -> tuple[int, str]:
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8', *args], capture_output=True, text=True, encoding='utf-8')
    return r.returncode, (r.stdout + r.stderr).strip()


IMPORTAR = ('Importe no Anki (Arquivo > Importar), um TSV por vez: separador Tabulação, "Permitir HTML" ligado, '
            "coluna 1 e 2 nos campos e coluna 3 em Etiquetas; C/E no tipo de nota Básico (sem inverso) do projeto e "
            "Cloze no tipo Cloze; TSV vazio não se importa. O CSS padrão (Arial 20 px) fica nos tipos de nota: "
            "skills/gerar-revisao-anki/scripts/estilo_anki.py.")


def relatorios_faltando(dados: Path) -> list[str]:
    """Relatórios obrigatórios ausentes ou vazios (os mesmos que o exportador exigia)."""
    sys.path.insert(0, str(AQUI.parent))
    from exportar_anki import REQUIRED_REPORTS
    rel = dados / 'relatorios'
    faltam = [n for n in REQUIRED_REPORTS if not (rel / n).is_file() or not (rel / n).stat().st_size]
    triagem = rel / 'triagem_previa_pdf.txt'
    if triagem.is_file() and not triagem.stat().st_size:
        faltam.append('triagem_previa_pdf.txt (vazio)')
    return faltam


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('lote', type=Path, help='pasta do lote (contém lote/ com os TSVs e relatorios/)')
    ap.add_argument('--baralho', required=True)
    ap.add_argument('--profile', choices=('mixed', 'focused'))
    ap.add_argument('--exception-reason')
    ap.add_argument('--max-cards')
    ap.add_argument('--colecao', help='collection.anki2 para a checagem de duplicatas (padrão: perfil concursos)')
    a = ap.parse_args(argv)
    lote = (a.lote if a.lote.is_absolute() else Path.cwd() / a.lote).resolve()
    dados = lote / 'lote'
    if not (dados / 'anki_certo_errado.tsv').exists() or not (dados / 'anki_cloze.tsv').exists():
        print(f'ERRO: {dados} sem anki_certo_errado.tsv/anki_cloze.tsv; rode fonte/gerar_lote.py antes')
        return 1
    faltam = relatorios_faltando(dados)
    if faltam:
        print('ERRO: relatório obrigatório ausente ou vazio (não fabricar auditoria): ' + ', '.join(faltam))
        return 1
    perfil = []
    for opcao, valor in (('--profile', a.profile), ('--exception-reason', a.exception_reason),
                         ('--max-cards', a.max_cards)):
        if valor:
            perfil += [opcao, valor]
    alvo = str(dados)
    checagens = [
        ('validar_anki --new', [str(GERAR / 'validar_anki.py'), '--new', alvo, *perfil]),
        ('calibração', [str(GERAR / 'validar_calibracao_cebraspe.py'), alvo]),
        ('revisão de recuperação', [str(GERAR / 'validar_revisao_pedagogica.py'), alvo]),
        ('banco referencias/', [str(REFERENCIAS), 'validar']),
    ]
    if (dados / 'relatorios' / 'cobertura_pdf.json').exists():
        checagens.append(('cobertura do PDF', [str(GERAR / 'validar_cobertura_pdf.py'), alvo]))
    falhas = 0
    for nome, args in checagens:
        codigo, saida = rodar(args)
        linhas = [l for l in saida.splitlines() if l.strip()]
        resumo = ' | '.join(l for l in linhas if re.search(r'Notas:|Modalidades:|total_cartoes|CONSISTENTE|COBERTURA|ERRO|FALHA', l))
        print(f'{"OK " if codigo == 0 else "FALHOU"} {nome}: {resumo or (linhas[-1] if linhas else "")}')
        if codigo:
            falhas += 1
            print('\n'.join(linhas[-15:]))
    for aviso in avisos(lote, dados, a.colecao):
        print(f'AVISO {aviso}')
    if not falhas:
        h = registrar_historico(lote, a.baralho, dados, HISTORICO)
        caminho = HISTORICO.relative_to(REPO).as_posix() if HISTORICO.is_relative_to(REPO) else HISTORICO
        print(f'Histórico: {caminho} ({h["rapidos"]} R, {h["desafiadores"]} D, '
              f'{h["cloze"]} Cloze; {len(h["ids_banco"].split(";")) if h["ids_banco"] else 0} IDs do banco)')
        print(f'TSV C/E:   {dados / "anki_certo_errado.tsv"}')
        print(f'TSV Cloze: {dados / "anki_cloze.tsv"}' + ('' if (dados / 'anki_cloze.tsv').stat().st_size else ' (vazio)'))
        print(f'Baralho: {a.baralho}. {IMPORTAR}')
    return 1 if falhas else 0


if __name__ == '__main__':
    sys.exit(main())
