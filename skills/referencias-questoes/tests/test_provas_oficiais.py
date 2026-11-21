"""Importação de provas oficiais e contagem de prioridades, com PDFs e dados SINTÉTICOS."""
import pytest

import provas_oficiais as po
import referencias as ref

pymupdf = pytest.importorskip('pymupdf')

CFG = dict(ano=2024, orgao='ORGAO TESTE', pasta='TESTE_24', caderno='CAD_01', url='https://example.test/cad.pdf',
           gabarito_url='https://example.test/gab.pdf', concurso='Concurso fictício 2024', cargo='Cargo fictício',
           alvo='PRF', itens='1-3')

SPEC = """#disc informatica
1 correio_eletronico | protocolos | smtp; envio | Função do SMTP.
2 correio_eletronico | protocolos | pop3 | Função do POP3.
#disc portugues
3 interpretacao | inferencia | texto fictício | Inferência sobre o texto.
!enun 2 Linha um⏎Linha dois
!vig 3 Lei fictícia revogada.
"""


def _pdf(caminho, linhas):
    doc = pymupdf.open()
    pg = doc.new_page(width=595, height=842)
    for x, y, t in linhas:
        pg.insert_text((x, y), t, fontsize=10)
    doc.save(str(caminho))


@pytest.fixture
def cadernos(tmp_path):
    cad, gab = tmp_path / 'cad.pdf', tmp_path / 'gab.pdf'
    _pdf(cad, [(28, 100, 'Texto 9A1-I'), (56, 116, 'Era uma vez um texto fictício sobre provas.'),
               (28, 132, 'Julgue os itens a seguir.'),
               (28, 150, '1 O protocolo SMTP é usado para'), (46, 163, 'receber mensagens.'),
               (28, 180, '2 O POP3 envia mensagens.'),
               (28, 200, 'Com base no texto 9A1-I, julgue o item.'),
               (28, 218, '3 O texto é fictício.')])
    _pdf(gab, [(30, 100, '1'), (60, 100, '2'), (90, 100, '3'), (30, 120, 'E'), (60, 120, 'X'), (90, 120, 'C')])
    return cad, gab


def test_extrai_itens_texto_base_e_gabarito(cadernos):
    cad, gab = cadernos
    itens = po.extrair_caderno(cad, 1, 3)
    assert [i['item'] for i in itens] == [1, 2, 3]
    assert itens[0]['enunciado'] == 'O protocolo SMTP é usado para receber mensagens.'
    assert itens[0]['contexto'][0] == 'Texto 9A1-I' and itens[0]['contexto'][-1] == 'Julgue os itens a seguir.'
    assert itens[1]['contexto'] == itens[0]['contexto']
    assert itens[2]['contexto'] == ['Com base no texto 9A1-I, julgue o item.']
    assert po.ler_gabarito(gab) == {1: 'E', 2: 'X', 3: 'C'}


def test_spec_e_correcoes():
    itens, fix = po.ler_spec(SPEC + '4 =existente\n')
    assert itens[1]['disciplina'] == 'informatica' and itens[1]['palavras_chave'] == ['smtp', 'envio']
    assert itens[4] is None and fix['vig'][3].startswith('Lei fictícia')
    with pytest.raises(ref.ErroBanco):
        po.ler_spec('#disc rlm\n5 assunto | sub | a | b | c\n')


def test_paragrafos_limpa_lixo_e_cola_linhas():
    ctx = ['-- CONHECIMENTOS BÁSICOS --', 'Bloco I', 'Texto 1A1-I', 'Primeira linha do texto que', 'continua aqui.',
           'Autor. Obra. In: Revista', 'v. 1, 2020.', 'Julgue os itens.']
    assert po.paragrafos(ctx) == ['Texto 1A1-I', 'Primeira linha do texto que continua aqui.',
                                  'Autor. Obra. In: Revista v. 1, 2020.', 'Julgue os itens.']
    assert po.matematica('𝛾 e 𝑋') == 'γ e X'


def test_montar_gera_questoes_validas_e_repete_o_texto(cadernos, tmp_path):
    cad, gab = cadernos
    itens = po.extrair_caderno(cad, 1, 3)
    g = po.ler_gabarito(gab)
    for it in itens:
        it['gabarito'] = g[it['item']]
    banco = tmp_path / 'referencias'
    novos, exist, faltam = po.montar('teste', itens, SPEC, '2026-11-21', banco, CFG)
    assert (len(novos), exist, faltam) == (3, [], [])
    n1, n2, n3 = novos
    assert n2['gabarito'] == 'anulada' and n2['gabarito_status'] == 'anulado'
    assert n2['operacao_observada'].startswith('Item anulado.') and n2['enunciado'] == 'Linha um\nLinha dois'
    assert n1['concursos_alvo'] == ['PRF', 'PF_AGENTE']
    assert 'Era uma vez' in n3['texto_base'] and n3['vigencia'] == 'desatualizada'
    for d in novos:
        status, q, msgs = ref.nova(d, banco)
        assert status == 'criada', msgs
    assert q.id == 'cebraspe-2024-orgao-teste-003'
    assert ref.validar(banco)[1] == []


