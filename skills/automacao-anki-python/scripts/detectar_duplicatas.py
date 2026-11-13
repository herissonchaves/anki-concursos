#!/usr/bin/env python3
"""Suggest—not delete—possible literal and near-duplicate Anki fronts."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
from difflib import SequenceMatcher
import sys
from anki_utils import open_colpkg,note_fronts,normalized,digest


def fronts_tsv(path: Path):
    with Path(path).open('r',encoding='utf-8-sig',newline='') as f:
        for n,row in enumerate(csv.reader(f,delimiter='\t'),1):
            if not row or all(not x.strip() for x in row):
                continue
            if len(row)!=3:
                raise ValueError(f'Linha {n} tem {len(row)} campos; esperados 3')
            if n==1 and row[0].strip().lower() in ('frente','texto'):
                continue
            yield f'L{n}',row[0]


def score(a,b):
    try:
        from rapidfuzz.fuzz import ratio
        return round(ratio(a,b),1)
    except ImportError:
        return round(100*SequenceMatcher(None,a,b).ratio(),1)


def find_duplicates(new_cards, old_cards=(), threshold=88.0, limit=100):
    seen={}
    matches=[]
    old_norm=[(str(oldid),normalized(old)) for oldid,old in old_cards]
    for rowid,text in new_cards:
        value=normalized(text)
        if len(value)<16:
            continue
        for previous_id,previous_val in seen.items():
            v=score(value,previous_val)
            if v>=threshold:
                matches.append({'novo':rowid,'comparado_com':previous_id,'similaridade_textual':v,'tipo':'mesmo_lote','hash_novo':digest(text)})
        for oldid,old in old_norm:
            if len(old)<16:
                continue
            v=score(value,old)
            if v>=threshold:
                matches.append({'novo':rowid,'comparado_com':'anki:'+oldid,'similaridade_textual':v,'tipo':'backup','hash_novo':digest(text)})
                if len(matches)>=limit: break
        seen[rowid]=value
        if len(matches)>=limit:break
    return matches[:limit]


def main(argv=None):
    p=argparse.ArgumentParser(description='Sinalizar cartões possivelmente duplicados (sem apagar nada)')
    p.add_argument('tsv',type=Path)
    p.add_argument('--backup',type=Path)
    p.add_argument('--limiar',type=float,default=88.0)
    p.add_argument('--max-resultados',type=int,default=100)
    p.add_argument('-o','--saida',required=True,type=Path)
    a=p.parse_args(argv)
    if not (0<a.limiar<=100) or a.max_resultados<1:raise ValueError('Limiar (0,100] e limite >=1 são obrigatórios')
    novos=list(fronts_tsv(a.tsv))
    if a.backup:
        with open_colpkg(a.backup) as (db,member,has21b):
            antigos=note_fronts(db)
            backup_warning='Se .anki21b estiver presente, o índice .anki2 pode ser incompleto.' if has21b and member=='collection.anki2' else ''
    else:
        antigos=[];backup_warning='Nenhum backup foi fornecido.'
    result={'novos':len(novos),'comparados_backup':len(antigos),'limiar':a.limiar,'possiveis_duplicatas':find_duplicates(novos,antigos,a.limiar,a.max_resultados),
            'alertas':['Similaridade de texto não demonstra equivalência pedagógica; verificar negações, condições e habilidades mentais antes de excluir.',backup_warning]}
    a.saida.parent.mkdir(parents=True,exist_ok=True)
    a.saida.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'possiveis_duplicatas':len(result['possiveis_duplicatas']),'saida':str(a.saida)},ensure_ascii=False))
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:print(f'ERRO: {exc}',file=sys.stderr);sys.exit(1)

