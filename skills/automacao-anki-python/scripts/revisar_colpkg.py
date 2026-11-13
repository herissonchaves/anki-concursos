#!/usr/bin/env python3
"""Apply a human/agent-reviewed, complete field-only plan to an isolated Anki copy.

Requires the official anki Python package. Never opens a live profile, syncs,
deletes notes, resets scheduling, or changes the input package. Structural checks
do NOT certify the pedagogical decisions declared in the plan.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
import zipfile
from anki_utils import open_colpkg


def snapshot(package):
    with open_colpkg(Path(package)) as (db, _, _):
        return {t: db.execute(f'SELECT * FROM "{t}" ORDER BY rowid').fetchall()
                for t in ('notes', 'cards', 'revlog')}


def field_indices(fields):
    return {int(i) for i in re.findall(r'\{\{c(\d+)::', '\x1f'.join(fields))}


def validate_plan(plan, original):
    rows = plan['notes']
    ids = [r['id'] for r in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(original):
        raise ValueError('Plano deve cobrir todos os IDs exatamente uma vez')
    for r in rows:
        if r.get('decision') not in ('APROVAR', 'REFORMULAR') or not r.get('reason', '').strip():
            raise ValueError('Cada nota exige decisão e motivo de revisão semântica')
        old = original[r['id']]
        new = r['new_fields']
        if r['old_fields'] != old:
            raise ValueError('Plano desatualizado: conteúdo original divergente')
        if not isinstance(new, list) or len(new) != len(old) or not all(isinstance(f, str) for f in new):
            raise ValueError('Quantidade ou tipo dos campos divergente')
        if any('\x1f' in f or '\x00' in f for f in new):
            raise ValueError('Separador interno inválido em campo')
        if field_indices(old) != field_indices(new):
            raise ValueError('Não remover, adicionar ou renumerar índices Cloze neste fluxo')
        if r['decision'] == 'APROVAR' and new != old:
            raise ValueError('Nota aprovada sem reforma deve permanecer idêntica')
        if r['decision'] == 'REFORMULAR' and new == old:
            raise ValueError('Reformulação declarada sem mudança')


def revise(source, plan_path, output, report_path):
    from anki.collection import Collection
    from anki._backend import RustBackend
    source, output, report_path = map(Path, (source, output, report_path))
    if source.resolve() == output.resolve() or output.exists():
        raise ValueError('Use um novo caminho de saída; original e saídas existentes são preservados')
    if report_path.resolve() in (source.resolve(), output.resolve()) or report_path.exists():
        raise ValueError('Relatório deve usar caminho novo e distinto')
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    before = snapshot(source)
    original = {r[0]: r[6].split('\x1f') for r in before['notes']}
    plan = json.loads(Path(plan_path).read_text(encoding='utf-8'))
    validate_plan(plan, original)
    with tempfile.TemporaryDirectory(prefix='anki_revision_') as temporary:
        temp = Path(temporary)
        col_path = temp / 'collection.anki2'
        media = temp / 'collection.media'
        media.mkdir()
        # Private API isolated here; tested with anki 26.9.3. Fail closed on API change.
        RustBackend().import_collection_package(
            col_path=str(col_path), backup_path=str(source.resolve()),
            media_folder=str(media), media_db=str(temp / 'collection.media.db2'))
        media_before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in media.iterdir() if p.is_file()}
        col = Collection(str(col_path))
        try:
            for r in plan['notes']:
                if r['decision'] == 'REFORMULAR':
                    note = col.get_note(r['id'])
                    note.fields = r['new_fields']
                    col.update_note(note)
            # Render every real card through Anki's own template engine.
            rendered = []
            for cid in col.find_cards(''):
                c = col.get_card(cid)
                q, a = c.question(), c.answer()
                if not q.strip() or not a.strip():
                    raise ValueError(f'Cartão vazio: {cid}')
                rendered.append({'card_id': cid, 'note_id': c.nid, 'question': q, 'answer': a})
            staged = temp / 'revised.colpkg'
            col.export_collection_package(str(staged), include_media=True, legacy=False)
        finally:
            col.close()
        after = snapshot(staged)
        for table in ('cards', 'revlog'):
            if before[table] != after[table]:
                raise ValueError(f'Alteração inesperada em {table}: saída não liberada')
        expected = {r['id']: r['new_fields'] for r in plan['notes']}
        if {r[0]: r[6].split('\x1f') for r in after['notes']} != expected:
            raise ValueError('Conteúdo exportado não corresponde ao plano')
        for row in after['notes']:
            old = next(r for r in before['notes'] if r[0] == row[0])
            if any(old[i] != row[i] for i in (0, 1, 2, 5, 9, 10)):
                raise ValueError('Identidade, modelo, tags ou dados da nota alterados')
        if zipfile.ZipFile(staged).testzip() is not None:
            raise ValueError('Falha de integridade ZIP')
        # Re-import the exported package independently and compare every media byte.
        check = temp / 'roundtrip'; check.mkdir()
        check_media = check / 'collection.media'; check_media.mkdir()
        RustBackend().import_collection_package(
            col_path=str(check/'collection.anki2'), backup_path=str(staged),
            media_folder=str(check_media), media_db=str(check/'collection.media.db2'))
        media_after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in check_media.iterdir() if p.is_file()}
        if media_after != media_before:
            raise ValueError('Mídia original não preservada integralmente')
        if hashlib.sha256(source.read_bytes()).hexdigest() != source_hash:
            raise ValueError('Hash do original mudou')
        report = {'source_sha256': source_hash, 'notes': len(after['notes']),
                  'cards': len(after['cards']), 'revlog': len(after['revlog']),
                  'changed': sum(r['decision']=='REFORMULAR' for r in plan['notes']),
                  'media_files_preserved': len(media_before), 'cards_and_revlog_identical': True,
                  'official_backend_import_export_tested': True, 'desktop_gui_tested': False,
                  'rendered_cards': rendered}
        output.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation avoids overwriting an existing deliverable.
        with output.open('xb') as f: f.write(staged.read_bytes())
        with report_path.open('x', encoding='utf-8') as f: json.dump(report, f, ensure_ascii=False, indent=2)
        return {k:v for k,v in report.items() if k != 'rendered_cards'}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path); p.add_argument('plan', type=Path)
    p.add_argument('output', type=Path); p.add_argument('--report', required=True, type=Path)
    args=p.parse_args()
    print(json.dumps(revise(args.source,args.plan,args.output,args.report),ensure_ascii=False))
