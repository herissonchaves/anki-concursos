"""Avisos não bloqueantes do finalizar_lote.py: banco consultado e duplicatas na coleção viva."""
from hashlib import sha256

from finalizar_lote import avisos
from test_colecao_viva import fazer_colecao


def lote(tmp_path, selecao, frente):
    dados = tmp_path / 'PRF_Teste' / 'lote'
    (dados / 'relatorios').mkdir(parents=True)
    (dados / 'relatorios' / 'selecao_e_fontes.txt').write_text(selecao, encoding='utf-8')
    (dados / 'anki_certo_errado.tsv').write_text(f'{frente}\t✅ Certo<br><br>Verso.\tPRF\n', encoding='utf-8')
    (dados / 'anki_cloze.tsv').write_text('', encoding='utf-8')
    return dados.parent, dados


def test_avisa_banco_nao_registrado_e_duplicata(tmp_path):
    db = fazer_colecao(tmp_path)
    antes = sha256(db.read_bytes()).hexdigest()
    pasta, dados = lote(tmp_path, 'Fontes: planalto.gov.br\n', 'Parada é a imobilização para embarque')
    msgs = avisos(pasta, dados, str(db))
    assert any(m.startswith('banco:') for m in msgs)
    assert any(m.startswith('duplicatas: 1 ') for m in msgs)
    assert 'anki:100' in (pasta / 'duplicatas_colecao.txt').read_text(encoding='utf-8')
    assert sha256(db.read_bytes()).hexdigest() == antes


def test_sem_avisos_quando_banco_registrado_e_frente_nova(tmp_path, capsys):
    db = fazer_colecao(tmp_path)
    pasta, dados = lote(tmp_path, '- Banco consultado: assuntos -d transito; buscar -a parada\n',
                        'O acostamento não pode ser usado para ultrapassar outro veículo em rodovia federal.')
    assert avisos(pasta, dados, str(db)) == []
    assert 'nenhuma frente parecida' in capsys.readouterr().out
    assert not (pasta / 'duplicatas_colecao.txt').exists()


def test_colecao_ausente_so_avisa(tmp_path):
    pasta, dados = lote(tmp_path, 'Banco consultado: buscar -d transito\n', 'Frente qualquer de teste.')
    msgs = avisos(pasta, dados, str(tmp_path / 'nao_existe.anki2'))
    assert msgs and msgs[0].startswith('duplicatas: coleção não lida')
