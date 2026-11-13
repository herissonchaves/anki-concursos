"""Offline regression tests; a fake validator is used ONLY in exporter unit tests."""
import csv
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import zipfile

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0,str(SCRIPT))
from anki_utils import normalized,open_colpkg
from analisar_colpkg import analyze
from detectar_duplicatas import find_duplicates,fronts_tsv
from extrair_pdf import extract
from exportar_anki import export,tsv_rows


def make_backup(tmp_path, *, with_log=False):
    db=tmp_path/'bank.sqlite'
    with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE notes (id INTEGER, flds TEXT)')
        conn.execute('CREATE TABLE cards (id INTEGER, lapses INTEGER, queue INTEGER)')
        conn.executemany('INSERT INTO notes VALUES (?,?)',[(111,'Teoria da atividade\x1fVerso'),(222,'Teoria da atividade\x1fOutra explicação'),(333,'Outro assunto\x1fVerso')])
        conn.executemany('INSERT INTO cards VALUES (?,?,?)',[(1001,3,2),(1002,0,-1)])
        if with_log:
            conn.execute('CREATE TABLE revlog (id INTEGER)')
            conn.execute('INSERT INTO revlog VALUES (1)')
    out=tmp_path/'backup.colpkg'
    with zipfile.ZipFile(out,'w') as z:z.write(db,'collection.anki2')
    return out


def test_readonly_backup_does_not_change_source(tmp_path):
    from hashlib import sha256
    b=make_backup(tmp_path)
    before=sha256(b.read_bytes()).hexdigest()
    report=analyze(b)
    assert report['estatisticas']['notes']==3
    assert report['estatisticas']['cards']==2
    assert report['estatisticas']['cartoes_com_lapsos']==1
    assert report['estatisticas']['revlog'] is None
    assert report['duplicatas_exatas_candidatas'][0]['note_ids']==['111','222']
    assert sha256(b.read_bytes()).hexdigest()==before


def test_malformed_colpkg_rejected(tmp_path):
    path=tmp_path/'no.colpkg'
    with zipfile.ZipFile(path,'w') as z:z.writestr('media','{}')
    with pytest.raises(ValueError,match='SQLite'):analyze(path)


def test_duplicate_does_not_remove(tmp_path):
    new=[('L1','É aplicável a teoria da atividade'),('L2','É aplicável a teoria da atividade'),('L3','Não é aplicável a teoria da atividade')]
    result=find_duplicates(new,threshold=88)
    assert any(p['novo']=='L2' and p['comparado_com']=='L1' for p in result)
    assert len(new)==3


def test_compare_with_backup(tmp_path):
    backup=make_backup(tmp_path)
    with open_colpkg(backup) as (db,_,__):
        from anki_utils import note_fronts
        old=note_fronts(db)
    result=find_duplicates([('L3','Teoria da atividade')],old,90)
    assert any(r['tipo']=='backup' for r in result)


def test_tsv_three_fields_and_header(tmp_path):
    f=tmp_path/'a.tsv'
    f.write_text('Frente\tVerso\tTags\nOlá\t✅ Certo\tDir_Penal\n',encoding='utf-8')
    assert list(fronts_tsv(f))==[('L2','Olá')]
    assert list(tsv_rows(f))==[['Olá','✅ Certo','Dir_Penal']]
    f.write_text('incompleto\tum campo\n',encoding='utf-8')
    with pytest.raises(ValueError):list(fronts_tsv(f))


def test_pdf_text_and_scan_warning(tmp_path):
    fitz=pytest.importorskip('fitz')
    pdf=fitz.open()
    p=pdf.new_page();p.insert_text((20,30),'Direito Penal - Principio da legalidade e aplicacao da lei')
    pdf.new_page()
    src=tmp_path/'exemplo.pdf';pdf.save(src);pdf.close()
    result=extract(src,minimum_chars=20)
    assert result['total_paginas']==2
    assert result['paginas_com_alerta']==[2]
    assert not result['paginas'][0]['revisao_visual_obrigatoria']


