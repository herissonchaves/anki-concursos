"""Banco de questões de referência com dados SINTÉTICOS (não são itens reais de prova)."""
import json

import pytest

import referencias as ref

BASE = dict(banca='Cebraspe', formato='certo_errado', ano=2024, orgao='ORGAO TESTE', concurso='Concurso fictício 2024',
            cargo='Cargo fictício', caderno='CAD_01', disciplina='informatica', assunto='correio_eletronico',
            subassuntos=['protocolos', 'smtp'], palavras_chave=['smtp', 'cópia oculta'], gabarito='E',
            gabarito_status='definitivo', url='https://example.test/prova.pdf',
            gabarito_url='https://example.test/gab.pdf', origem='pesquisa_internet',
            fonte_descoberta='Busca sintética', consulta='2026-11-20', concursos_alvo=['PRF'],
            operacao_observada='Troca sintética de funções de protocolos')


def q(item, enunciado, **extra):
    return {**BASE, 'item': item, 'enunciado': enunciado, **extra}


@pytest.fixture
def banco(tmp_path):
    return tmp_path / 'referencias'


def test_nova_cria_arquivo_valido_e_indexa(banco):
    status, questao, msgs = ref.nova(q(7, 'O protocolo SMTP é usado para receber mensagens.'), banco)
    assert status == 'criada', msgs
    assert questao.id == 'cebraspe-2024-orgao-teste-007'
    assert questao.caminho == banco / 'questoes' / 'informatica' / 'correio_eletronico' / f'{questao.id}.md'
    texto = questao.caminho.read_bytes()
    assert b'\r\n' not in texto and not texto.startswith(b'\xef\xbb\xbf')
    meta, _ = ref.ler_documento(texto.decode('utf-8'))
    assert meta['item'] == '7' and meta['ano'] == 2024 and meta['palavras_chave'] == ['smtp', 'cópia oculta']
    n, erros, _ = ref.indexar(banco)
    assert (n, erros) == (1, [])
    assert 'correio_eletronico (1)' in (banco / 'assuntos.md').read_text(encoding='utf-8')


def test_duplicata_e_detectada_por_hash_normalizado(banco):
    ref.nova(q(1, 'Encaminhar   inclui os ANEXOS originais.'), banco)
    status, existente, msgs = ref.nova(q(2, 'encaminhar inclui os anexos originais'), banco)
    assert status == 'duplicada' and existente.id.endswith('-001')


def test_buscar_filtra_por_disciplina_termo_e_corpo(banco):
    ref.nova(q(1, 'Item sobre SMTP e envio.'), banco)
    ref.nova(q(2, 'Item sobre o navegador e cookies.', assunto='navegadores', subassuntos=['cookies'],
               palavras_chave=['cookie'], banca='FGV', formato='multipla_escolha', gabarito='B',
               alternativas={'A': 'um', 'B': 'dois'}), banco)
    assert [r['id'] for r in ref.buscar(banco, disciplina='informatica', termos=['smtp'])] == ['cebraspe-2024-orgao-teste-001']
    assert [r['banca'] for r in ref.buscar(banco, banca='fgv')] == ['FGV']
    assert ref.buscar(banco, termos=['envio']) == []
    assert len(ref.buscar(banco, termos=['envio'], corpo=True)) == 1
    assert len(ref.buscar(banco, formato='multipla_escolha', alvo='prf')) == 1


def test_indice_se_atualiza_quando_um_arquivo_e_apagado(banco):
    _, a, _ = ref.nova(q(1, 'Primeiro item.'), banco)
    ref.nova(q(2, 'Segundo item.'), banco)
    assert len(ref.ler_indice(banco)) == 2
    a.caminho.unlink()
    assert len(ref.ler_indice(banco)) == 1


def test_validacao_aponta_problemas(banco):
    _, questao, _ = ref.nova(q(3, 'Enunciado limpo.'), banco)
    texto = questao.caminho.read_text(encoding='utf-8')
    questao.caminho.write_text(texto.replace('Enunciado limpo.', 'Licenciado para Fulano 123.456.789-00')
                               .replace('gabarito: E', 'gabarito: X'), encoding='utf-8')
    _, erros, _ = ref.validar(banco)
    texto_erros = ' '.join(erros)
    assert 'hash desatualizado' in texto_erros and 'CPF' in texto_erros and 'gabarito' in texto_erros


