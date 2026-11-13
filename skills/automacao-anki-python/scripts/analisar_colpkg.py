#!/usr/bin/env python3
"""Generate a minimal, privacy-preserving read-only audit of a .colpkg."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sqlite3
import sys
from anki_utils import open_colpkg,table_names,note_fronts,digest,normalized


def analyze(package: Path):
    with open_colpkg(package) as (db,member,has21b):
        tables=table_names(db)
        report={'arquivo':package.name,'sqlite_usado':member,'arquivo_modificado':False,'estatisticas':{},'alertas':[]}
        if has21b and member=='collection.anki2':
            report['alertas'].append('Arquivo .anki21b disponível, mas não interpretado; o .anki2 pode ser cópia reduzida e métricas incompletas.')
        for table in ('notes','cards','revlog'):
            if table in tables:
                report['estatisticas'][table]=db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            else:
                report['estatisticas'][table]=None
        if 'cards' in tables:
            cols={r[1] for r in db.execute('PRAGMA table_info(cards)')}
            if 'lapses' in cols:
                report['estatisticas']['lapsos_cartoes_soma']=db.execute('SELECT COALESCE(SUM(lapses),0) FROM cards').fetchone()[0]
                report['estatisticas']['cartoes_com_lapsos']=db.execute('SELECT COUNT(*) FROM cards WHERE lapses>0').fetchone()[0]
            if 'queue' in cols:
                report['estatisticas']['cartoes_suspensos']=db.execute('SELECT COUNT(*) FROM cards WHERE queue=-1').fetchone()[0]
        if 'revlog' not in tables or report['estatisticas']['revlog']==0:
            report['alertas'].append('Histórico de revisões ausente ou vazio: não estimar retenção.')
        fronts=note_fronts(db)
        by_hash={}
        for noteid,front in fronts:
            if len(normalized(front))<10:
                continue
            by_hash.setdefault(digest(front),[]).append(noteid)
        # Only identifiers, not original card text.
        report['duplicatas_exatas_candidatas']=[{'hash':key,'note_ids':ids} for key,ids in by_hash.items() if len(ids)>1][:100]
        report['alertas'].append('Duplicatas são apenas candidatas (mesmo primeiro campo normalizado); verificar modelos, versões e operações mentais.')
        report['alertas'].append('Este script não mede retenção sem métricas apropriadas e não lê imagens ou coleções inacessíveis.')
        return report


def main(argv=None):
    p=argparse.ArgumentParser(description='Analisar .colpkg somente leitura (JSON)')
    p.add_argument('backup',type=Path)
    p.add_argument('-o','--saida',required=True,type=Path)
    a=p.parse_args(argv)
    result=analyze(a.backup)
    a.saida.parent.mkdir(parents=True,exist_ok=True)
    a.saida.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'estatisticas':result['estatisticas'],'duplicatas_exatas':len(result['duplicatas_exatas_candidatas']),'saida':str(a.saida)},ensure_ascii=False))
    return 0

if __name__=='__main__':
    try: sys.exit(main())
    except Exception as exc: print(f'ERRO: {exc}',file=sys.stderr);sys.exit(1)