def test_export_blocks_no_reports_or_validator(tmp_path, monkeypatch):
    ce=tmp_path/'ce.tsv';cl=tmp_path/'cl.tsv'
    ce.write_text('Frente\tVerso\tTags\n',encoding='utf-8')
    cl.write_text('Texto\tExtra\tTags\n',encoding='utf-8')
    rep=tmp_path/'relatorios';rep.mkdir()
    with pytest.raises(ValueError,match='obrigatório'):export(ce,cl,rep,tmp_path/'export.zip')
    for name in ['selecao_e_fontes.txt','economia_de_revisao.txt','auditoria_pedagogica.txt']:
        (rep/name).write_text('Relatório exemplar de teste (não produção).',encoding='utf-8')
    import exportar_anki
    monkeypatch.setattr(exportar_anki, '__file__', str(tmp_path/'absent'/'scripts'/'exportar_anki.py'))
    with pytest.raises(RuntimeError,match='indisponível'):export(ce,cl,rep,tmp_path/'export.zip')


def test_export_uses_existing_validator_twice_with_test_double(tmp_path,monkeypatch):
    # Unit test of subprocess orchestration, NOT real pedagogical/technical validation.
    # Build a temporary script tree equivalent to the installed plugin's layout.
    fake_scripts=tmp_path/'skills'/'automacao-anki-python'/'scripts'
    fake_scripts.mkdir(parents=True)
    shutil=__import__('shutil')
    src=SCRIPT/'exportar_anki.py'
    shutil.copyfile(src,fake_scripts/'exportar_anki.py')
    valid=tmp_path/'skills'/'gerar-revisao-anki'/'scripts'/'validar_anki.py'
    valid.parent.mkdir(parents=True)
    valid.write_text('import pathlib,sys\np=pathlib.Path(sys.argv[1])\nassert p.exists()\nprint("validação SIMULADA")\n',encoding='utf-8')
    shutil.copyfile(valid,valid.with_name('validar_revisao_pedagogica.py'))  # Test double, not real approval.
    ce=tmp_path/'ce.tsv';cl=tmp_path/'cl.tsv'
    ce.write_text('Frente\tVerso\tTags\nA conduta se enquadra na lei.\t✅ Certo<br><br>Condição atendida.<br><br>💡 Memorize: a lei é aplicada.\tDireito\n',encoding='utf-8')
    cl.write_text('Texto\tExtra\tTags\n',encoding='utf-8')
    rep=tmp_path/'relatorios';rep.mkdir()
    for name in ['selecao_e_fontes.txt','economia_de_revisao.txt','auditoria_pedagogica.txt']:
        (rep/name).write_text('EXEMPLO DE TESTE, NÃO USAR EM PRODUÇÃO.',encoding='utf-8')
    result=subprocess.run([sys.executable,str(fake_scripts/'exportar_anki.py'),'--ce',str(ce),'--cloze',str(cl),'--relatorios',str(rep),'-o',str(tmp_path/'out.zip')],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    with zipfile.ZipFile(tmp_path/'out.zip') as z:
        assert z.testzip() is None
        assert 'anki_certo_errado.tsv' in z.namelist()
        assert 'relatorios/auditoria_pedagogica.txt' in z.namelist()


def test_apkg_without_genanki_reports_error(tmp_path,monkeypatch):
    import builtins
    original_import=builtins.__import__
    def without_genanki(name,*args,**kwargs):
        if name=='genanki': raise ImportError('Ausência simulada para teste')
        return original_import(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',without_genanki)
    from exportar_anki import generate_apkg
    with pytest.raises(RuntimeError,match='genanki'):generate_apkg(tmp_path/'a.tsv',tmp_path/'b.tsv',tmp_path/'deck.apkg','Exemplo')
