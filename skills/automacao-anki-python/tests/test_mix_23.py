"""Real exporter gates: format requirements and uncapped quick cards."""
import pytest
from test_regressions_21 import sample, export, export_visual
from recovery_fixture import write_review

@pytest.mark.parametrize('missing', ['quick','hard'])
def test_missing_format_rejected(tmp_path, missing):
    ce,cl,rep=sample(tmp_path)
    if missing=='cloze': cl.write_text('',encoding='utf-8')
    else:
        tag='Tipo_Revisao_Rapida' if missing=='quick' else 'Tipo_Desafiadora_Cebraspe'
        ce.write_text('\n'.join(x for x in ce.read_text(encoding='utf-8').splitlines() if tag not in x)+'\n',encoding='utf-8')
    with pytest.raises(ValueError,match='rápidos e desafiadores'):
        export(ce,cl,rep,tmp_path/'out.zip')

def test_more_quick_allowed(tmp_path):
    ce,cl,rep=sample(tmp_path)
    with ce.open('a',encoding='utf-8') as f:
        f.write('A massa é medida em metros no SI.\t❌ Errado<br><br>Quilograma é a unidade SI de massa.\tTipo_Revisao_Rapida\n')
        f.write('A unidade SI de tempo é o segundo.\t✅ Certo<br><br>Segundo é a unidade SI de tempo.\tTipo_Revisao_Rapida\n')
    write_review(ce,cl,rep)
    export(ce,cl,rep,tmp_path/'out.zip')
    assert (tmp_path/'out.zip').is_file()

def test_visual_export_allows_more_quick(tmp_path):
    from test_regressions_21 import test_visual_manifest_and_apkg_media_survive
    test_visual_manifest_and_apkg_media_survive(tmp_path)
    ce,cl,rep=tmp_path/'ce.tsv',tmp_path/'cl.tsv',tmp_path/'reports'
    with ce.open('a',encoding='utf-8') as f:
        f.write('A massa é medida em metros no SI.\t❌ Errado<br><br>Quilograma é a unidade SI de massa.\tTipo_Revisao_Rapida\n')
        f.write('A unidade SI de tempo é o segundo.\t✅ Certo<br><br>Segundo é a unidade SI de tempo.\tTipo_Revisao_Rapida\n')
    media=tmp_path/'media'
    write_review(ce,cl,rep)
    export_visual(ce,cl,rep,media,tmp_path/'out.zip')
    assert (tmp_path/'out.zip').is_file()


def test_no_cloze_is_valid(tmp_path):
    ce,cl,rep=sample(tmp_path)
    cl.write_text("",encoding="utf-8")
    write_review(ce,cl,rep)
    export(ce,cl,rep,tmp_path/"no-cloze.zip")
    assert (tmp_path/"no-cloze.zip").is_file()