def test_embutir_figura_no_texto_base(cadernos, tmp_path):
    banco = tmp_path / 'referencias'
    d = dict(banca='Cebraspe', formato='certo_errado', ano=2024, orgao='ORGAO TESTE', concurso='Concurso fictício',
             cargo='Cargo', caderno='CAD', item='7', disciplina='fisica', assunto='cinematica', subassuntos=['queda'],
             palavras_chave=['queda'], gabarito='C', gabarito_status='definitivo', url='https://example.test/c.pdf',
             gabarito_url='https://example.test/g.pdf', origem='pesquisa_internet', fonte_descoberta='sintética',
             consulta='2026-11-21', concursos_alvo=['PRF'], operacao_observada='Queda livre.',
             texto_base='Um corpo cai, conforme a figura.\n\nJulgue o item.', enunciado='O corpo acelera.')
    _, q, _ = ref.nova(d, banco)
    with pytest.raises(ref.ErroBanco):
        po.embutir('fig.png', 'ctx', [q.id], banco)
    cad, _ = cadernos
    (banco / 'imagens').mkdir()
    po.renderizar(cad, 1, banco / 'imagens' / 'fig.png', [20, 80, 300, 140], 60, True)
    po.embutir('fig.png', 'ctx', [q.id], banco)
    corpo = ref.localizar([q.id], banco)[0].corpo
    assert '> ![[fig.png]]\n>\n> Julgue o item.' in corpo
    assert ref.validar(banco)[1] == []


def test_prioridades_contadas_e_curada_preservada(tmp_path):
    banco = tmp_path / 'referencias'
    base = dict(banca='Cebraspe', formato='certo_errado', orgao='ORGAO TESTE', concurso='C', cargo='Cargo',
                disciplina='informatica', subassuntos=['smtp'], palavras_chave=['smtp'], gabarito_status='definitivo',
                url='https://example.test/c.pdf', gabarito_url='https://example.test/g.pdf', origem='pesquisa_internet',
                fonte_descoberta='sintética', consulta='2026-11-21', concursos_alvo=['PRF'], operacao_observada='Op.')
    for i, (ano, cad, ass, gab) in enumerate([(2020, 'A', 'correio_eletronico', 'E'), (2020, 'A', 'correio_eletronico', 'C'),
                                              (2022, 'B', 'correio_eletronico', 'C'), (2022, 'B', 'redes', 'C')], 1):
        st, _, msgs = ref.nova(dict(base, ano=ano, caderno=cad, item=str(i), assunto=ass, gabarito=gab,
                                    enunciado=f'Afirmação fictícia número {i}.'), banco)
        assert st == 'criada', msgs
    curada = dict(tipo='prioridade', titulo='Teste — prioridade curada de correio', disciplina='informatica',
                  assunto='correio_eletronico', subassuntos=['smtp'], palavras_chave=['smtp'], concursos_alvo=['PRF'],
                  concurso='PRF', prioridade='baixa', incidencia='nao_medida', evidencias=[],
                  url='https://example.test/e.pdf', fonte_descoberta='Triagem manual', consulta='2026-11-01',
                  corpo='## Avaliação\n\n- Avaliação manual.\n\n## Alta\n\n- Subtema curado.\n\n## Pegadinhas recorrentes\n\n- Pegadinha curada.')
    assert ref.nova(curada, banco)[0] == 'criada'
    dados = dict(rotulos={'informatica/redes': 'redes de computadores'}, concursos={'PRF': dict(
        provas=[['Prova 2020', 2020, ['A']], ['Prova 2022', 2022, ['B']]], orgao='ORGAO TESTE', rotulo='Teste',
        edital='edital-x', nome_edital='edital fictício', fora_do_edital={'informatica/redes': 'fora do programa'})})
    docs, resumo = po.contar('PRF', banco, dados, '2026-11-21')
    prio = {r['assunto']: r['prioridade'] for r in resumo}
    assert prio == {'correio_eletronico': 'alta', 'redes': 'baixa'}
    msgs = po.gravar_prioridades(docs, banco)
    assert any(m.startswith('atualizada (curada)') for m in msgs) and any(m.startswith('criada') for m in msgs)
    _, erros, _ = ref.validar(banco)
    assert erros == []
    q = next(q for q in ref.carregar(banco)[0] if q.tipo == 'prioridade' and q.meta['assunto'] == 'correio_eletronico')
    assert q.meta['prioridade'] == 'alta' and q.meta['titulo'] == 'Teste — prioridade curada de correio'
    assert '- Subtema curado.' in q.corpo and '- Pegadinha curada.' in q.corpo and 'Triagem anterior (curada)' in q.corpo
    # Rodar de novo não muda o arquivo curado nem duplica o gerado.
    antes = q.caminho.read_text(encoding='utf-8')
    po.gravar_prioridades(po.contar('PRF', banco, dados, '2026-11-21')[0], banco)
    assert q.caminho.read_text(encoding='utf-8') == antes
    assert len([x for x in ref.carregar(banco)[0] if x.tipo == 'prioridade']) == 2
