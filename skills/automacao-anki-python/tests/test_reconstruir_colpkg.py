"""Reconstrução de coleção a partir de backup (2.34). Só dados sintéticos."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from reconstruir_colpkg import adicionar_de_lotes, rebuild, validate_plan, problemas_nota  # noqa: E402

TAGS_R = 'Direito_Penal::Teoria_Geral_do_Crime::Conceito Rapida'
MN_FRENTE = ('<b>Mnemônico FOCO:</b><br>Na convalidação, são sanáveis os vícios de<br>'
             'FO{{c1::rma}}<br>e CO{{c1::mpetência}}.')
MN_EXTRA = 'Explicação.<br>📚 Origem do mnemônico: Autoral: criado para este card.<br>💡 Memorize: FOCO.'


def entry(nid, fields, tags, new_tags, new_fields=None):
    r = {'id': nid, 'old_fields': fields, 'old_tags': tags, 'new_tags': new_tags, 'reason': 'retag 2.33'}
    if new_fields is not None:
        r['new_fields'] = new_fields
    return r


def test_regras_de_nota():
    assert problemas_nota(False, ['a', 'b'], TAGS_R) == []
    assert problemas_nota(False, ['a', 'b'], 'PRF Tipo_Revisao_Rapida')
    assert problemas_nota(True, ['Dica autoral X: {{c1::abc}}', ''], 'A::B::C Cloze')
    assert problemas_nota(True, [MN_FRENTE, MN_EXTRA], 'Direito_Administrativo::Atos::Convalidacao Cloze') == []


def test_plano_exige_todas_as_notas_e_bloqueia_cloze():
    original = {1: (['a', 'b'], 'PRF'), 2: (['{{c1::x}}', ''], '')}
    clz = {1: False, 2: True}
    with pytest.raises(ValueError, match='exclusão'):
        validate_plan({'editar': [entry(1, ['a', 'b'], 'PRF', TAGS_R)]}, original, clz)
    plano = {'editar': [entry(1, ['a', 'b'], 'PRF', TAGS_R),
                        entry(2, ['{{c1::x}}', ''], '', 'A::B::C Cloze', ['{{c2::x}}', ''])]}
    with pytest.raises(ValueError, match='Cloze'):
        validate_plan(plano, original, clz)
    plano['editar'][1]['old_tags'] = 'velha'
    with pytest.raises(ValueError, match='desatualizado'):
        validate_plan(plano, original, clz)


def test_reconstrucao_preserva_historico_e_adiciona(tmp_path):
    pytest.importorskip('anki')
    from anki.collection import Collection
    c = Collection(str(tmp_path / 'collection.anki2'))
    basic = next(m for m in c.models.all() if m['type'] == 0 and len(m['flds']) == 2 and len(m['tmpls']) == 1)
    cloze = next(m for m in c.models.all() if m['type'] == 1)
    did = c.decks.id('Direito Penal')
    n1 = c.new_note(basic); n1.fields = ['Frente', 'Verso']; n1.tags = ['PRF', 'Tipo_Revisao_Rapida']
    c.add_note(n1, did)
    n2 = c.new_note(cloze); n2.fields = ['Dica autoral FOCO: vícios de {{c1::FOrma e COmpetência}}', 'x']
    c.add_note(n2, did)
    cid = c.find_cards(f'nid:{n1.id}')[0]
    c.db.execute('update cards set reps=17,lapses=3,ivl=22,due=123,type=2,queue=2 where id=?', cid)
    c.db.execute('insert into revlog values(?,?,?,?,?,?,?,?,?)', 10000, cid, -1, 3, 22, 10, 2500, 5000, 1)
    (tmp_path / 'collection.media' / 'fixture.txt').write_bytes(b'synthetic media bytes')
    source = tmp_path / 'source.colpkg'
    c.export_collection_package(str(source), True, False)
    c.close()
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    tsv = tmp_path / 'anki_certo_errado.tsv'
    tsv.write_text('Nova frente\tNovo verso\tDireito_Penal::Teoria_Geral_do_Crime::Dolo '
                   'Missao_06_DPE040002 Pagina_05 Rapida\n', encoding='utf-8')
    plano = {'editar': [entry(n1.id, ['Frente', 'Verso'], 'PRF Tipo_Revisao_Rapida', TAGS_R),
                        entry(n2.id, list(n2.fields), '',
                              'Direito_Administrativo::Atos::Convalidacao Cloze', [MN_FRENTE, MN_EXTRA])],
             'adicionar': [{'tsv': str(tsv), 'deck': 'Direito Penal', 'notetype': basic['name']}]}
    plan = tmp_path / 'plan.json'
    plan.write_text(json.dumps(plano, ensure_ascii=False), encoding='utf-8')
    out = tmp_path / 'out.colpkg'
    r = rebuild(source, plan, out, tmp_path / 'report.json')
    assert r['old_cards_and_revlog_identical'] and r['revlog'] == 1
    assert r['notes'] == 3 and r['added_notes'] == 1 and r['retagged'] == 2 and r['fields_edited'] == 1
    assert r['media_files_preserved'] == 1
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    with pytest.raises(ValueError, match='existentes'):
        rebuild(source, plan, out, tmp_path / 'r2.json')


def test_adicionar_de_lotes_le_baralho_do_historico_2_36(tmp_path):
    hist = tmp_path / 'historico_lotes.tsv'
    hist.write_text('data\tlote\tbaralho\trapidos\tdesafiadores\tcloze\tids_banco\n'
                    '2026-11-23\tPRF_A\tDireito Penal\t1\t0\t0\t\n', encoding='utf-8')
    for nome, ce, cz in (('PRF_A', 'f\tv\tt\n', ''), ('PRF_Vazio', '', '')):
        (tmp_path / nome / 'lote').mkdir(parents=True)
        (tmp_path / nome / 'lote' / 'anki_certo_errado.tsv').write_text(ce, encoding='utf-8')
        (tmp_path / nome / 'lote' / 'anki_cloze.tsv').write_text(cz, encoding='utf-8')
    saida = adicionar_de_lotes([tmp_path / 'PRF_A', tmp_path / 'PRF_Vazio'], hist)
    assert [(x['deck'], x['notetype']) for x in saida] == [('Direito Penal', 'Basic')]
    (tmp_path / 'PRF_B' / 'lote').mkdir(parents=True)
    (tmp_path / 'PRF_B' / 'lote' / 'anki_certo_errado.tsv').write_text('f\tv\tt\n', encoding='utf-8')
    with pytest.raises(ValueError, match='histórico'):
        adicionar_de_lotes([tmp_path / 'PRF_B'], hist)


@pytest.mark.parametrize('script', ['analisar_colpkg.py', 'detectar_duplicatas.py', 'revisar_colpkg.py',
                                    'reconstruir_colpkg.py', 'colecao_anki.py', 'finalizar_lote.py'])
def test_scripts_rodam_com_python_isolado_2_36(script):
    """Com -I o Python não põe a pasta do script no sys.path; o script tem de fazê-lo."""
    import subprocess
    pasta = Path(__file__).resolve().parents[1] / 'scripts'
    r = subprocess.run([sys.executable, '-I', str(pasta / script), '-h'], capture_output=True, text=True,
                       cwd=Path(__file__).resolve().parents[3])
    assert r.returncode == 0, r.stderr[-300:]
