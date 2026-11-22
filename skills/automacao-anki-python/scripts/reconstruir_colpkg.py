#!/usr/bin/env python3
"""Rebuild a .colpkg from a backup, on an isolated copy: edit fields and tags of every note and
add the notes of reviewed batch TSVs. Never deletes notes or cards, never touches scheduling or
review history, never opens a live profile and never syncs.

Requires the official anki Python package (tested with 26.9.3). Plan JSON:

    {"editar": [{"id": 1, "old_fields": [...], "new_fields": [...],   # new_fields optional
                 "old_tags": "a b", "new_tags": "c d", "reason": "..."}],   # one per existing note
     "adicionar": [{"tsv": "lote/anki_certo_errado.tsv", "deck": "Direito Penal",
                    "notetype": "Basic"}]}

Every existing note must appear exactly once in `editar`. TSV rows have three columns (front,
back/extra, tags), as written by montar_lote.py. Each final note must pass the 2.33 tag rules
(`regras_tags.problemas_tags`) and every Cloze mnemonic the format rules. Structural checks do
NOT certify the pedagogical decisions in the plan.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import zipfile

from anki_utils import open_colpkg

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'gerar-revisao-anki' / 'scripts'))
import regras_tags as rt  # noqa: E402


def snapshot(package):
    with open_colpkg(Path(package)) as (db, _, _):
        out = {t: db.execute(f'SELECT * FROM "{t}" ORDER BY rowid').fetchall()
               for t in ('notes', 'cards', 'revlog')}
        out['notetypes'] = dict(db.execute('SELECT id, name FROM notetypes').fetchall())
        out['decks'] = dict(db.execute('SELECT id, name FROM decks').fetchall())
        return out


def cloze_indices(fields):
    return {int(i) for i in re.findall(r'\{\{c(\d+)::', '\x1f'.join(fields))}


def read_tsv(path):
    rows = []
    for n, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip() or line.startswith('#'):
            continue
        cols = line.split('\t')
        if len(cols) != 3:
            raise ValueError(f'{path}:{n}: esperado 3 colunas (frente, verso, tags), achou {len(cols)}')
        rows.append(cols)
    return rows


def tipo_da_nota(is_cloze, tags):
    if is_cloze:
        return rt.CLOZE
    t = tags.split()
    return rt.DESAFIADORA if rt.DESAFIADORA in t else rt.RAPIDA


def problemas_nota(is_cloze, fields, tags):
    erros = rt.problemas_tags(tags, tipo_da_nota(is_cloze, tags))
    if not is_cloze and not ({rt.RAPIDA, rt.DESAFIADORA} & set(tags.split())):
        erros.append('nota Basic sem tag Rapida ou Desafiadora')
    if is_cloze:
        frente, extra = fields[0], (fields[1] if len(fields) > 1 else '')
        if rt.mnemonico_fora_do_formato(frente):
            erros.append('mnemônico fora do formato (sem "Mnemônico SIGLA:")')
        elif rt.sigla_mnemonico(frente):
            erros += rt.problemas_mnemonico(frente, extra)
    return erros


def validate_plan(plan, original, notetypes_by_note):
    rows = plan.get('editar', [])
    ids = [r['id'] for r in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(original):
        raise ValueError('Plano deve cobrir todas as notas existentes exatamente uma vez (nenhuma exclusão)')
    for r in rows:
        if not r.get('reason', '').strip():
            raise ValueError(f'Nota {r["id"]}: motivo obrigatório')
        fields, tags = original[r['id']]
        if r['old_fields'] != fields or ' '.join(r['old_tags'].split()) != ' '.join(tags.split()):
            raise ValueError(f'Nota {r["id"]}: plano desatualizado (campos ou tags divergentes do backup)')
        new = r.get('new_fields', fields)
        if not isinstance(new, list) or len(new) != len(fields) or not all(isinstance(f, str) for f in new):
            raise ValueError(f'Nota {r["id"]}: quantidade ou tipo dos campos divergente')
        if any('\x1f' in f or '\x00' in f for f in new):
            raise ValueError(f'Nota {r["id"]}: separador interno inválido em campo')
        if cloze_indices(fields) != cloze_indices(new):
            raise ValueError(f'Nota {r["id"]}: não remover, adicionar ou renumerar índices Cloze')
        erros = problemas_nota(notetypes_by_note[r['id']], new, r['new_tags'])
        if erros:
            raise ValueError(f'Nota {r["id"]}: ' + '; '.join(erros))
    for a in plan.get('adicionar', []):
        for n, (f, b, tags) in enumerate(read_tsv(a['tsv']), 1):
            erros = problemas_nota(a['notetype'].casefold().startswith('cloze'), [f, b], tags)
            if erros:
                raise ValueError(f'{a["tsv"]}:{n}: ' + '; '.join(erros))


def _sorted_tags(s):
    return sorted(s.split(), key=str.casefold)


def rebuild(source, plan_path, output, report_path):
    from anki.collection import Collection
    from anki._backend import RustBackend
    source, output, report_path = map(Path, (source, output, report_path))
    if source.resolve() == output.resolve() or output.exists():
        raise ValueError('Use um novo caminho de saída; original e saídas existentes são preservados')
    if report_path.resolve() in (source.resolve(), output.resolve()) or report_path.exists():
        raise ValueError('Relatório deve usar caminho novo e distinto')
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    before = snapshot(source)
    original = {r[0]: (r[6].split('\x1f'), r[5]) for r in before['notes']}
    is_cloze = {r[0]: before['notetypes'].get(r[2], '').casefold().startswith('cloze') for r in before['notes']}
    plan = json.loads(Path(plan_path).read_text(encoding='utf-8'))
    validate_plan(plan, original, is_cloze)
    expected_new = []
    with tempfile.TemporaryDirectory(prefix='anki_rebuild_') as temporary:
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
            edited = retagged = 0
            for r in plan['editar']:
                note = col.get_note(r['id'])
                new = r.get('new_fields', note.fields)
                changed = False
                if new != note.fields:
                    note.fields = new; edited += 1; changed = True
                if _sorted_tags(r['new_tags']) != _sorted_tags(' '.join(note.tags)):
                    note.tags = r['new_tags'].split(); retagged += 1; changed = True
                if changed:
                    col.update_note(note)
            added = {}
            for a in plan.get('adicionar', []):
                model = col.models.by_name(a['notetype'])
                if model is None:
                    raise ValueError(f'Tipo de nota inexistente na coleção: {a["notetype"]}')
                did = col.decks.id_for_name(a['deck'])
                if did is None:
                    raise ValueError(f'Baralho inexistente na coleção: {a["deck"]}')
                rows = read_tsv(a['tsv'])
                for f, b, tags in rows:
                    note = col.new_note(model)
                    if len(note.fields) < 2:
                        raise ValueError(f'Tipo de nota {a["notetype"]} precisa de 2 campos')
                    note.fields[0], note.fields[1] = f, b
                    note.tags = tags.split()
                    col.add_note(note, did)
                    expected_new.append((note.id, [f, b] + note.fields[2:], tags))
                added[a['tsv']] = len(rows)
            col.tags.clear_unused_tags()
            rendered = []
            for cid in col.find_cards(''):
                c = col.get_card(cid)
                q, ans = c.question(), c.answer()
                if not q.strip() or not ans.strip():
                    raise ValueError(f'Cartão vazio: {cid}')
                rendered.append({'card_id': cid, 'note_id': c.nid, 'question': q, 'answer': ans})
            staged = temp / 'rebuilt.colpkg'
            col.export_collection_package(str(staged), include_media=True, legacy=False)
        finally:
            col.close()
        after = snapshot(staged)
        old_cards = {r[0]: r for r in before['cards']}
        new_cards = {r[0]: r for r in after['cards']}
        if any(new_cards.get(cid) != row for cid, row in old_cards.items()):
            raise ValueError('Cartão antigo ausente ou alterado: saída não liberada')
        if after['revlog'] != before['revlog']:
            raise ValueError('Histórico de revisões alterado: saída não liberada')
        after_notes = {r[0]: r for r in after['notes']}
        for r in plan['editar']:
            row, old = after_notes.get(r['id']), next(x for x in before['notes'] if x[0] == r['id'])
            if row is None:
                raise ValueError(f'Nota {r["id"]} ausente na saída')
            if any(old[i] != row[i] for i in (0, 1, 2)):
                raise ValueError(f'Nota {r["id"]}: identidade ou modelo alterados')
            if row[6].split('\x1f') != r.get('new_fields', original[r['id']][0]):
                raise ValueError(f'Nota {r["id"]}: campos exportados não correspondem ao plano')
            if _sorted_tags(row[5]) != _sorted_tags(r['new_tags']):
                raise ValueError(f'Nota {r["id"]}: tags exportadas não correspondem ao plano: {row[5]!r}')
        for nid, fields, tags in expected_new:
            row = after_notes.get(nid)
            if row is None or row[6].split('\x1f') != fields or _sorted_tags(row[5]) != _sorted_tags(tags):
                raise ValueError(f'Nota nova {nid} não corresponde ao TSV')
        if len(after['notes']) != len(before['notes']) + len(expected_new):
            raise ValueError('Número de notas inesperado na saída')
        extra_cards = [r for cid, r in new_cards.items() if cid not in old_cards]
        if any(r[6] != 0 or r[7] != 0 for r in extra_cards):  # type, queue: new cards only
            raise ValueError('Cartão novo com agendamento: saída não liberada')
        if zipfile.ZipFile(staged).testzip() is not None:
            raise ValueError('Falha de integridade ZIP')
        check = temp / 'roundtrip'; check.mkdir()
        check_media = check / 'collection.media'; check_media.mkdir()
        RustBackend().import_collection_package(
            col_path=str(check / 'collection.anki2'), backup_path=str(staged),
            media_folder=str(check_media), media_db=str(check / 'collection.media.db2'))
        media_after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in check_media.iterdir() if p.is_file()}
        if media_after != media_before:
            raise ValueError('Mídia original não preservada integralmente')
        if hashlib.sha256(source.read_bytes()).hexdigest() != source_hash:
            raise ValueError('Hash do original mudou')
        report = {'source_sha256': source_hash, 'notes_before': len(before['notes']),
                  'notes': len(after['notes']), 'cards_before': len(before['cards']),
                  'cards': len(after['cards']), 'revlog': len(after['revlog']),
                  'fields_edited': edited, 'retagged': retagged, 'added': added,
                  'added_notes': len(expected_new), 'media_files_preserved': len(media_before),
                  'old_cards_and_revlog_identical': True, 'tag_rules_passed': True,
                  'official_backend_import_export_tested': True, 'desktop_gui_tested': False,
                  'rendered_cards': rendered}
        output.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with output.open('xb') as f:
            f.write(staged.read_bytes())
        with report_path.open('x', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return {k: v for k, v in report.items() if k != 'rendered_cards'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('source', type=Path)
    p.add_argument('plan', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--report', required=True, type=Path)
    args = p.parse_args()
    print(json.dumps(rebuild(args.source, args.plan, args.output, args.report), ensure_ascii=False))
