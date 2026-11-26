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
    dict(id='ceb-2024-fixture-001', banca='Cebraspe', formato='certo_errado', concurso='FICTICIO', cargo='Teste', ano=2024,
         caderno='Fixture', item='1', url='https://example.test/prova', consulta=HOJE,
         operacao_observada='Operação sintética', gabarito_status='definitivo', gabarito_url='https://example.test/gab'),
    dict(id='fgv-2023-fixture-009', banca='FGV', formato='multipla_escolha', concurso='FICTICIO 2', cargo='Teste', ano=2023,
         caderno='Fixture B', item='9', url='https://example.test/prova-fgv', consulta=HOJE,
         operacao_observada='Alternativa sintética', gabarito_status='definitivo', gabarito_url='https://example.test/gab-fgv'),
]
REVISAO = dict(alvo='Alvo sintético', sol='Solução sintética', alt='Alternativa sintética testada',
               rec='Recuperação sintética', fb='Feedback sintético', fx=('si',))


def r(k, g, f):
    return dict(k=k, g=g, f=f, tags='Forca', b=[regra('A unidade SI de força é o newton.')], m='Força: newton.',
                refs=['fgv-2023-fixture-009'], **REVISAO)


def d(k, g, f, **extra):
    base = dict(k=k, g=g, f=f, tags='Forca', b=[regra('F = m·a.')] + ([erro('A conta foi invertida.')] if g == 'E' else []),
                m='Aceleração = força ÷ massa.', alvo='Aplicar F = m·a', op='Calcular a aceleração', regra='F = m·a',
                dado='6 N sobre 2 kg', solucao='6 ÷ 2 = 3 m/s²', erro='Multiplicar em vez de dividir',
                conc='Leitura concorrente sintética', orig='Situação sintética', fx=('si',), refs=['ceb-2024-fixture-001', 'fgv-2023-fixture-009'],
                fid='comparada', cmp='Mesma operação da referência sintética',
                rb=m.rubrica(*(f'Evidência sintética {i} de {k}' for i in range(8))))
    base.update(extra)
    return base


def lote(pasta, **kw):
    R = [r('R01', 'C', 'A unidade SI de força é o newton.'), r('R02', 'E', 'A unidade SI de força é o joule.')]
    D = [d('D01', 'C', 'Uma força resultante de 6 N age sobre 2 kg. A aceleração é 3 m/s².'),
         d('D02', 'E', 'Uma força resultante de 6 N age sobre 2 kg. A aceleração é 12 m/s².')]
    CZ = [dict(k='C01', tags='Forca', t='A unidade SI de força é o {{c1::newton}}.', b=[regra('Newton mede força.')],
               m='Força: newton.', cob={'1': ['D01']}, refs=['fgv-2023-fixture-009'],
               cobra='A questão sintética troca newton por joule', **REVISAO)]
    return m.Lote(pasta, '', F, HOJE, REFS, R, D, CZ, semente=1, **{'assunto': 'Fisica::Dinamica', 'pdf': 'Missao_01', **kw})


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
    assert json.loads(calibracao)['schema_version'] == 3  # 2.37
    assert json.loads(revisao)['schema_version'] == 2
    assert rev.validate(items, revisao) == []
    assert not (tmp_path / 'previa_cards.html').exists()  # sem prévia desde a 2.30


def test_metadados_curtos_2_24_passam(tmp_path, monkeypatch):
    """R/Cloze sem alt/rec/fb, Cloze sem sol e D com rubrica curta passam nos validadores."""
    curto = {k: v for k, v in REVISAO.items() if k in ('alvo', 'sol', 'fx')}
    monkeypatch.setitem(globals(), 'REVISAO', curto)
    rb = m.rubrica('Correção sintética', 'Determinação sintética', 'Operação sintética', 'Comparação sintética',
                   linguagem_didatica='Linguagem sintética')
    orig_d = d
    monkeypatch.setitem(globals(), 'd', lambda *a, **kw: orig_d(*a, **{'rb': rb, **kw}))
    final = gerar_resolvido(tmp_path)
    items, calibracao, revisao = ler(tmp_path)
    assert final.pendentes == []
    assert cal.validate(items['anki_certo_errado.tsv'], calibracao) == []
    assert rev.validate(items, revisao) == []
    registro = json.loads(revisao)['cartoes']
    assert all('alternativa_concorrente' not in x for x in registro)
    with pytest.raises(ValueError, match='linguagem_didatica'):
        m.rubrica('a', 'b', 'c', 'd')


