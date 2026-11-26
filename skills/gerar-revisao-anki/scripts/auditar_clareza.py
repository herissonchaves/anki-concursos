#!/usr/bin/env python3
"""Sinais heurísticos de clareza em lotes Anki. NÃO valida qualidade pedagógica.

Uso: python3 auditar_clareza.py PACOTE.zip --report relatorios/sinais_clareza.tsv
     python3 auditar_clareza.py anki_certo_errado.tsv
     python3 auditar_clareza.py DIRETORIO_DO_LOTE/

Diagnóstico não bloqueante; revisão humana de 100% dos cartões continua obrigatória.
"""
from __future__ import annotations

import argparse
import csv
from difflib import SequenceMatcher
import html
import io
from pathlib import Path
import re
import sys
import unicodedata
import zipfile

C_E = 'anki_certo_errado.tsv'
CLOZE = 'anki_cloze.tsv'
ABSOLUTES = re.compile(r'\b(sempre|nunca|jamais|necessariamente|automaticamente|qualquer|somente|apenas|todos os casos|em todos os casos)\b', re.I)
META = re.compile(r'\b(?:segundo|conforme|de acordo com)\s+(?:o|a|este|esta|esse|essa)?\s*(?:pdf|material|apostila|arquivo|aula)\b|\b(?:o|a)\s+(?:material|pdf|apostila)\s+(?:afirma|diz|indica|define|considera)\b|\bdoutrina indicada no material\b', re.I)
HTML = re.compile(r'<[^>]+>')
CLOZE_REGEX = re.compile(r'\{\{c\d+::([^{}]*?)(?:::[^{}]*?)?\}\}')


def plain(text: str) -> str:
    text = CLOZE_REGEX.sub(lambda m: m.group(1), text)
    return html.unescape(HTML.sub(' ', text))


def folded(text: str) -> str:
    text = plain(text)
    text = ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]+', ' ', text)).strip()


def _read_bytes(path: Path) -> dict[str, bytes]:
    if path.is_dir():
        files = {n: (path/n).read_bytes() for n in (C_E, CLOZE) if (path/n).is_file()}
    elif path.is_file() and path.suffix.lower() == '.tsv':
        files = {path.name: path.read_bytes()}
    elif path.is_file() and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            if z.testzip() is not None:
                raise ValueError('Falha de CRC no ZIP')
            files = {n: z.read(n) for n in (C_E, CLOZE) if n in z.namelist()}
    else:
        raise ValueError('Informe pasta do pacote, ZIP válido ou .tsv')
    if not files:
        raise ValueError('Nenhum TSV reconhecido encontrado')
    return files


def load_cards(path: Path) -> list[dict[str, str]]:
    rows = []
    for filename, body in _read_bytes(path).items():
        content = body.decode('utf-8-sig')
        for line_no, line in enumerate(content.splitlines(), 1):
            if not line.strip():
                continue
            cells = line.split('\t')
            if len(cells) != 3:
                raise ValueError(f'{filename}:{line_no}: esperados 3 campos TSV')
            front, back, tags = cells
            typ = ('cloze' if filename == CLOZE else 'rapida' if {'Rapida', 'Tipo_Revisao_Rapida'} & set(tags.split()) else 'desafiadora' if {'Desafiadora', 'Tipo_Desafiadora_Cebraspe'} & set(tags.split()) else 'C/E-sem-tipo')
            rows.append({'id':f'{filename}:{line_no}', 'front':front, 'back':back, 'tags':tags, 'tipo':typ})
    return rows