def test_nova_rejeita_metadados_incompletos(banco):
    dados = q(4, 'Sem disciplina válida.', disciplina='Informática', gabarito_status='definitivo', gabarito_url='nao_localizado')
    status, _, msgs = ref.nova(dados, banco)
    assert status == 'invalida'
    assert any('snake_case' in m for m in msgs) and any('gabarito_url' in m for m in msgs)
    assert not (banco / 'questoes').exists() or not list((banco / 'questoes').rglob('*.md'))


def test_calibracao_e_registro_de_uso(banco):
    _, a, _ = ref.nova(q(5, 'Item com fonte.'), banco)
    _, b, _ = ref.nova(q(6, 'Item de apostila sem fonte.', url='nao_localizado', origem='anexo_usuario',
                         gabarito_status='nao_verificado', gabarito_url='nao_localizado'), banco)
    refs = ref.calibracao(a.id, raiz=banco)
    assert refs[0]['id'] == a.id and refs[0]['item'] == '5' and refs[0]['gabarito_url'].startswith('https://')
    with pytest.raises(ref.ErroBanco):
        ref.calibracao(b.id, raiz=banco)
    assert ref.registrar_uso(a.id, 'PRF/Missao_09_X', ['D01'], banco)
    assert ref.registrar_uso(a.id, 'PRF/Missao_09_X', ['D01', 'D02'], banco)
    assert not ref.registrar_uso(a.id, 'PRF/Missao_09_X', ['D01', 'D02'], banco)
    assert ref.localizar([a.id], banco)[0].meta['usado_em'] == ['PRF/Missao_09_X#D01,D02']
    assert ref.buscar(banco, nao_usadas=True)[0]['id'] == b.id


def test_cli_nova_buscar_mostrar(banco, tmp_path, capsys):
    entrada = tmp_path / 'qs.json'
    entrada.write_text(json.dumps([q(8, 'Item CLI sobre Cco.', texto_base='Texto-base sintético.',
                                     analise='Operação sintética.')], ensure_ascii=False), encoding='utf-8')
    assert ref.main(['--raiz', str(banco), 'nova', str(entrada)]) == 0
    assert ref.main(['--raiz', str(banco), 'buscar', '-t', 'smtp', '--ids']) == 0
    ident = capsys.readouterr().out.strip().splitlines()[-1]
    assert ident == 'cebraspe-2024-orgao-teste-008'
    assert ref.main(['--raiz', str(banco), 'mostrar', ident]) == 0
    saida = capsys.readouterr().out
    assert 'Item CLI sobre Cco.' in saida and 'Texto-base sintético.' in saida and 'Operação sintética' not in saida
    assert ref.main(['--raiz', str(banco), 'validar']) == 0
    assert ref.main(['--raiz', str(banco), 'mostrar', 'inexistente']) == 1


def test_frontmatter_ida_e_volta():
    meta = {'id': 'x-1', 'item': '99', 'ano': 2024, 'consulta': '2026-11-20', 'url': 'https://a.test/b?c=d',
            'concurso': 'Nome: com "aspas", vírgula', 'subassuntos': ['a_b', 'c'], 'palavras_chave': ['com espaço', 'x,y'],
            'usado_em': []}
    lido, corpo = ref.ler_documento(ref.escrever_documento(meta, '## Enunciado\n\ntexto'))
    assert lido == meta and corpo.startswith('## Enunciado')


def test_indice_percebe_edicao_no_mesmo_instante(banco):
    """Edição com o mesmo mtime do índice (mesmo tique do relógio) ainda reindexa."""
    import os
    _, a, _ = ref.nova(q(9, 'Item para registrar uso.'), banco)
    ref.indexar(banco)
    instante = (banco / 'indice.tsv').stat().st_mtime_ns
    ref.registrar_uso(a.id, 'PRF/Missao_10_Y', ['R01'], banco)
    os.utime(a.caminho, ns=(instante, instante))
    assert ref.buscar(banco, nao_usadas=True) == []


def test_vigencia_desatualizada_exige_nota_e_aparece_na_busca(banco, capsys):
    status, _, msgs = ref.nova(q(11, 'Item com regra revogada.', vigencia='desatualizada'), banco)
    assert status == 'invalida' and any('vigencia_nota' in m for m in msgs)
    status, questao, _ = ref.nova(q(12, 'Item com regra revogada.', vigencia='desatualizada',
                                    vigencia_nota='Regra sintética revogada em 2025'), banco)
    assert status == 'criada'
    ref.nova(q(13, 'Item atual.'), banco)
    assert [r['id'] for r in ref.buscar(banco, vigentes=True)] == ['cebraspe-2024-orgao-teste-013']
    assert ref.main(['--raiz', str(banco), 'buscar']) == 0
    assert 'DESATUALIZADA' in capsys.readouterr().out
    assert ref.main(['--raiz', str(banco), 'mostrar', questao.id]) == 0
    assert 'DESATUALIZADA: Regra sintética revogada' in capsys.readouterr().out


