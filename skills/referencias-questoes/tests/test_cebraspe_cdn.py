"""cebraspe_cdn.py: lista, baixa e busca itens sem rede (dados SINTÉTICOS)."""
import pytest

import cebraspe_cdn as cdn

EVENTO = {
    'eventoURL': 'PF_18',
    'arquivosGabarito': [
        {'nomeArquivo': 'GAB_DEFINITIVO_408_X013.PDF', 'descricaoArquivo': 'GABARITO DEFINITIVO - CARGO 13', 'dataArquivo': '11/10/2018'},
        {'nomeArquivo': 'MATRIZ_408_X013.PDF', 'descricaoArquivo': 'PROVA OBJETIVA - CARGO 13', 'dataArquivo': '18/09/2018'},
        {'nomeArquivo': 'MALOTE01_ORAL.PDF', 'descricaoArquivo': 'PROVA ORAL', 'dataArquivo': '04/02/2024'},
    ],
    'arquivosEdital': [{'nomeArquivo': 'ED_1.PDF', 'descricaoArquivo': 'EDITAL DE ABERTURA', 'dataArquivo': '01/08/2018'}],
}


def test_lista_e_filtra_arquivos_do_evento():
    arquivos = cdn.arquivos_do_evento(EVENTO)
    assert len(arquivos) == 4
    assert arquivos[0]['url'] == 'https://cdn.cebraspe.org.br/concursos/PF_18/arquivos/GAB_DEFINITIVO_408_X013.PDF'
    assert [a['arquivo'] for a in cdn.filtrar(arquivos, 'definitivo|objetiva')] == ['GAB_DEFINITIVO_408_X013.PDF',
                                                                                  'MATRIZ_408_X013.PDF']


def test_url_de_aceita_pasta_arquivo_e_recusa_http():
    assert cdn.url_de('PF_18/A.PDF') == 'https://cdn.cebraspe.org.br/concursos/PF_18/arquivos/A.PDF'
    with pytest.raises(cdn.ErroCdn):
        cdn.url_de('sem_barra')
    with pytest.raises(cdn.ErroCdn):
        cdn._abrir('http://exemplo.test/a.pdf')


def test_baixar_grava_so_pdf_e_nao_repete(tmp_path):
    chamadas = []

    def falso(url):
        chamadas.append(url)
        return b'%PDF-1.4 sintetico' if url.endswith('.PDF') else b'<html>pagina</html>'

    salvos = cdn.baixar(['PF_18/A.PDF'], tmp_path / 'novo', abrir=falso)
    assert salvos[0].read_bytes().startswith(b'%PDF') and len(chamadas) == 1
    cdn.baixar(['PF_18/A.PDF'], tmp_path / 'novo', abrir=falso)
    assert len(chamadas) == 1  # já baixado: não busca de novo
    with pytest.raises(cdn.ErroCdn):
        cdn.baixar(['https://cdn.cebraspe.org.br/concursos/PF_18/'], tmp_path / 'outro', abrir=falso)


def test_buscar_itens_devolve_so_os_do_tema_com_o_comando():
    texto = ('Acerca dos atos administrativos, julgue os itens a seguir.\n'
             '25 Sob o fundamento da ilegalidade, a administração deverá revogar o ato sintético.\n'
             '26 A autotutela permite ao Judiciário intervir no ato sintético.\n'
             'Acerca de licitações, julgue o item.\n'
             '27 A licitação sintética é dispensável.\n')
    achados = cdn.buscar_itens(texto, r'revogar|autotutela')
    assert [a.split()[0] for a in achados] == ['25', '26']
    assert 'julgue os itens a seguir' in achados[0]
    assert cdn.buscar_itens(texto, r'inexistente') == []