def test_desafiador_leva_tag_da_questao_de_origem_2_31(tmp_path, monkeypatch):
    """Cada ID de `refs` do D vira tag (o nome do arquivo .md da questão); R e Cloze não ganham."""
    orig_r, orig_d = r, d
    monkeypatch.setitem(globals(), 'r', lambda *a: {**orig_r(*a), 'refs': ['ceb-2024-fixture-001']})
    monkeypatch.setitem(globals(), 'd', lambda *a, **kw: orig_d(*a, **{'refs': ['ceb-2024-fixture-001', 'fgv-2023-fixture-009', 'ceb-2024-fixture-001'], **kw}))
    final = gerar_resolvido(tmp_path)
    items, calibracao, _ = ler(tmp_path)
    linhas = items['anki_certo_errado.tsv'].decode().splitlines()
    tags = {k: linhas[n - 1].split('\t')[2].split() for k, n in final.line_of.items()}
    for k in ('D01', 'D02'):
        assert tags[k][-2:] == ['ceb-2024-fixture-001', 'fgv-2023-fixture-009'] and tags[k].count('ceb-2024-fixture-001') == 1
    assert 'ceb-2024-fixture-001' not in tags['R01'] and 'ceb-2024-fixture-001' not in tags['R02']
    assert 'ceb-2024-fixture-001' not in items['anki_cloze.tsv'].decode().split('\t')[2].split()
    assert cal.validate(items['anki_certo_errado.tsv'], calibracao) == []
    assert m.Lote.tags_origem({'refs': []}) == '' and m.Lote.tags_origem({}) == ''


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
    gerado.D[0].update(refs=['ceb-2024-fixture-001'], obp='Buscas FGV/FCC sem item acessível (sintético)')
    gerado.gerar(imprimir=False)
    registro = json.loads((pasta / 'lote' / cal.REPORT).read_text(encoding='utf-8'))
    assert registro['cartoes'][0]['outras_bancas_pendencia'].startswith('Buscas')


def test_schema_1_keeps_legacy_shape(tmp_path):
    gerar_resolvido(tmp_path, schema_calibracao=1)
    registro = json.loads((tmp_path / 'lote' / cal.REPORT).read_text(encoding='utf-8'))
    assert registro['schema_version'] == 1 and 'outras_bancas_pendencia' not in registro['cartoes'][0]


MNEMONICO_OK = ('<b>Mnemônico CE-NO-RE:</b><br>Pela Lei 9.784/1999 (art. 13), não podem ser delegados:<br>'
                'a matéria de C{{c1::ompetência}} E{{c1::xclusiva}},<br>a edição de atos NO{{c1::rmativos}}<br>'
                'e a decisão de RE{{c1::cursos administrativos}}.')


def test_multiple_omissions_only_in_mnemonic_2_33(tmp_path):
    gerado = lote(tmp_path)
    gerado.CZ[0]['t'] = 'Força em {{c1::newton}}, energia em {{c1::joule}}.'
    with pytest.raises(SystemExit, match='uma omissão por nota'):
        gerado.montar_linhas()
    gerado.CZ[0].update(t=MNEMONICO_OK, mn=dict(sigla='CE-NO-RE', origem='autoral'), cob={'*': ['D01']})
    gerado.montar_linhas()
    assert gerado.CZ[0]['cob'] == {str(i): ['D01'] for i in range(1, 5)}  # 2.36: '*' vira uma chave por lacuna
    texto, extra, tags = gerado.cz_rows[0]
    assert 'Origem do mnemônico' in extra and 'Autoral' in extra and 'autoral' not in texto.casefold()
    assert tags.split() == ['Fisica::Dinamica::Forca', 'Cloze']


def test_mnemonico_com_link_da_fonte_no_verso(tmp_path):
    gerado = lote(tmp_path)
    gerado.CZ[0].update(t=MNEMONICO_OK, mn=dict(sigla='CE-NO-RE', origem=('encontrado', 'https://example.test/mn', 'Blog X')), cob={'*': ['D01']})
    gerado.montar_linhas()
    assert '<a href="https://example.test/mn">Blog X</a>' in gerado.cz_rows[0][1]


