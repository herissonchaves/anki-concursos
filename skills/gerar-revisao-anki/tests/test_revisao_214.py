"""Integração real das barreiras 2.14; declarações de fonte FICTÍCIAS."""
import copy
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
import zipfile

import pytest
from recovery_fixture import check, make_review, write_review
from calibration_fixture import write_calibration

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'automacao-anki-python/scripts'))
import exportar_anki as exporter

CE = ('Uma conjunção exige duas proposições verdadeiras para ser verdadeira.\t✅ Certo<br><br>Uma conjunção só é verdadeira se ambas as proposições componentes forem verdadeiras.\tTipo_Revisao_Rapida\n'
      'O número inteiro 2 é ímpar.\t❌ Errado<br><br>O inteiro 2 é par, porque pode ser dividido por 2 sem deixar resto na divisão.\tTipo_Revisao_Rapida\n')
D = CE.replace('Tipo_Revisao_Rapida', 'Tipo_Desafiadora_Cebraspe Estilo_Cebraspe')


def evaluate(items, data):
    return check.validate(items, json.dumps(data,ensure_ascii=False).encode())


@pytest.fixture
def package(tmp_path):
    ce,cl,rep=tmp_path/'anki_certo_errado.tsv',tmp_path/'anki_cloze.tsv',tmp_path/'relatorios'
    rep.mkdir()
    ce.write_text(CE,encoding='utf-8');cl.write_text('',encoding='utf-8')
    for name in exporter.REQUIRED_REPORTS:
        (rep/name).write_text('Fixture sintética, não revisão de produção.',encoding='utf-8')
    write_review(ce,cl,rep)
    return ce,cl,rep,tmp_path/'out.zip'


def do_export(package):
    ce,cl,rep,out=package
    return exporter.export(ce,cl,rep,out,profile='focused',exception_reason='Teste documental sintético')


def test_missing_review_blocks_even_with_nonempty_text_reports(package):
    ce,cl,rep,out=package
    (rep/'revisao_recuperacao.json').unlink()
    before=ce.read_bytes()
    with pytest.raises(ValueError,match='recuperação ausente'): do_export(package)
    assert not out.exists() and ce.read_bytes()==before


@pytest.mark.parametrize('key', ['alvo','solucao','alternativa_concorrente','recuperacao','feedback','fontes','segunda_conferencia','decisao','sha256'])
def test_required_per_card_evidence(package,key):
    ce,cl,rep,out=package
    items={check.FILES[0]:ce.read_bytes(),check.FILES[1]:cl.read_bytes()}
    data=make_review(items)
    del data['cartoes'][0][key]
    assert evaluate(items,data)


@pytest.mark.parametrize('field', range(3))
def test_edited_front_back_or_tags_invalidates_review(package,field):
    ce,cl,rep,out=package
    items={check.FILES[0]:ce.read_bytes(),check.FILES[1]:cl.read_bytes()}
    data=make_review(items)
    lines=items[check.FILES[0]].decode().splitlines()
    row=lines[0].split('\t');row[field]+=' alterado';lines[0]='\t'.join(row)
    items[check.FILES[0]]=('\n'.join(lines)+'\n').encode()
    errors=evaluate(items,data)
    assert any('SHA256 do lote' in x for x in errors)
    assert any('SHA256 divergente' in x for x in errors)


@pytest.mark.parametrize('bad', [None,[],True,{'schema_version':True},{'schema_version':2}])
def test_malformed_root_types(package,bad):
    ce,cl,rep,out=package
    items={check.FILES[0]:ce.read_bytes(),check.FILES[1]:cl.read_bytes()}
    assert evaluate(items,bad)


def test_coverage_duplicate_unknown_and_unapproved(package):
    ce,cl,rep,out=package
    items={check.FILES[0]:ce.read_bytes(),check.FILES[1]:cl.read_bytes()}
    original=make_review(items)
    for action in ('missing','duplicate','unknown','pending','unreviewed','no_identity'):
        data=copy.deepcopy(original)
        if action=='missing': data['cartoes'].pop()
        if action=='duplicate': data['cartoes'].append(data['cartoes'][0])
        if action=='unknown': data['cartoes'][0]['id']='anki_cloze.tsv:99'
        if action=='pending': data['cartoes'][0]['decisao']='PENDENTE'
        if action=='unreviewed': data['cartoes'][0]['segunda_conferencia']=False
        if action=='no_identity': data['revisor']=' '
        assert evaluate(items,data),action


@pytest.mark.parametrize('source', [None,{}, {'url':'file:///private','consulta':'2026-11-08','trecho':'Teste'},
    {'url':'https://user:secret@example.test','consulta':'2026-11-08','trecho':'Teste'},
    {'url':'https://example.test','consulta':'2026-02-30','trecho':'Teste'},
    {'url':'https://[bad','consulta':'2026-11-08','trecho':'Teste'}])
