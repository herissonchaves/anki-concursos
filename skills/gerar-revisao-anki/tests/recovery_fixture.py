"""Fixture DOCUMENTAL FICTÍCIA. Não importar em código de produção.

Gera declarações sintéticas para testar transporte/esquema, sem revisão semântica.
Fontes .test e justificativas abaixo não são evidência de conteúdo real.
"""
import importlib.util
import json
from pathlib import Path

_path = Path(__file__).resolve().parents[1]/'scripts/validar_revisao_pedagogica.py'
_spec = importlib.util.spec_from_file_location('recovery_fixture_check', _path)
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)


def make_review(items):
    records = []
    rows = check.cards(items)
    challenges = [row['id'] for row in rows if row['tipo'] == 'desafiadora']
    for row in rows:
        if row['tipo'] not in ('rapida', 'cloze'):
            continue
        records.append(dict(id=row['id'], sha256=check.fingerprint([row['front'],row['back'],row['tags']]),
            alvo='Fixture sintética, não alvo de estudo aprovado',
            solucao='Declaração fictícia de solução para testar esquema',
            alternativa_concorrente='Não avaliada semanticamente nesta fixture documental',
            recuperacao='Justificativa fictícia de recuperação', feedback='Feedback fictício para teste de transporte',
            fontes=[dict(url='https://example.test/fonte',consulta='2026-11-08',trecho='Fonte FICTÍCIA de teste')],
            segunda_conferencia=True,decisao='APROVAR'))
        if row['tipo'] == 'cloze':
            records[-1]['desafiadores_por_lacuna'] = {
                str(number): challenges[:1]
                for number, _ in enumerate(check.structure.CLOZE_ANY.finditer(row['front']), 1)
            }
    return dict(schema_version=1,sha256_lote=check.batch_hash(items),
        revisor='Fixture automatizada; NÃO houve revisão pedagógica',tipo_revisao='autorevisao',cartoes=records,
        sinais=[dict(sinal_id=issue['sinal_id'],decisao='EXCECAO_JUSTIFICADA',motivo='Fixture para testar o transporte da resolução; não é justificativa pedagógica real') for issue in check.signals(items)])


def write_review(ce, cloze, reports):
    items = {check.FILES[0]:Path(ce).read_bytes(),check.FILES[1]:Path(cloze).read_bytes()}
    target = Path(reports)/Path(check.REPORT).name
    target.write_text(json.dumps(make_review(items),ensure_ascii=False),encoding='utf-8')
    return target