def scan(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    def warn(card: dict[str,str], code: str, details: str):
        issues.append({'id':card['id'],'tipo':card['tipo'],'sinal':code,'detalhes':details,'decisao_humana':'PENDENTE'})
    for c in rows:
        front = plain(c['front']).strip()
        words = len(front.split())
        # 2.39 (modo rápido): frente de 8 a 15 palavras com um fato só; verso com regra em 1 frase + Memorize.
        if c['tipo'] == 'rapida' and words > 20:
            warn(c,'FRENTE_RAPIDA_EXTENSA',f'{words} palavras; R mira 8 a 15: um fato só, sem caso nem exceção')
        if c['tipo'] == 'rapida' and len(plain(c['back']).split()) > 80:
            warn(c,'VERSO_RAPIDO_EXTENSO',f'{len(plain(c["back"]).split())} palavras; R pede regra em 1 frase + Memorize')
        # 2.40: Cloze de conceito-chave em uma frase curta; mnemônico ("Mnemônico SIGLA:") não tem limite.
        mnemonico = re.match(r'(?:<[^>]+>|\s)*Mnem[oô]nico\s+[^:<]{1,40}:', c['front'], re.I)
        if c['tipo'] == 'cloze' and not mnemonico and words > 30:
            warn(c,'CLOZE_FRENTE_EXTENSA',f'{words} palavras; Cloze de conceito pede uma frase curta (mnemônico não tem limite)')
        elif c['tipo'] == 'desafiadora' and words > 50:
            warn(c,'FRENTE_DESAFIADORA_EXTENSA',f'{words} palavras; avaliar se a extensão agrega inferência')
        if META.search(front) or META.search(plain(c['back'])):
            warn(c,'REFERENCIA_EXTERNA','Referência a material/aula; cartão deve ser autossuficiente')
        found = ABSOLUTES.findall(front)
        if found and c['tipo'] in ('rapida','desafiadora'):
            warn(c,'ABSOLUTO_PISTA_POSSIVEL',', '.join(found[:5]))
        if c['tipo'] == 'desafiadora' and words < 12:
            warn(c,'DESAFIO_CURTO_VERIFICAR','Checar se há inferência real; concisão não é erro')
        back = folded(c['back'])
        if re.search(r'<img\b[^>]*\bsrc\s*=\s*[\"\x27]?https?://',c['front']+c['back'],re.I):
            warn(c,'MIDIA_REMOTA','Imagem não incorporada; verificar uso offline e suficiência do contexto visual')
        if re.search(r'\b(voce acertou|parabens pelo acerto)\b',back):
            warn(c,'ACERTO_PRESUMIDO','Exibir gabarito sem presumir resposta do aluno')
        if c['tipo']=='cloze':
            # 2.33: mnemônico no formato (título + letras visíveis + resto em c1) já recupera os termos.
            formato = re.match(r'(?:<[^>]+>|\s)*Mnem[oô]nico\s+[^:<]{1,40}:', c['front'], re.I)
            if not formato and re.search(r'\b(mnemonico|sigla|a letra)\b',folded(c['front'])):
                warn(c,'MEMORIA_DE_SIGLA','Avaliar se a lacuna recupera conceito útil ou só a sigla/letra')
            # Check each view independently: other indices stay visible.
            pattern=re.compile(r'\{\{c(\d+)::([^{}]*?)(?:::[^{}]*?)?\}\}')
            matches=list(pattern.finditer(c['front']))
            for index in sorted({m[1] for m in matches}):
                visible=pattern.sub(lambda m: ' ' if m[1]==index else m[2],c['front'])
                visible=' '+folded(visible)+' '
                for number, m in enumerate(matches, 1):
                    answer=folded(m[2])
                    if m[1]==index and len(answer)>=4 and ' '+answer+' ' in visible:
                        gap = f', lacuna {number}' if len(matches) > 1 else ''
                        warn(c,'RESPOSTA_CLOZE_VISIVEL',f'c{index}{gap}: resposta reaparece no texto visível; revisar a vista')
        if len(back) < 55:
            warn(c,'VERSO_MUITO_CURTO','Verificar se explica regra e dado decisivo, não só gabarito')
    # Similaridade lexical sinaliza revisão cognitiva, nunca remoção automática.
    # Limitamos pares para que um pacote grande não cause processamento excessivo.
    normalized = [(c,folded(c['front'])) for c in rows]
    for i in range(len(normalized)):
        if i > 1500:
            break
        a, ta = normalized[i]
        if len(ta) < 35:
            continue
        for b,tb in normalized[i+1:]:
            if abs(len(ta)-len(tb)) > max(len(ta),len(tb))*.35 or len(tb)<35:
                continue
            score = SequenceMatcher(None,ta,tb,autojunk=True).ratio()
            if score >= .84:
                warn(b,'SEMELHANCA_LEXICAL',f'Com {a["id"]}; escore={score:.2f} (NÃO comprova repetição cognitiva)')
    quick = [c for c in rows if c['tipo']=='rapida']
    flagged_wrong = sum(1 for c in quick if ABSOLUTES.search(plain(c['front'])) and c['back'].startswith('❌ Errado'))
    total_wrong = sum(1 for c in quick if c['back'].startswith('❌ Errado'))
    if total_wrong >= 4 and flagged_wrong/total_wrong > .65:
        warn({'id':'LOTE','tipo':'lote'},'PADRAO_ABSOLUTOS_ERRADOS', f'{flagged_wrong}/{total_wrong} rápidos Errados contêm absoluto; revisar pistas na distribuição')
    return issues


def save_report(issues: list[dict[str,str]], report: Path) -> None:
    report.parent.mkdir(parents=True,exist_ok=True)
    with report.open('w',newline='',encoding='utf-8') as out:
        writer=csv.DictWriter(out,fieldnames=['id','tipo','sinal','detalhes','decisao_humana'],delimiter='\t',lineterminator='\n')
        writer.writeheader()
        writer.writerows(issues)


def main(argv: list[str]|None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args(argv)
    try:
        cards=load_cards(args.source)
        issues=scan(cards)
        if args.report:
            save_report(issues,args.report)
    except (OSError,UnicodeError,ValueError,zipfile.BadZipFile) as exc:
        print(f'ERRO DE LEITURA: {exc}',file=sys.stderr)
        return 2
    print(f'{len(cards)} cartões verificados; {len(issues)} sinais heurísticos encontrados.')
    for w in issues[:15]:
        print(f' - {w["id"]}: {w["sinal"]} — {w["detalhes"]}')
    if len(issues)>15:print(f' ... mais {len(issues)-15} sinais no relatório')
    print('ATENÇÃO: sinal de risco não é erro comprovado nem auditoria semântica. Revisar 100% dos cartões individualmente.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