def test_invalid_sources(package,source):
    ce,cl,rep,out=package
    items={check.FILES[0]:ce.read_bytes(),check.FILES[1]:cl.read_bytes()}
    data=make_review(items);data['cartoes'][0]['fontes']=[source]
    assert any('fontes requer' in x for x in evaluate(items,data))


def test_exposed_cloze_blocks_until_specific_exception_or_correction(package):
    ce,cl,rep,out=package
    ce.write_text(D, encoding='utf-8')
    write_calibration(ce, rep)
    cl.write_text('A sublimação é a mudança de sólido para gás chamada de {{c1::sublimação}}.\tEssa mudança leva diretamente do sólido ao gás, sem passagem pelo estado líquido.\tTeste\n',encoding='utf-8')
    target=write_review(ce,cl,rep)
    data=json.loads(target.read_text(encoding='utf-8'))
    items = {check.FILES[0]: ce.read_bytes(), check.FILES[1]: cl.read_bytes()}
    exposed, = (signal['sinal_id'] for signal in check.signals(items)
                if signal['sinal'] == 'RESPOSTA_CLOZE_VISIVEL')
    original=copy.deepcopy(data)
    data['sinais'] = [signal for signal in data['sinais'] if signal['sinal_id'] != exposed]
    target.write_text(json.dumps(data),encoding='utf-8')
    with pytest.raises(ValueError,match='RESPOSTA_CLOZE_VISIVEL'): do_export(package)
    assert not out.exists()
    for decision,reason in [('CORRIGIDO','Declaração não removeu a pista'),('EXCECAO_JUSTIFICADA',' ')]:
        data = copy.deepcopy(original)
        resolution = next(signal for signal in data['sinais'] if signal['sinal_id'] == exposed)
        resolution.update(decisao=decision, motivo=reason)
        target.write_text(json.dumps(data),encoding='utf-8')
        with pytest.raises(ValueError,match='EXCECAO_JUSTIFICADA'): do_export(package)
    # A correção precisa estar nos TSVs e requer nova revisão, sem resolução obsoleta.
    cl.write_text('A passagem direta do sólido para o gás é {{c1::sublimação}}.\tEssa mudança ocorre sem passar pelo estado líquido, ao contrário da fusão.\tTeste\n',encoding='utf-8')
    write_review(ce,cl,rep);do_export(package)
    assert out.exists()


def test_justified_warning_and_stale_or_duplicate_resolution(package):
    ce,cl,rep,out=package
    ce.write_text(CE.replace('Uma conjunção exige','Uma conjunção sempre exige'),encoding='utf-8')
    target=write_review(ce,cl,rep)
    data=json.loads(target.read_text(encoding='utf-8'))
    assert data['sinais']
    do_export(package)  # Exceção FICTÍCIA: teste do mecanismo, não aprovação do texto.
    items={check.FILES[0]:ce.read_bytes(),check.FILES[1]:cl.read_bytes()}
    original=copy.deepcopy(data)
    data['sinais'].append(data['sinais'][0]);assert evaluate(items,data)
    data=copy.deepcopy(original);data['sinais'][0]['sinal_id']='0'*64;assert evaluate(items,data)


def test_zero_cloze_and_cloze_with_challenges_and_d_only(package):
    ce,cl,rep,out=package
    do_export(package)
    ce.write_text('',encoding='utf-8')
    cl.write_text('A passagem direta do sólido ao gás é {{c1::sublimação}}.\tEssa passagem não apresenta a fase líquida intermediária e difere da fusão.\tTeste\n',encoding='utf-8')
    write_review(ce, cl, rep)
    with pytest.raises(ValueError, match='requer IDs de C/E desafiadores'):
        do_export(package)
    ce.write_text(D, encoding='utf-8')
    write_calibration(ce, rep)
    write_review(ce, cl, rep)
    do_export(package)
    cl.write_text('',encoding='utf-8');write_calibration(ce,rep);write_review(ce,cl,rep)
    assert not json.loads((rep/'revisao_recuperacao.json').read_text(encoding='utf-8'))['cartoes']
    do_export(package)