def test_rascunho_com_marcador_revisar_e_recusado(banco):
    status, _, msgs = ref.nova(q(14, 'Item importado.', operacao_observada='REVISAR', palavras_chave=['REVISAR']), banco)
    assert status == 'invalida' and any('rascunho' in m for m in msgs)


def test_id_usa_o_concurso_quando_falta_o_orgao(banco):
    _, questao, msgs = ref.nova(q(15, 'Item sem órgão.', orgao='nao_localizado', banca='SOCIESC', ano=2011,
                                  concurso='SOCIESC — Agente de Trânsito — 2011'), banco)
    assert questao is not None, msgs
    assert questao.id == 'sociesc-2011-agente-de-transito-015'


def test_sem_prova_e_busca_com_url(banco):
    _, a, _ = ref.nova(q(16, 'Item com prova.'), banco)
    _, b, _ = ref.nova(q(17, 'Item sem prova.', url='nao_localizado', gabarito_status='nao_verificado',
                         gabarito_url='nao_localizado', origem='anexo_usuario'), banco)
    assert [r['id'] for r in ref.buscar(banco, com_url=True)] == [a.id]
    assert ref.tem_prova(a.id, banco) and not ref.tem_prova(b.id, banco)
    resumo = ref.sem_prova(b.id, raiz=banco)[0]
    assert resumo['id'] == b.id and resumo['origem'] == 'anexo_usuario' and resumo['vigencia'] == 'atual'


def test_importar_extrai_questoes_de_texto(tmp_path):
    import importar_questoes as imp
    texto = (
        'QUESTÕES SEM COMENTÁRIOS\n'
        '01. CEBRASPE – ÓRGÃO FICTÍCIO – 2020:\n'
        'Julgue o item. O item sintético é verdadeiro.\n'
        '02. BANCA X – PREFEITURA DE TESTE – 2021:\n'
        'Assinale a opção correta.\n(A) primeira\n(B) segunda 0123456789ABCDEF0123456789ABCDEF\n(C) terceira\n'
        'Nome Fulano CPF 123.456.789-00\n'
        '01. Certo. 02. B\n'
        'Página | 9\n')
    arq = tmp_path / 'apostila.txt'
    arq.write_text(texto, encoding='utf-8')
    itens = imp.extrair(arq, disciplina='fisica', assunto='dinamica')
    assert [i['formato'] for i in itens] == ['certo_errado', 'multipla_escolha']
    assert [i['gabarito'] for i in itens] == ['C', 'B']
    assert itens[1]['alternativas'] == {'A': 'primeira', 'B': 'segunda', 'C': 'terceira'}
    assert itens[0]['ano'] == 2020 and itens[1]['orgao'] == 'Prefeitura de Teste'
    assert itens[0]['operacao_observada'] == 'REVISAR' and itens[0]['origem'] == 'anexo_usuario'
    assert 'CPF' not in json.dumps(itens, ensure_ascii=False)


DOC = dict(disciplina='transito', assunto='motorista_profissional', subassuntos=['descanso'],
           palavras_chave=['67-c'], concursos_alvo=['PRF'], url='https://example.test/lei',
           fonte_descoberta='Fonte sintética', consulta='2026-11-21')


