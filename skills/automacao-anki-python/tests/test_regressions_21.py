"""Real exporter regressions using synthetic content, never user collections."""
from pathlib import Path
import importlib.util
import json
import sqlite3
import sys
import zipfile
import pytest
import exportar_anki
import exportar_anki_visual

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
from exportar_anki import export, generate_apkg, deck_id, tsv_rows
from exportar_anki_visual import export as export_visual, COLS
from anki_utils import open_colpkg
from calibration_fixture import write_calibration
from recovery_fixture import write_review
VPATH=SCRIPTS.parents[1]/'gerar-revisao-anki'/'scripts'
def module(name):
    spec=importlib.util.spec_from_file_location(name,VPATH/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
v=module('validar_anki');g=module('validar_gabaritos_rapidos')

def sample(tmp_path,front='A unidade SI de força é o newton.'):
    ce=tmp_path/'ce.tsv';cl=tmp_path/'cl.tsv';rep=tmp_path/'reports';rep.mkdir()
    ce.write_text(front+'\t✅ Certo<br><br>Força é medida em newtons no SI. 💡 Memorize: resumo sintético.\tTeste::Sintetico::Topico Rapida\n'
        +'Um carro mantém sua massa e dobra a velocidade. Sua energia cinética também dobra.\t❌ Errado<br><br>A energia cinética depende do quadrado da velocidade; por isso quadruplica. 💡 Memorize: resumo sintético.\tTeste::Sintetico::Topico Desafiadora\n',encoding='utf-8')
    cl.write_text('A unidade SI de energia é o {{c1::joule}}.\tEnergia e trabalho usam a mesma unidade SI. 💡 Memorize: resumo sintético.\tTeste::Sintetico::Topico Cloze\n',encoding='utf-8')
    for n in ['selecao_e_fontes','economia_de_revisao','auditoria_pedagogica']:
        (rep/(n+'.txt')).write_text('Fixture sintética de teste, não auditoria de produção.',encoding='utf-8')
    lines=ce.read_text(encoding='utf-8').splitlines()
    lines.insert(1,'O newton é unidade SI de massa.\t❌ Errado<br><br>Quilograma mede massa; newton mede força. 💡 Memorize: resumo sintético.\tTeste::Sintetico::Topico Rapida')
    lines.append('Na mecânica clássica, um corpo de massa constante dobra a velocidade e quadruplica a energia cinética.\t✅ Certo<br><br>O quadrado da velocidade fica quatro vezes maior. 💡 Memorize: resumo sintético.\tTeste::Sintetico::Topico Desafiadora')
    ce.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    write_calibration(ce,rep)
    write_review(ce,cl,rep)
    return ce,cl,rep

def test_no_mnemonic_and_valid_ratio(tmp_path):
    ce,cl,rep=sample(tmp_path)
    result=export(ce,cl,rep,tmp_path/'out.zip')
    assert result['validador_executado']
    errors=[];v.validate_type_distribution(ce.read_bytes(),errors,True)
    assert not errors
    v.validate_type_distribution(ce.read_bytes(),errors,True,True)
    assert not errors

def test_balance_is_opt_in():
    row='Proposição.\t✅ Certo<br><br>Fundamento. 💡 Memorize: resumo sintético.\tTeste::Sintetico::Topico Rapida\n'
    assert not g.contar_rapidos((row*2).encode())[1]
    assert g.contar_rapidos((row*2).encode(),True)[1]

def test_text_export_rejects_missing_type(tmp_path):
    ce,cl,rep=sample(tmp_path)
    ce.write_text(ce.read_text(encoding='utf-8').replace('Topico Rapida','Topico'),encoding='utf-8')
    with pytest.raises(ValueError,match='sem tag'):
        export(ce,cl,rep,tmp_path/'out.zip')

def test_modern_stub_is_not_a_collection(tmp_path):
    p=tmp_path/'modern.colpkg'
    with zipfile.ZipFile(p,'w') as z:
        z.writestr('collection.anki21b',b'unsupported compressed data')
        z.writestr('collection.anki2',b'compatibility stub')
    with pytest.raises(ValueError,match='stub'):
        with open_colpkg(p):pass

def test_leading_quote_preserved(tmp_path):
    ce,cl,rep=sample(tmp_path,'"Força" é medida em newtons.')
    assert list(tsv_rows(ce))[0][0]=='"Força" é medida em newtons.'

def test_deck_identity_and_apkg_counts(tmp_path):
    pytest.importorskip('genanki')
    ce,cl,rep=sample(tmp_path)
    cl.write_text('A relação usa {{c1::massa}} e {{c2::aceleração}}.\tExemplo estrutural sintético.\tTeste::Sintetico::Topico Cloze\n',encoding='utf-8')
    assert deck_id('Anki-Concursos')==1987052180
    assert deck_id('Fisica')==deck_id('Fisica')!=deck_id('Portugues')
    package=tmp_path/'out.apkg'
    generate_apkg(ce,cl,package,'Fisica')
    with zipfile.ZipFile(package) as z:
        db=tmp_path/'read.sqlite';db.write_bytes(z.read('collection.anki2'))
    with sqlite3.connect(db) as conn:
        assert conn.execute('select count(*) from notes').fetchone()[0]==5
        assert conn.execute('select count(*) from cards').fetchone()[0]==6
        assert conn.execute('select distinct did from cards').fetchall()==[(deck_id('Fisica'),)]

def visual_sample(tmp_path):
    import base64,csv
    ce,cl,rep=sample(tmp_path,'<img src="fixture.png"> A figura serve apenas a teste estrutural.')
    media=tmp_path/'media';media.mkdir()
    blob=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Zl1sAAAAASUVORK5CYII=')
    (media/'fixture.png').write_bytes(blob)
    # Synthetic provenance solely for pipeline testing, never a production license assertion.
    with (rep/'fontes_visuais.tsv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(COLS)
        w.writerow(['fixture.png','TEST-1','https://example.org/test','https://example.org/test.png','fixture','teste-sintetico','2026-11-01','teste apenas','aprovada'])
    return ce, cl, rep, media, blob


@pytest.mark.parametrize('visual', [False, True], ids=['textual', 'visual'])
def test_invalid_apkg_path_does_not_publish_zip(tmp_path, visual):
    if visual:
        ce, cl, rep, media, _ = visual_sample(tmp_path)
        exporter, inputs = export_visual, (ce, cl, rep, media)
    else:
        exporter, inputs = export, sample(tmp_path)
    out = tmp_path / 'out.zip'
    with pytest.raises(ValueError, match=r'\.apkg'):
        exporter(*inputs, out, tmp_path / 'wrong.ext')
    assert not out.exists()


@pytest.mark.parametrize('visual', [False, True], ids=['textual', 'visual'])
def test_apkg_failure_preserves_existing_packages(tmp_path, monkeypatch, visual):
    def fail_apkg(ce, cloze, destination, *args):
        destination.write_bytes(b'partial APKG')
        raise RuntimeError('Falha simulada na geração do APKG')

    if visual:
        ce, cl, rep, media, _ = visual_sample(tmp_path)
        exporter, inputs = export_visual, (ce, cl, rep, media)
        monkeypatch.setattr(exportar_anki_visual, 'make_apkg', fail_apkg)
    else:
        exporter, inputs = export, sample(tmp_path)
        monkeypatch.setattr(exportar_anki, 'generate_apkg', fail_apkg)
    out = tmp_path / 'out.zip'
    apkg = tmp_path / 'out.apkg'
    out.write_bytes(b'previous ZIP')
    apkg.write_bytes(b'previous APKG')
    with pytest.raises(RuntimeError, match='Falha simulada'):
        exporter(*inputs, out, apkg)
    assert out.read_bytes() == b'previous ZIP'
    assert apkg.read_bytes() == b'previous APKG'


def test_visual_manifest_and_apkg_media_survive(tmp_path):
    pytest.importorskip('genanki')
    ce, cl, rep, media, blob = visual_sample(tmp_path)
    out=tmp_path/'visual.zip';apkg=tmp_path/'visual.apkg'
    export_visual(ce,cl,rep,media,out,apkg,'Visual teste')
    with zipfile.ZipFile(out) as z:
        assert z.read('midia/fixture.png')==blob
        assert 'relatorios/fontes_visuais.tsv' in z.namelist()
        assert 'Básico'.encode() in z.read('LEIA-ME.txt')
    with zipfile.ZipFile(apkg) as z:
        mapping=json.loads(z.read('media'))
        key=next(k for k,val in mapping.items() if val=='fixture.png')
        assert z.read(key)==blob

def test_actual_cli_counts_cloze_towards_user_cap(tmp_path):
    import subprocess
    ce,cl,rep=sample(tmp_path)
    out=tmp_path/'out.zip';export(ce,cl,rep,out)
    result=subprocess.run([sys.executable,'-X','utf8',str(VPATH/'validar_anki.py'),str(out),'--new','--max-cards','1'],capture_output=True,encoding='utf-8')
    assert result.returncode==1
    assert 'Teto do usu' in result.stdout
