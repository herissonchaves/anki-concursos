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