def test_cob_de_mnemonico_exige_uma_chave_por_lacuna_2_36(tmp_path):
    gerado = lote(tmp_path)
    gerado.CZ[0].update(t=MNEMONICO_OK, mn=dict(sigla='CE-NO-RE', origem='autoral'), cob={'1': ['D01']})
    with pytest.raises(SystemExit, match='uma chave por lacuna'):
        gerado.montar_linhas()


def test_tag_com_dois_pontos_ganha_a_disciplina_2_36(tmp_path):
    """Tag de card com '::' que não começa pela disciplina do ASSUNTO recebe o prefixo; a completa fica como está."""
    gerado = lote(tmp_path, assunto='Fisica')
    gerado.tags_pagina = {}
    assert gerado._tags({'k': 'X', 'tags': 'Dinamica::Forca'}) == 'Fisica::Dinamica::Forca'
    assert gerado._tags({'k': 'X', 'tags': 'Fisica::Dinamica::Energia'}) == 'Fisica::Dinamica::Energia'


@pytest.mark.parametrize('texto', [
    # o caso reprovado pelo usuário: origem na frente e a lista inteira numa lacuna só
    'Dica autoral CE-NO-RE: pela Lei 9.784/1999 (art. 13), não podem ser delegados {{c1::a matéria de Competência '
    'Exclusiva, a edição de atos NOrmativos e a decisão de REcursos administrativos}}.',
    # sem letra-pista visível antes da lacuna
    '<b>Mnemônico CE-NO-RE:</b><br>não se delegam: {{c1::competência}} {{c1::exclusiva}}.',
    # sem título
    'Não se delegam: C{{c1::ompetência}} E{{c1::xclusiva}}.',
])
def test_mnemonico_fora_do_formato_reprovado(tmp_path, texto):
    gerado = lote(tmp_path)
    gerado.CZ[0].update(t=texto, mn=dict(sigla='CE-NO-RE', origem='autoral'))
    with pytest.raises(SystemExit):
        gerado.montar_linhas()


@pytest.mark.parametrize('base, kw', [('PRF', {}), ('', {'assunto': ''}), ('Revisao_PDF', {})])
def test_tags_proibidas_ou_sem_assunto_reprovadas_2_33(tmp_path, base, kw):
    gerado = lote(tmp_path, **kw)
    gerado.base = base
    if kw:
        gerado.assunto = ''
    with pytest.raises(SystemExit, match='TAGS'):
        gerado.montar_linhas()


def test_tags_do_lote_sem_pdf_2_33(tmp_path):
    gerado = lote(tmp_path)
    gerado.montar_linhas()
    r01 = gerado.ce_rows[gerado.line_of['R01'] - 1][2].split()
    d01 = gerado.ce_rows[gerado.line_of['D01'] - 1][2].split()
    assert r01 == ['Fisica::Dinamica::Forca', 'Rapida']
    assert d01 == ['Fisica::Dinamica::Forca', 'Desafiadora', 'ceb-2024-fixture-001', 'fgv-2023-fixture-009']
    assert 'Missao_01' not in ' '.join(r01 + d01)  # PDF só com Pagina_NN


def test_referencias_do_banco_por_id_e_registro_de_uso(tmp_path):
    """IDs do banco referencias/ viram referências da calibração e registram o uso."""
    import sys
    sys.path.insert(0, str(m.SCRIPTS_REFERENCIAS))
    import referencias as banco_mod

    banco = tmp_path / 'referencias'
    ids = {}
    for chave, ref in (('ceb-2024-fixture-001', REFS[0]), ('fgv-2023-fixture-009', REFS[1])):
        dados = {k: v for k, v in ref.items() if k != 'id'}
        dados.update(orgao=f'Órgão {chave}', disciplina='fisica', assunto='dinamica', subassuntos=['segunda_lei'],
                     palavras_chave=['força'], gabarito='C' if chave == 'ceb-2024-fixture-001' else 'A', origem='pesquisa_internet',
                     fonte_descoberta='Fixture sintética', concursos_alvo=['PRF'], enunciado=f'Item sintético {chave}.',
                     alternativas={'A': 'x', 'B': 'y'} if chave == 'fgv-2023-fixture-009' else None)
        status, questao, msgs = banco_mod.nova(dados, banco)
        assert status == 'criada', msgs
        ids[chave] = questao.id

    pasta = tmp_path / 'lote_banco'
    (pasta / 'fonte').mkdir(parents=True)
    gerado = lote(pasta, banco_referencias=banco)
    for x in gerado.D:
        x['refs'] = [ids['ceb-2024-fixture-001'], ids['fgv-2023-fixture-009']]
    for x in gerado.R + gerado.CZ:
        x['refs'] = [ids['fgv-2023-fixture-009']]
    gerado.refs = gerado._resolver_refs([])  # os IDs citados nos cartões bastam
    gerado.gerar(imprimir=False)
    items, calibracao, _ = ler(pasta)
    registro = json.loads(calibracao)
    assert sorted(r['id'] for r in registro['referencias']) == sorted([ids['ceb-2024-fixture-001'], ids['fgv-2023-fixture-009']])
    assert cal.validate(items['anki_certo_errado.tsv'], calibracao) == []
    usos = banco_mod.localizar([ids['ceb-2024-fixture-001']], banco)[0].meta['usado_em']
    assert usos == ['lote_banco#D01,D02']


