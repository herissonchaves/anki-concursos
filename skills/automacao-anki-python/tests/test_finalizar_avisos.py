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


def test_finalizar_valida_a_pasta_e_entrega_so_tsv_2_30(tmp_path, monkeypatch, capsys):
    """Sem ZIP, APKG nem prévia: as barreiras rodam na pasta lote/ e o histórico ganha a linha do lote."""
    import finalizar_lote
    from test_montar_lote import gerar_resolvido
    pasta = tmp_path / 'PRF_Fixture'
    gerar_resolvido(pasta)
    (pasta / 'lote' / 'relatorios' / 'selecao_e_fontes.txt').write_text('Banco consultado: fixture\n', encoding='utf-8')
    historico = tmp_path / 'historico_lotes.tsv'
    monkeypatch.setattr(finalizar_lote, 'HISTORICO', historico)
    codigo = finalizar_lote.main([str(pasta), '--baralho', 'Fixture', '--colecao', str(tmp_path / 'nao_existe.anki2')])
    saida = capsys.readouterr().out
    assert codigo == 0, saida
    assert 'TSV C/E:' in saida and 'TSV Cloze:' in saida
    assert not list(pasta.glob('*.zip')) and not list(pasta.glob('*.apkg'))
    assert not (pasta / 'previa_cards.html').exists()
    assert 'PRF_Fixture\tFixture\t2\t2\t1' in historico.read_text(encoding='utf-8')


def test_finalizar_recusa_relatorio_obrigatorio_ausente(tmp_path, capsys):
    import finalizar_lote
    from test_montar_lote import gerar_resolvido
    pasta = tmp_path / 'PRF_Fixture'
    gerar_resolvido(pasta)
    assert finalizar_lote.main([str(pasta), '--baralho', 'Fixture']) == 1
    assert 'selecao_e_fontes.txt' in capsys.readouterr().out


def test_colecao_ausente_so_avisa(tmp_path):
    pasta, dados = lote(tmp_path, 'Banco consultado: buscar -d transito\n', 'Frente qualquer de teste.')
    msgs = avisos(pasta, dados, str(tmp_path / 'nao_existe.anki2'))
    assert msgs and msgs[0].startswith('duplicatas: coleção não lida')
