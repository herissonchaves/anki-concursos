"""Synthetic fixtures only. No private collection or content is shipped."""
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import zipfile
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import anki_utils
from revisar_colpkg import validate_plan, revise

def compression():
    try:
        from compression import zstd
        return zstd.compress
    except ImportError:
        return pytest.importorskip('zstandard').ZstdCompressor().compress

def modern(tmp_path):
    db=tmp_path/'db.sqlite'
    with sqlite3.connect(db) as conn:
        conn.execute('create table notes(id integer primary key, flds text)')
        conn.execute('insert into notes values(1, ?)', ('Questão\x1fResposta',))
    p=tmp_path/'coleção.colpkg'
    with zipfile.ZipFile(p,'w') as z:
        z.writestr('collection.anki21b', compression()(db.read_bytes()))
        z.writestr('collection.anki2',b'not the real database')
    return p

def test_modern_reads_real_database_readonly(tmp_path):
    p=modern(tmp_path); before=p.read_bytes()
    with anki_utils.open_colpkg(p) as (db,member,modern_format):
        assert member=='collection.anki21b' and modern_format
        assert db.execute('select flds from notes').fetchone()[0]=='Questão\x1fResposta'
        with pytest.raises(sqlite3.OperationalError): db.execute('delete from notes')
    assert p.read_bytes()==before

def test_expansion_limit(tmp_path,monkeypatch):
    p=modern(tmp_path)
    monkeypatch.setattr(anki_utils,'MAX_SQLITE_UNCOMPRESSED',1024)
    with pytest.raises(ValueError,match='limite'):
        with anki_utils.open_colpkg(p): pass

def test_bad_modern_never_reads_stub(tmp_path):
    p=modern(tmp_path)
    with zipfile.ZipFile(p,'w') as z:
        z.writestr('collection.anki21b',b'corrupt')
        z.writestr('collection.anki2',b'valid legacy would not be read either')
    with pytest.raises(ValueError,match='stub'):
        with anki_utils.open_colpkg(p): pass

def entry(old,new,decision='REFORMULAR'):
    return {'id':1,'old_fields':old,'new_fields':new,'decision':decision,'reason':'Revisão sintética de teste.'}

def test_plan_blocks_missing_coverage_stale_and_cloze_changes():
    old=['Conceito {{c1::alvo}}.','Explicação']
    with pytest.raises(ValueError,match='todos os IDs'): validate_plan({'notes':[]},{1:old})
    with pytest.raises(ValueError,match='Cloze'): validate_plan({'notes':[entry(old,['Conceito {{c2::alvo}}.','Explicação'])]},{1:old})
    with pytest.raises(ValueError,match='desatualizado'): validate_plan({'notes':[entry(['outro',''],old)]},{1:old})
    with pytest.raises(ValueError,match='idêntica'): validate_plan({'notes':[entry(old,[old[0],'Novo'],'APROVAR')]},{1:old})
    validate_plan({'notes':[entry(old,[old[0],'Novo'])]},{1:old})

def test_official_roundtrip_keeps_scheduling_and_media(tmp_path):
    pytest.importorskip('anki')
    from anki.collection import Collection
    c=Collection(str(tmp_path/'collection.anki2'))
    model=next(m for m in c.models.all() if m['type']==0 and len(m['flds'])==2 and len(m['tmpls'])==1)
    note=c.new_note(model); note.fields=['Original','Verso']; c.add_note(note,1)
    cid=c.find_cards('')[0]
    c.db.execute('update cards set reps=17,lapses=3,ivl=22,due=123,type=2,queue=2 where id=?',cid)
    c.db.execute('insert into revlog values(?,?,?,?,?,?,?,?,?)',10000,cid,-1,3,22,10,2500,5000,1)
    (tmp_path/'collection.media'/'fixture.txt').write_bytes(b'synthetic media bytes')
    source=tmp_path/'source.colpkg'; c.export_collection_package(str(source),True,False); c.close()
    before=hashlib.sha256(source.read_bytes()).hexdigest()
    plan=tmp_path/'plan.json'
    r=entry(['Original','Verso'],['Revisado','Explicação melhor']); r['id']=note.id
    plan.write_text(json.dumps({'notes':[r]}),encoding='utf-8')
    result=revise(source,plan,tmp_path/'out.colpkg',tmp_path/'report.json')
    assert result['cards_and_revlog_identical'] and result['revlog']==1
    assert result['media_files_preserved']==1 and result['changed']==1
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
    with pytest.raises(ValueError,match='existentes'): revise(source,plan,source,tmp_path/'r.json')