def test_sugere_item_cebraspe_do_banco_para_d_em_inspiracao_geral(tmp_path, capsys):
    import sys
    sys.path.insert(0, str(m.SCRIPTS_REFERENCIAS))
    import referencias as banco_mod

    banco = tmp_path / 'referencias'
    ids = {}
    for chave, ref in (('ceb-2024-fixture-001', REFS[0]), ('fgv-2023-fixture-009', REFS[1])):
        dados = {k: v for k, v in ref.items() if k != 'id'}
        dados.update(orgao=f'Órgão {chave}', disciplina='fisica', assunto='dinamica', subassuntos=['segunda_lei'],
                     palavras_chave=['força'], gabarito='C' if chave == 'ceb-2024-fixture-001' else 'A', origem='pesquisa_internet',
                     fonte_descoberta='Fixture sintética', concursos_alvo=['PRF'], enunciado=f'Item sintético {chave}.',
                     alternativas={'A': 'x', 'B': 'y'} if chave == 'fgv-2023-fixture-009' else None)
        ids[chave] = banco_mod.nova(dados, banco)[1].id
    pasta = tmp_path / 'lote_sugestao'
    (pasta / 'fonte').mkdir(parents=True)
    gerado = lote(pasta, banco_referencias=banco, registrar_uso=False)
    gerado.D[0].update(refs=[ids['fgv-2023-fixture-009']], fid='inspiracao_geral', lim='Limitação sintética')
    gerado.D[1].update(refs=[], fid='inspiracao_geral', lim='Limitação sintética', a='fisica/dinamica')
    assert gerado.sugestoes_cebraspe() == {'D01': [ids['ceb-2024-fixture-001']], 'D02': [ids['ceb-2024-fixture-001']]}
    gerado.D[0]['refs'] = [ids['ceb-2024-fixture-001'], ids['fgv-2023-fixture-009']]
    gerado.D[0]['fid'] = 'comparada'
    assert gerado.sugestoes_cebraspe() == {'D02': [ids['ceb-2024-fixture-001']]}
    gerado.D[1]['sa'] = ['primeira_lei']  # subtema diferente: sem aviso (2.29)
    assert gerado.sugestoes_cebraspe() == {}
    gerado.D[1]['sa'] = 'segunda_lei, terceira_lei'
    assert gerado.sugestoes_cebraspe() == {'D02': [ids['ceb-2024-fixture-001']]}


