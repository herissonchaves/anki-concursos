"""Regressões 2.15: HTML visual compatível com o Anki e Cloze de omissão única."""
import importlib.util
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'


def load(name):
    spec = importlib.util.spec_from_file_location(name + '_215', SCRIPTS / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


h = load('html_anki')
v = load('validar_anki')


def test_verso_ce_keeps_exact_prefix_and_ends_with_memorize():
    verso = h.verso_ce('E', [h.regra('POP3 recebe.'), h.erro('A frase diz que envia.')], 'POP3 recebe; SMTP envia.')
    assert verso.startswith('❌ Errado<br><br>')
    assert verso.rfind('💡 Memorize') > verso.rfind('Onde está o erro')
    assert h.problemas_html(verso) == []
    assert '\t' not in verso and '\n' not in verso


def test_verso_requires_memorize_and_valid_answer():
    with pytest.raises(ValueError):
        h.verso_ce('C', [h.regra('x')], '  ')
    with pytest.raises(ValueError):
        h.verso_ce('Certo', [h.regra('x')], 'resumo')


def test_components_reject_line_breaks_and_bad_tables():
    with pytest.raises(ValueError):
        h.regra('linha 1\nlinha 2')
    with pytest.raises(ValueError):
        h.tabela(['A', 'B'], [['só uma']])
    with pytest.raises(ValueError):
        h.fluxo(['única'])


def test_scheme_components_are_balanced_and_safe():
    texto = h.extra_cloze([h.regra('Termo.'), h.esquema(h.tabela(['POP3', 'IMAP'], [['110', '143']]) + h.fluxo(['MUA', 'MSA', 'MTA']))], 'Resumo.')
    assert h.problemas_html(texto) == []
    assert 'rgba(' in texto and 'color:#' in texto  # fundo translúcido; cor só em títulos/bordas


@pytest.mark.parametrize('ruim', [
    '<script>alert(1)</script>', '<img src="x.png" onerror="x()">', '<a href="javascript:x()">a</a>',
    '<img src="https://ex.org/a.png">', '<style>b{}</style>', '<div style="position:fixed">x</div>',
    '<div>aberta', 'linha\tcom tab',
])
def test_problemas_html_flags_unsafe_or_broken_markup(ruim):
    assert h.problemas_html(ruim)


def test_local_media_is_allowed():
    assert h.problemas_html('<img src="midia/esquema.png">') == []


def test_new_cloze_single_omission_and_mnemonic_tag():
    def errors(text, tags):
        found = []
        v.validate_new_cloze(f'{text}\tExtra específico.\t{tags}\n'.encode(), found)
        return found
    assert errors('POP3 usa a porta {{c1::110}}.', 'Portas') == []
    assert errors('POP3 → {{c1::110}}; IMAP → {{c1::143}}.', 'Portas')
    assert errors('S {{c1::ua}} M {{c1::ensagem}}', 'Mnemonico') == []


def test_new_html_check_reports_line_and_field():
    items = {'anki_certo_errado.tsv': 'Frente.\t✅ Certo<br><br><div>sem fechar\tTipo_Revisao_Rapida\n'.encode(),
             'anki_cloze.tsv': b''}
    found = []
    v.validate_new_html(items, found)
    assert found and 'anki_certo_errado.tsv:1 verso/extra' in found[0]


def test_unsafe_html_rejected_even_outside_new_batches():
    found = []
    v.verify_tsvo('anki_certo_errado.tsv', 'Frente <script>x</script>.\t✅ Certo<br><br>Motivo.\tTag\n'.encode(), found)
    assert any('HTML inseguro' in e for e in found)
