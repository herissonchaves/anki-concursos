"""Regras de tags e de Cloze mnemônico da 2.33 (references/tags.md). Dados sintéticos."""
import importlib.util
from pathlib import Path

import pytest

import regras_tags as t

_spec = importlib.util.spec_from_file_location('validar_233', Path(__file__).resolve().parents[1] / 'scripts/validar_anki.py')
v = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v)

H = 'Direito_Administrativo::Atos_Administrativos::Delegacao'


@pytest.mark.parametrize('tags, tipo', [
    (f'{H} Rapida', t.RAPIDA),
    (f'{H} Rapida Missao_07 Pagina_12 Pagina_13', t.RAPIDA),
    (f'{H} Desafiadora cebraspe-2021-prf-080 Missao_07 Pagina_12', t.DESAFIADORA),
    (f'{H} Cloze', t.CLOZE),
])
def test_tags_validas(tags, tipo):
    assert t.problemas_tags(tags, tipo) == []


@pytest.mark.parametrize('tags, tipo, trecho', [
    (f'PRF {H} Rapida', t.RAPIDA, 'proibida'),
    (f'{H} Rapida Estilo_Cebraspe', t.RAPIDA, 'proibida'),
    (f'{H} Rapida Revisao_PDF', t.RAPIDA, 'proibida'),
    (f'{H} Cloze Mnemonico', t.CLOZE, 'proibida'),
    (f'{H} Tipo_Revisao_Rapida', t.RAPIDA, 'tipo'),
    (f'{H} Rapida Desafiadora', t.RAPIDA, 'tipo'),
    (f'{H}', t.CLOZE, 'tipo'),
    ('Direito_Administrativo Rapida', t.RAPIDA, 'Disciplina::Assunto::Topico'),
    ('Direito_Administrativo::Atos Rapida', t.RAPIDA, 'três níveis'),
    (f'{H} Rapida Pagina_12', t.RAPIDA, 'nome curto do PDF'),
    (f'{H} Rapida Missao_07', t.RAPIDA, 'sem categoria'),
    (f'{H} Rapida cebraspe-2021-prf-080', t.RAPIDA, 'só em Desafiadora'),
    (f'{H} Desafiadora Missao_07 Pagina_12', t.DESAFIADORA, 'questão real'),  # 2.37
])
def test_tags_reprovadas(tags, tipo, trecho):
    assert any(trecho in e for e in t.problemas_tags(tags, tipo))


def test_tipos_antigos_seguem_lidos_em_lotes_antigos():
    linhas = ('Frente A.\t✅ Certo<br><br>X.\tFisica Tipo_Revisao_Rapida\n'
              'Frente B.\t❌ Errado<br><br>Y.\tFisica Tipo_Desafiadora_Cebraspe Estilo_Cebraspe\n').encode()
    erros = []
    assert v.validate_type_distribution(linhas, erros) == {'rapidos': 1, 'desafiadores': 1, 'sem_tipo': 0}
    assert erros == []


def test_validador_new_reprova_tag_de_concurso():
    itens = {'anki_certo_errado.tsv': f'Frente.\t✅ Certo<br><br>X.\tPRF {H} Rapida\n'.encode(), 'anki_cloze.tsv': b''}
    erros = []
    v.validate_new_tags(itens, erros)
    assert any('PRF' in e for e in erros)


ORIGEM = '<div>📚 Origem do mnemônico</div>Encontrado em <a href="https://example.test/img">Imagem X</a>.'
CENORE = ('<b>Mnemônico CE-NO-RE:</b><br>Pela Lei 9.784/1999 (art. 13), não podem ser delegados:<br>'
          'a matéria de C{{c1::ompetência}} E{{c1::xclusiva}},<br>a edição de atos NO{{c1::rmativos}}<br>'
          'e a decisão de RE{{c1::cursos administrativos}}.')


def test_mnemonico_cenore_aprovado_com_link():
    assert t.sigla_mnemonico(CENORE) == 'CE-NO-RE'
    assert t.problemas_mnemonico(CENORE, ORIGEM) == []


def test_caso_reprovado_pelo_usuario():
    ruim = ('Dica autoral CE-NO-RE: pela Lei 9.784/1999 (art. 13), não podem ser delegados {{c1::a matéria de '
            'Competência Exclusiva, a edição de atos NOrmativos e a decisão de REcursos administrativos}}.')
    assert t.mnemonico_fora_do_formato(ruim)
    erros = []
    v.validate_new_cloze(f'{ruim}\tAutoral.\t{H} Cloze\n'.encode(), erros)
    assert any('mnemônico fora do formato' in e for e in erros)


def test_origem_no_verso_obrigatoria():
    assert any('Origem do mnemônico' in e for e in t.problemas_mnemonico(CENORE, 'Explica os termos.'))
    assert any('Autoral' in e for e in t.problemas_mnemonico(CENORE, '📚 Origem do mnemônico: sei lá.'))
