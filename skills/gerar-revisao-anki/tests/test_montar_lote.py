"""montar_lote.py com um mini-lote SINTÉTICO; não é conteúdo de estudo aprovado."""
import json
from pathlib import Path

import pytest

import montar_lote as m
import validar_calibracao_cebraspe as cal
import validar_revisao_pedagogica as rev
from html_anki import erro, regra

HOJE = '2026-11-18'
F = {'si': ('https://example.test/si', 'Fonte FICTÍCIA de teste sobre unidades do SI')}
REFS = [
    dict(id='CEB', banca='Cebraspe', formato='certo_errado', concurso='FICTICIO', cargo='Teste', ano=2024,
         caderno='Fixture', item='1', url='https://example.test/prova', consulta=HOJE,
         operacao_observada='Operação sintética', gabarito_status='definitivo', gabarito_url='https://example.test/gab'),
    dict(id='FGV', banca='FGV', formato='multipla_escolha', concurso='FICTICIO 2', cargo='Teste', ano=2023,
         caderno='Fixture B', item='9', url='https://example.test/prova-fgv', consulta=HOJE,
         operacao_observada='Alternativa sintética', gabarito_status='definitivo', gabarito_url='https://example.test/gab-fgv'),
]
REVISAO = dict(alvo='Alvo sintético', sol='Solução sintética', alt='Alternativa sintética testada',
               rec='Recuperação sintética', fb='Feedback sintético', fx=('si',))


def r(k, g, f):
    return dict(k=k, g=g, f=f, tags='Fisica', b=[regra('A unidade SI de força é o newton.')], m='Força: newton.', **REVISAO)


def d(k, g, f, **extra):
    base = dict(k=k, g=g, f=f, tags='Fisica', b=[regra('F = m·a.')] + ([erro('A conta foi invertida.')] if g == 'E' else []),
                m='Aceleração = força ÷ massa.', alvo='Aplicar F = m·a', op='Calcular a aceleração', regra='F = m·a',
                dado='6 N sobre 2 kg', solucao='6 ÷ 2 = 3 m/s²', erro='Multiplicar em vez de dividir',
                conc='Leitura concorrente sintética', orig='Situação sintética', fx=('si',), refs=['CEB', 'FGV'],
                fid='comparada', cmp='Mesma operação da referência sintética',
                rb=m.rubrica(*(f'Evidência sintética {i} de {k}' for i in range(8))))
    base.update(extra)
    return base


def lote(pasta, **kw):
    R = [r('R01', 'C', 'A unidade SI de força é o newton.'), r('R02', 'E', 'A unidade SI de força é o joule.')]
    D = [d('D01', 'C', 'Uma força resultante de 6 N age sobre 2 kg. A aceleração é 3 m/s².'),
         d('D02', 'E', 'Uma força resultante de 6 N age sobre 2 kg. A aceleração é 12 m/s².')]
    CZ = [dict(k='C01', tags='Fisica', t='A unidade SI de força é o {{c1::newton}}.', b=[regra('Newton mede força.')],
               m='Força: newton.', cob={'1': ['D01']}, **REVISAO)]
    return m.Lote(pasta, 'Teste Fixture', F, HOJE, REFS, R, D, CZ, semente=1, **kw)


def ler(pasta):
    out = Path(pasta) / 'lote'
    items = {name: (out / name).read_bytes() for name in rev.FILES}
    return items, (out / cal.REPORT).read_bytes(), (out / rev.REPORT).read_bytes()


def gerar_resolvido(pasta, **kw):
    """Gera, justifica os sinais pendentes (sinteticamente) e gera de novo."""
    (pasta / 'fonte').mkdir(parents=True, exist_ok=True)
    primeiro = lote(pasta, **kw)
    primeiro.gerar(imprimir=False)
    motivos = {chave: 'Justificativa SINTÉTICA de teste' for chave in primeiro.pendentes}
    (pasta / 'fonte' / 'sinais_resolvidos.json').write_text(json.dumps(motivos), encoding='utf-8')
    final = lote(pasta, **kw)
    final.gerar(imprimir=False)
    return final


def test_generated_batch_passes_documentary_validators(tmp_path):
    final = gerar_resolvido(tmp_path)
    assert final.pendentes == []
    items, calibracao, revisao = ler(tmp_path)
    assert cal.validate(items['anki_certo_errado.tsv'], calibracao) == []
    assert json.loads(calibracao)['schema_version'] == 2
    assert rev.validate(items, revisao) == []
    assert (tmp_path / 'previa_cards.html').is_file()