def test_cloze_coverage_requires_every_gap_and_only_current_challenges():
    items = {
        check.FILES[0]: (CE + D).encode(),
        check.FILES[1]: ('Alfa {{c1::beta}} e {{c1::gama}}.\t'
                         'Contexto sintético para os dois alvos.\tTeste\n').encode(),
    }
    report = make_review(items)
    assert evaluate(items, report) == []  # O primeiro D cobre ambas as lacunas na fixture.
    record = report['cartoes'][-1]
    for coverage in (
        None,
        {'1': ['anki_certo_errado.tsv:3']},
        {'1': ['anki_certo_errado.tsv:3'], '2': []},
        {'1': ['anki_certo_errado.tsv:3'], '2': ['anki_certo_errado.tsv:1']},
        {'1': ['anki_certo_errado.tsv:3'], '2': ['anki_certo_errado.tsv:99']},
    ):
        record['desafiadores_por_lacuna'] = coverage
        assert any('anki_cloze.tsv:1' in error for error in evaluate(items, report))


def test_directory_and_final_zip_are_both_checked(package):
    original=exporter.subprocess.run
    with patch.object(exporter.subprocess,'run',wraps=original) as run:
        do_export(package)
    calls=[call.args[0] for call in run.call_args_list if any(str(x).endswith('validar_revisao_pedagogica.py') for x in call.args[0])]
    assert len(calls)==2 and Path(calls[1][-1]).suffix=='.zip'
    ce,cl,rep,out=package
    with zipfile.ZipFile(out) as archive:
        assert archive.read(check.REPORT)==(rep/'revisao_recuperacao.json').read_bytes()
    assert not check.validate(*check.read_package(out))


def test_final_zip_tampering_rejected(package):
    do_export(package)
    ce,cl,rep,out=package
    changed=out.with_name('tampered.zip')
    with zipfile.ZipFile(out) as src,zipfile.ZipFile(changed,'w') as dst:
        for name in src.namelist():
            body=src.read(name)
            if name==check.FILES[0]: body=body.replace('Uma conjunção'.encode(),'Outra afirmação'.encode())
            dst.writestr(name,body)
    assert check.validate(*check.read_package(changed))


def test_cli_lists_hashes_but_does_not_create_approval(package):
    ce,cl,rep,out=package
    target=rep/'revisao_recuperacao.json';target.unlink()
    script=ROOT/'gerar-revisao-anki/scripts/validar_revisao_pedagogica.py'
    result=subprocess.run([sys.executable,'-X','utf8',str(script),str(ce.parent),'--listar-sinais'],capture_output=True,encoding='utf-8')
    assert result.returncode==0 and json.loads(result.stdout)['sha256_lote']
    assert not target.exists()
    result=subprocess.run([sys.executable,'-X','utf8',str(script),str(ce.parent)],capture_output=True,encoding='utf-8')
    assert result.returncode==1


def test_complete_false_declarations_can_still_pass_documents(package):
    # Limite intencional: esse verificador NÃO entende ou valida a matemática.
    ce,cl,rep,out=package
    ce.write_text(CE.replace('duas proposições verdadeiras','uma proposição verdadeira').replace('✅ Certo','✅ Certo'),encoding='utf-8')
    write_review(ce,cl,rep)
    do_export(package)
    assert out.exists()  # Conteúdo falso deve ser reprovado pelo auditor semântico.


def test_missing_checker_cannot_silently_disable_gate(package,monkeypatch):
    original=Path.is_file
    monkeypatch.setattr(Path,'is_file',lambda self: False if self.name=='validar_revisao_pedagogica.py' else original(self))
    with pytest.raises(RuntimeError,match='recuperação indisponível'): do_export(package)
    assert not package[-1].exists()


def test_visual_final_gate_and_failure_does_not_publish(tmp_path):
    import base64
    import exportar_anki_visual as visual
    ce,cl,rep,out=package.__wrapped__(tmp_path)
    ce.write_text(CE.replace('Uma conjunção','<img src="test.png"> Uma conjunção',1),encoding='utf-8')
    write_review(ce,cl,rep)
    media=tmp_path/'media';media.mkdir()
    (media/'test.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aRZkAAAAASUVORK5CYII='))
    vals=['test.png','TEST','https://example.test/img','https://example.test/img.png','Fixture','CC0 fixture','2026-11-08','Teste de transporte','aprovada']
    (rep/'fontes_visuais.tsv').write_text('\t'.join(visual.COLS)+'\n'+'\t'.join(vals)+'\n',encoding='utf-8')
    with patch.object(visual,'check_recovery',wraps=visual.check_recovery) as gate:
        visual.export(ce,cl,rep,media,out,profile='focused',exception_reason='Teste visual')
    assert gate.call_count==1 and gate.call_args.args[1].name=='visual.zip'
    original=out.read_bytes()
    with patch.object(visual,'check_recovery',side_effect=ValueError('Falha final simulada')):
        with pytest.raises(ValueError,match='Falha final simulada'):
            visual.export(ce,cl,rep,media,out,profile='focused',exception_reason='Teste visual')
    assert out.read_bytes()==original