def test_questao_sem_prova_vai_para_referencias_sem_prova(tmp_path):
    """Questão do PDF sem url: inspiração de outra banca, fora das referências comparadas."""
    import sys
    sys.path.insert(0, str(m.SCRIPTS_REFERENCIAS))
    import referencias as banco_mod

    banco = tmp_path / 'referencias'
    dados = dict(banca='Vunesp', formato='multipla_escolha', ano=2023, orgao='Prefeitura Fictícia',
                 concurso='Prefeitura Fictícia — 2023', disciplina='fisica', assunto='dinamica',
                 subassuntos=['segunda_lei'], palavras_chave=['força'], gabarito='B', gabarito_status='nao_verificado',
                 origem='anexo_usuario', fonte_descoberta='apostila sintética, p. 3, questão 01', consulta=HOJE,
                 concursos_alvo=['PRF'], operacao_observada='Operação sintética sem prova', item='nao_localizado',
                 enunciado='Item sintético sem prova.', alternativas={'A': 'x', 'B': 'y'})
    status, questao, msgs = banco_mod.nova(dados, banco)
    assert status == 'criada', msgs

    pasta = tmp_path / 'lote_sem_prova'
    (pasta / 'fonte').mkdir(parents=True)
    gerado = lote(pasta, banco_referencias=banco)
    gerado.D[0]['refs'] = ['ceb-2024-fixture-001', questao.id]
    gerado.D[1]['refs'] = ['ceb-2024-fixture-001', questao.id]
    for x in gerado.R + gerado.CZ:
        x['refs'] = [questao.id]
    gerado.refs = gerado._resolver_refs([REFS[0]])
    gerado.gerar(imprimir=False)
    items, calibracao, _ = ler(pasta)
    registro = json.loads(calibracao)
    assert [r['id'] for r in registro['referencias']] == ['ceb-2024-fixture-001']
    assert [r['id'] for r in registro['referencias_sem_prova']] == [questao.id]
    assert registro['cartoes'][0]['referencias'] == ['ceb-2024-fixture-001']
    assert registro['cartoes'][0]['referencias_sem_prova'] == [questao.id]
    # A questão de outra banca sem prova satisfaz a exigência de outra banca; não há pendência.
    assert cal.validate(items['anki_certo_errado.tsv'], calibracao) == []
    usos = banco_mod.localizar([questao.id], banco)[0].meta['usado_em']
    assert usos == ['lote_sem_prova#R01,R02,D01,D02,C01']


COBERTURA = [
    dict(u='U01', pag='3', p='alta', conteudo='Unidade de força no SI (sintético)', cartoes=['R01', 'R02', 'C01']),
    dict(u='U02', pag='4-5', p='media', conteudo='Segunda lei de Newton (sintético)', cartoes=['D01', 'D02']),
    dict(u='U03', pag='1', conteudo='Sumário', excluir='nao_conteudo: sumário'),
    dict(u='U04', pag='6', p='baixa', conteudo='Curiosidade histórica (sintético)', motivo='Periférico para o cargo'),
    dict(u='U05', pag='7', p='media', conteudo='Definição já na coleção (sintético)', colecao=['1234567890']),
]


def test_cobertura_total_gera_tags_de_pagina_e_passa_no_validador(tmp_path):
    import validar_cobertura_pdf as cob
    final = gerar_resolvido(tmp_path, cobertura=COBERTURA)
    assert final.pendentes == []
    items, calibracao, revisao = ler(tmp_path)
    linhas_ce = items['anki_certo_errado.tsv'].decode().splitlines()
    d01 = linhas_ce[final.line_of['D01'] - 1].split('\t')[2].split()
    assert 'Pagina_04' in d01 and 'Pagina_05' in d01 and 'Pagina_03' not in d01
    assert 'Pagina_03' in items['anki_cloze.tsv'].decode().split('\t')[2].split()
    registro = json.loads((tmp_path / 'lote' / 'relatorios' / 'cobertura_pdf.json').read_text(encoding='utf-8'))
    assert registro['unidades'][1]['pag'] == [4, 5]
    assert cob.validar(cob.ler(tmp_path / 'lote')) == []
    assert registro['unidades'][3]['p'] == 'baixa' and registro['unidades'][3]['cartoes'] == []
    assert b'Prioridade_' not in items['anki_certo_errado.tsv']
    assert cal.validate(items['anki_certo_errado.tsv'], calibracao) == []
    assert rev.validate(items, revisao) == []


@pytest.mark.parametrize('mudanca, esperado', [
    (lambda c: c[0].update(cartoes=[]), 'sem card nem nota da coleção'),
    (lambda c: c[1].update(cartoes=['D01']), 'D02: card sem unidade Alta ou Média'),
    (lambda c: c[0].update(cartoes=['R01', 'R02', 'C01', 'R99']), 'R99 não existe'),
    (lambda c: c.append(dict(u='Q01', pag='9', p='alta', questao='questao-x', cartoes=['D01'])), 'questao-x precisa estar nos refs'),
    (lambda c: c[2].update(excluir='curiosidade'), 'excluir é só para texto que não é conteúdo'),
    (lambda c: c[3].update(cartoes=['R01']), 'prioridade baixa não vira card'),
    (lambda c: c[3].pop('motivo'), 'prioridade baixa exige motivo'),
    (lambda c: c[4].pop('colecao'), 'sem card nem nota da coleção'),
    (lambda c: c[1].pop('p'), 'p deve ser alta, media ou baixa'),
    (lambda c: c[1].update(p='baixa', motivo='x'), 'prioridade baixa não vira card'),
])
def test_cobertura_incompleta_falha(tmp_path, mudanca, esperado):
    cobertura = [dict(u) for u in COBERTURA]
    mudanca(cobertura)
    with pytest.raises(SystemExit) as falha:
        lote(tmp_path, cobertura=cobertura).gerar(imprimir=False)
    assert esperado in str(falha.value)