def test_tsvs_are_utf8_without_bom_and_lf(tmp_path):
    gerar_resolvido(tmp_path)
    items, _, _ = ler(tmp_path)
    for data in items.values():
        assert not data.startswith(b'\xef\xbb\xbf') and b'\r' not in data and data.endswith(b'\n')
    ce = items['anki_certo_errado.tsv'].decode().splitlines()
    assert len(ce) == 4 and all(len(row.split('\t')) == 3 for row in ce)


def test_shuffle_is_reproducible(tmp_path):
    a, b = gerar_resolvido(tmp_path / 'a'), gerar_resolvido(tmp_path / 'b')
    assert a.line_of == b.line_of


def test_unresolved_signals_are_reported(tmp_path, capsys):
    (tmp_path / 'fonte').mkdir()
    gerado = lote(tmp_path)
    gerado.gerar(imprimir=False)
    if gerado.pendentes:
        assert 'SINAIS PENDENTES' in capsys.readouterr().out
        items, _, revisao = ler(tmp_path)
        assert rev.validate(items, revisao)


def test_other_bank_pending_goes_to_schema_2_record(tmp_path):
    pasta = tmp_path
    (pasta / 'fonte').mkdir()
    gerado = lote(pasta)
    gerado.D[0].update(refs=['CEB'], obp='Buscas FGV/FCC sem item acessível (sintético)')
    gerado.gerar(imprimir=False)
    registro = json.loads((pasta / 'lote' / cal.REPORT).read_text(encoding='utf-8'))
    assert registro['cartoes'][0]['outras_bancas_pendencia'].startswith('Buscas')


def test_schema_1_keeps_legacy_shape(tmp_path):
    gerar_resolvido(tmp_path, schema_calibracao=1)
    registro = json.loads((tmp_path / 'lote' / cal.REPORT).read_text(encoding='utf-8'))
    assert registro['schema_version'] == 1 and 'outras_bancas_pendencia' not in registro['cartoes'][0]


def test_multiple_omissions_require_mnemonic_tag(tmp_path):
    gerado = lote(tmp_path)
    gerado.CZ[0]['t'] = 'Força em {{c1::newton}}, energia em {{c1::joule}}.'
    with pytest.raises(AssertionError):
        gerado.montar_linhas()
    gerado.CZ[0]['tags'] = 'Fisica Mnemonico'
    gerado.montar_linhas()


def test_referencias_do_banco_por_id_e_registro_de_uso(tmp_path):
    """IDs do banco referencias/ viram referências da calibração e registram o uso."""
    import sys
    sys.path.insert(0, str(m.SCRIPTS_REFERENCIAS))
    import referencias as banco_mod

    banco = tmp_path / 'referencias'
    ids = {}
    for chave, ref in (('CEB', REFS[0]), ('FGV', REFS[1])):
        dados = {k: v for k, v in ref.items() if k != 'id'}
        dados.update(orgao=f'Órgão {chave}', disciplina='fisica', assunto='dinamica', subassuntos=['segunda_lei'],
                     palavras_chave=['força'], gabarito='C' if chave == 'CEB' else 'A', origem='pesquisa_internet',
                     fonte_descoberta='Fixture sintética', concursos_alvo=['PRF'], enunciado=f'Item sintético {chave}.',
                     alternativas={'A': 'x', 'B': 'y'} if chave == 'FGV' else None)
        status, questao, msgs = banco_mod.nova(dados, banco)
        assert status == 'criada', msgs
        ids[chave] = questao.id

    pasta = tmp_path / 'lote_banco'
    (pasta / 'fonte').mkdir(parents=True)
    gerado = lote(pasta, banco_referencias=banco)
    gerado.refs = gerado._resolver_refs([ids['CEB'], ids['FGV']])
    for x in gerado.D:
        x['refs'] = [ids['CEB'], ids['FGV']]
    gerado.gerar(imprimir=False)
    items, calibracao, _ = ler(pasta)
    registro = json.loads(calibracao)
    assert [r['id'] for r in registro['referencias']] == [ids['CEB'], ids['FGV']]
    assert cal.validate(items['anki_certo_errado.tsv'], calibracao) == []
    usos = banco_mod.localizar([ids['CEB']], banco)[0].meta['usado_em']
    assert usos == ['lote_banco#D01,D02']