def test_conteudo_noticia_edital_prioridade_criados_validados_e_indexados(banco):
    conteudo = dict(DOC, tipo='conteudo', titulo='Lei sintética, art. 1', norma='Lei sintética', dispositivos=['art. 1'],
                    situacao='vigente', verificado_em=_hoje(), corpo='## Art. 1\n\nTexto sintético verificado.')
    noticia = dict(DOC, tipo='noticia', titulo='Decisão sintética', data_evento='2026-01-02', status='confirmada',
                   efeito='Muda o gabarito sintético', normas_afetadas=['Lei sintética, art. 1'], corpo='## Resumo\n\nFato sintético.')
    edital = dict(DOC, tipo='edital', titulo='Edital sintético 2026', disciplina='geral', assunto='concurso_ficticio',
                  orgao='Órgão fictício', banca='Banca fictícia', cargo='Cargo fictício', ano=2026, edicao='Edital nº 1/2026',
                  status='historico', corpo='## Legislação de Trânsito\n\n1 Lei sintética.\n\n## Informática\n\n1 Redes.')
    prioridade = dict(DOC, tipo='prioridade', titulo='PRF — motorista profissional (sintético)', concurso='PRF',
                      prioridade='alta', incidencia='nao_medida', evidencias=[], corpo='## Subtemas\n\n- Alta: descanso.')
    ids = {}
    for d in (conteudo, noticia, edital, prioridade):
        status, q, msgs = ref.nova(dict(d), banco)
        assert status == 'criada', msgs
        ids[d['tipo']] = q.id
    assert (banco / 'conteudos' / 'transito' / 'motorista_profissional' / f'{ids["conteudo"]}.md').exists()
    assert (banco / 'editais' / 'concurso_ficticio' / f'{ids["edital"]}.md').exists()
    assert (banco / 'prioridades' / 'prf' / 'transito' / f'{ids["prioridade"]}.md').exists()
    n, erros, _ = ref.indexar(banco)
    assert (n, erros) == (4, [])
    assert [r['id'] for r in ref.buscar(banco, tipo='conteudo', recentes=90)] == [ids['conteudo']]
    assert [r['tipo'] for r in ref.buscar(banco, termos=['67-c'], tipo='noticia')] == ['noticia']
    assert 'tipos:' in (banco / 'assuntos.md').read_text(encoding='utf-8')
    url, trecho = ref.fonte(ids['conteudo'], banco)
    assert url == 'https://example.test/lei' and 'verificado em' in trecho and ids['conteudo'] in trecho
    _, trecho_art = ref.fonte(ids['conteudo'] + '#Art. 1', banco)
    assert trecho_art.startswith('Lei sintética — Art. 1 — verificado em')
    with pytest.raises(ref.ErroBanco):
        ref.fonte(ids['conteudo'] + '#Art. 99', banco)
    assert ref.nova(dict(conteudo), banco)[0] == 'duplicada'
    with pytest.raises(ref.ErroBanco):
        ref.calibracao(ids['conteudo'], raiz=banco)


def test_mostrar_secao_de_edital(banco, capsys):
    edital = dict(DOC, tipo='edital', titulo='Edital sintético B', disciplina='geral', assunto='concurso_b', orgao='Órgão',
                  banca='Banca', cargo='Cargo', ano=2025, edicao='Edital nº 2', status='vigente',
                  corpo='## Legislação de Trânsito\n\nItem de trânsito.\n\n## Informática\n\nItem de informática.')
    _, q, _ = ref.nova(edital, banco)
    assert ref.main(['--raiz', str(banco), 'mostrar', q.id, '--secao', 'legislacao de transito']) == 0
    saida = capsys.readouterr().out
    assert 'Item de trânsito.' in saida and 'Item de informática.' not in saida


def test_documento_invalido_aponta_problemas(banco):
    ruim = dict(DOC, tipo='conteudo', titulo='Sem seção', norma='Lei', dispositivos=['art. 1'], situacao='em_vigor',
                verificado_em='21/11/2026', corpo='Texto sem seção.')
    status, _, msgs = ref.nova(ruim, banco)
    assert status == 'invalida'
    texto = ' '.join(msgs)
    assert 'situacao' in texto and 'verificado_em' in texto and 'seção' in texto


def _hoje():
    import datetime
    return datetime.date.today().isoformat()


def test_imagem_embutida_precisa_existir_em_imagens(banco):
    status, questao, msgs = ref.nova(q(9, 'Na figura, o ícone indicado abre um novo documento.\n\n![[fig-teste.png]]'), banco)
    assert status == 'criada', msgs
    assert ref.imagens_citadas(questao.corpo) == ['fig-teste.png']
    _, erros, _ = ref.validar(banco)
    assert any('fig-teste.png' in e for e in erros)
    (banco / 'imagens').mkdir()
    (banco / 'imagens' / 'fig-teste.png').write_bytes(b'\x89PNG\r\n\x1a\n')
    _, erros, _ = ref.validar(banco)
    assert erros == []


def test_recorte_de_assuntos_e_barato():
    arvore = ('# Assuntos\n\nGerado. Total: 3 itens.\n\n- **informatica** (2)\n  - correio (2): smtp 1\n'
              '- **transito** (1)\n  - cargas (1): peso 1\n')
    curto = ref.recortar_assuntos(arvore)
    assert '- **transito** (1)' in curto and 'correio' not in curto
    so = ref.recortar_assuntos(arvore, ['transito'])
    assert '  - cargas (1)' in so and 'informatica' not in so
    assert ref.recortar_assuntos(arvore, completo=True) == arvore