def test_questoes_do_pdf_viram_unidades_pelos_refs_2_29(tmp_path):
    import validar_cobertura_pdf as cob
    final = gerar_resolvido(tmp_path, cobertura=COBERTURA, questoes_pdf={'Q01': ('8', 'ceb-2024-fixture-001')})
    assert final.pendentes == []
    registro = json.loads((tmp_path / 'lote' / 'relatorios' / 'cobertura_pdf.json').read_text(encoding='utf-8'))
    q01 = [u for u in registro['unidades'] if u['u'] == 'Q01'][0]
    assert q01['p'] == 'media' and q01['questao'] == 'ceb-2024-fixture-001' and sorted(q01['ids_editoriais']) == ['D01', 'D02']
    assert cob.validar(cob.ler(tmp_path / 'lote')) == []
    triagem = (tmp_path / 'lote' / 'relatorios' / 'triagem_previa_pdf.txt').read_text(encoding='utf-8')
    assert 'Q01 | 8 | media | Questão 01 do PDF [ceb-2024-fixture-001]' in triagem and m.MARCA_GERADO in triagem


def test_questao_do_pdf_sem_card_exige_unidade_declarada(tmp_path):
    with pytest.raises(SystemExit) as falha:
        lote(tmp_path, cobertura=[dict(u) for u in COBERTURA], questoes_pdf={'Q02': ('9', 'nao-citada')}).gerar(imprimir=False)
    assert 'Q02 (nao-citada): nenhum card a cita' in str(falha.value)


def test_padrao_d_completa_so_as_chaves_ausentes_e_regra_vem_da_fonte(tmp_path):
    padrao = dict(rb=m.rubrica('c', 'd', 'o', 'cmp', linguagem_didatica='termos explicados'), orig='Caso autoral.')
    base = lote(tmp_path)
    D = [{k: v for k, v in x.items() if k not in ('rb', 'orig', 'regra')} for x in base.D]
    D[1]['orig'] = 'Origem própria'
    novo = m.Lote(tmp_path, '', F, HOJE, REFS, base.R, D, base.CZ, semente=1, padrao_d=padrao, assunto='Fisica::Dinamica')
    assert novo.D[0]['orig'] == 'Caso autoral.' and novo.D[1]['orig'] == 'Origem própria'
    assert novo.D[0]['regra'] == F['si'][1] and novo.D[0]['rb'] == padrao['rb']


def test_relatorios_gerados_e_manuscrito_preservado(tmp_path):
    rel = tmp_path / 'lote' / 'relatorios'
    rel.mkdir(parents=True)
    (rel / 'economia_de_revisao.txt').write_text('Escrito à mão.', encoding='utf-8')
    gerar_resolvido(tmp_path, cobertura=COBERTURA, relatorio={'material': 'Apostila sintética'})
    assert (rel / 'economia_de_revisao.txt').read_text(encoding='utf-8') == 'Escrito à mão.'
    auditoria = (rel / 'auditoria_pedagogica.txt').read_text(encoding='utf-8')
    assert 'D01 (CE:' in auditoria and 'C01 (CZ:1) | Cloze' in auditoria
    assert 'Material: Apostila sintética' in (rel / 'triagem_previa_pdf.txt').read_text(encoding='utf-8')
    fontes = (rel / 'fontes_e_referencias.txt').read_text(encoding='utf-8')
    assert '- ceb-2024-fixture-001: ' in fontes and 'si: https://example.test/si' in fontes


def test_validador_de_cobertura_aponta_tag_de_pagina_ausente(tmp_path):
    import validar_cobertura_pdf as cob
    gerar_resolvido(tmp_path, cobertura=COBERTURA)
    pasta = tmp_path / 'lote'
    ce = (pasta / 'anki_certo_errado.tsv').read_text(encoding='utf-8').replace(' Pagina_03', '', 1)
    (pasta / 'anki_certo_errado.tsv').write_text(ce, encoding='utf-8', newline='\n')
    assert any('Pagina_03' in e for e in cob.validar(cob.ler(pasta)))


def test_lote_sem_cobertura_nao_ganha_tags_de_pagina(tmp_path):
    gerar_resolvido(tmp_path)
    items, _, _ = ler(tmp_path)
    assert b'Pagina_' not in items['anki_certo_errado.tsv']
    assert not (tmp_path / 'lote' / 'relatorios' / 'cobertura_pdf.json').exists()


def test_modelos_do_exportador_usam_o_css_padrao():
    import sys as _sys
    genanki = pytest.importorskip('genanki')
    _sys.path.insert(0, str(Path(m.__file__).resolve().parents[2] / 'automacao-anki-python' / 'scripts'))
    import exportar_anki
    import estilo_anki
    basic, clz = exportar_anki.modelos(genanki)
    assert basic.css == estilo_anki.CSS_BASE and 'font-size: 20px' in basic.css
    assert clz.css == estilo_anki.CSS_CLOZE and '.cloze' in clz.css
    assert (basic.model_id, basic.name) == estilo_anki.MODELO_CE
    assert (clz.model_id, clz.name) == estilo_anki.MODELO_CLOZE


def test_uso_de_card_retirado_sai_do_banco(tmp_path):
    """Questão que deixou de estar nos refs do lote perde o registro de uso daquele lote."""
    import sys
    sys.path.insert(0, str(m.SCRIPTS_REFERENCIAS))
    import referencias as banco_mod
    banco = tmp_path / 'referencias'
    dados = {k: v for k, v in REFS[0].items() if k != 'id'}
    dados.update(orgao='Órgão X', disciplina='fisica', assunto='dinamica', subassuntos=['segunda_lei'],
                 palavras_chave=['força'], gabarito='C', origem='pesquisa_internet', fonte_descoberta='Fixture',
                 concursos_alvo=['PRF'], enunciado='Item sintético para uso.')
    _, questao, _ = banco_mod.nova(dados, banco)
    pasta = tmp_path / 'lote_uso'
    (pasta / 'fonte').mkdir(parents=True)
    primeiro = lote(pasta, banco_referencias=banco)
    primeiro.R[0]['refs'] = [questao.id]
    primeiro.refs = primeiro._resolver_refs(REFS)
    primeiro.gerar(imprimir=False)
    assert banco_mod.localizar([questao.id], banco)[0].meta['usado_em'] == ['lote_uso#R01']
    segundo = lote(pasta, banco_referencias=banco)
    segundo.gerar(imprimir=False)
    assert banco_mod.localizar([questao.id], banco)[0].meta['usado_em'] == []


def test_fontes_aceitam_id_de_conteudo_do_banco(tmp_path):
    import sys, datetime
    sys.path.insert(0, str(m.SCRIPTS_REFERENCIAS))
    import referencias as banco_mod
    banco = tmp_path / 'referencias'
    status, q, msgs = banco_mod.nova(dict(tipo='conteudo', titulo='SI sintético', disciplina='fisica', assunto='dinamica',
                                         subassuntos=['unidades'], palavras_chave=['newton'], concursos_alvo=['PRF'],
                                         url='https://example.test/si', fonte_descoberta='Fixture', norma='SI sintético',
                                         dispositivos=['força'], situacao='vigente',
                                         verificado_em=datetime.date.today().isoformat(), corpo='## Força\n\nNewton.'), banco)
    assert status == 'criada', msgs
    gerado = lote(tmp_path / 'lote_fonte', banco_referencias=banco)
    gerado.F = {'si': q.id}
    novo = m.Lote(tmp_path / 'lote_fonte', '', {'si': q.id}, HOJE, REFS, gerado.R, gerado.D, gerado.CZ, semente=1,
                  banco_referencias=banco, assunto='Fisica::Dinamica')
    assert novo.F['si'][0] == 'https://example.test/si' and q.id in novo.F['si'][1]
    secao = m.Lote(tmp_path / 'lote_secao', '', {'si': q.id + '#Força'}, HOJE, REFS, gerado.R, gerado.D, gerado.CZ,
                   semente=1, banco_referencias=banco, assunto='Fisica::Dinamica')
    assert 'Força' in secao.F['si'][1] and q.id in secao.F['si'][1]
    secao.gerar(imprimir=False)  # todos os cartões da fixture citam a fonte 'si'
    usos = banco_mod.localizar([q.id], banco)[0].meta['usado_em']
    assert len(usos) == 1 and usos[0].startswith('lote_secao#') and 'R01' in usos[0]


# ------------------------------------------------------------ evidência de cobrança (2.37)
@pytest.mark.parametrize('mudanca, esperado', [
    (lambda g: g.D[0].update(refs=[]), 'D01: D precisa de ao menos uma questão real'),
    (lambda g: g.D[0].update(nucleo='Regra central sintética'), 'D01: D não aceita nucleo'),
    (lambda g: g.R[0].update(refs=[]), 'R01: sem questão real em refs'),
    (lambda g: g.CZ[0].update(refs=[]), 'C01: sem questão real em refs'),
    (lambda g: g.CZ[0].pop('cobra'), 'C01: Cloze precisa de cobra='),
])
def test_card_sem_evidencia_de_cobranca_falha_2_37(tmp_path, mudanca, esperado):
    gerado = lote(tmp_path)
    mudanca(gerado)
    with pytest.raises(SystemExit) as falha:
        gerado.montar_linhas()
    assert 'EVIDÊNCIA DE COBRANÇA' in str(falha.value) and esperado in str(falha.value)


def test_nucleo_do_cargo_dispensa_questao_so_em_r_e_cloze_2_37(tmp_path):
    def nucleo(g):
        g.R[0].update(refs=[], nucleo='Regra central sintética do cargo')
        g.CZ[0].update(refs=[], nucleo='Regra central sintética do cargo')
    (tmp_path / 'fonte').mkdir()
    primeiro = lote(tmp_path, cobertura=COBERTURA)
    nucleo(primeiro)
    primeiro.gerar(imprimir=False)
    motivos = {chave: 'Justificativa SINTÉTICA de teste' for chave in primeiro.pendentes}
    (tmp_path / 'fonte' / 'sinais_resolvidos.json').write_text(json.dumps(motivos), encoding='utf-8')
    final = lote(tmp_path, cobertura=COBERTURA)
    nucleo(final)
    final.gerar(imprimir=False)
    items, calibracao, revisao = ler(tmp_path)
    assert rev.validate(items, revisao) == [] and cal.validate(items['anki_certo_errado.tsv'], calibracao) == []
    registro = {x['id']: x for x in json.loads(revisao)['cartoes']}
    r01 = registro[final.rid('R01')]
    assert r01['evidencia_cobranca'] == {'nucleo_cargo': 'Regra central sintética do cargo'}
    assert registro[final.rid('R02')]['evidencia_cobranca'] == {'questoes': ['fgv-2023-fixture-009']}
    assert registro['anki_cloze.tsv:1']['cobranca_do_termo'].startswith('A questão sintética')
    fontes = (tmp_path / 'lote' / 'relatorios' / 'fontes_e_referencias.txt').read_text(encoding='utf-8')
    assert '- R01: núcleo do cargo — Regra central sintética do cargo' in fontes
    assert '- R02: fgv-2023-fixture-009' in fontes and 'termo cobrado: A questão sintética' in fontes


def test_validador_de_revisao_exige_evidencia_no_schema_2(tmp_path):
    gerar_resolvido(tmp_path)
    items, _, revisao = ler(tmp_path)
    dados = json.loads(revisao)
    for x in dados['cartoes']:
        x.pop('evidencia_cobranca')
        x.pop('cobranca_do_termo', None)
    erros = rev.validate(items, json.dumps(dados).encode())
    assert any('evidencia_cobranca' in e for e in erros) and any('cobranca_do_termo' in e for e in erros)
    dados['schema_version'] = 1  # legado: sem a exigência
    assert not any('evidencia' in e or 'cobranca' in e for e in rev.validate(items, json.dumps(dados).encode()))


def test_calibracao_schema_3_reprova_d_sem_questao_real(tmp_path):
    gerar_resolvido(tmp_path)
    items, calibracao, _ = ler(tmp_path)
    dados = json.loads(calibracao)
    dados['cartoes'][0].update(referencias=[], fidelidade='inspiracao_geral', limitacao='Sintética',
                               outras_bancas_pendencia='Buscas sintéticas sem resultado')
    dados['cartoes'][0].pop('comparacao', None)
    erros = cal.validate(items['anki_certo_errado.tsv'], json.dumps(dados).encode())
    assert any('D sem questão real' in e for e in erros)
