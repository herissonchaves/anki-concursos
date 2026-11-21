"""Leitor da coleção viva: consulta em cópia e nunca altera o arquivo original."""
from hashlib import sha256
import sqlite3
import time

from colecao_anki import Colecao, buscar, desempenho, dificeis, duplicatas, lacunas, main

CAMPOS_INDICE = ('id tipo titulo disciplina assunto subassuntos banca formato ano gabarito status orgao '
                 'cargo alvos usos palavras arquivo vigencia tem_url data').split()


def fazer_colecao(pasta):
    db = pasta / 'collection.anki2'
    agora = int(time.time())
    with sqlite3.connect(db) as c:
        c.executescript('''
            CREATE TABLE col (crt INTEGER);
            CREATE TABLE decks (id INTEGER, name TEXT);
            CREATE TABLE notetypes (id INTEGER, name TEXT);
            CREATE TABLE notes (id INTEGER, mid INTEGER, flds TEXT, tags TEXT);
            CREATE TABLE cards (id INTEGER, nid INTEGER, did INTEGER, odid INTEGER, queue INTEGER,
                                due INTEGER, ivl INTEGER, lapses INTEGER, reps INTEGER);
            CREATE TABLE revlog (id INTEGER, cid INTEGER, ease INTEGER, type INTEGER, time INTEGER);
        ''')
        c.execute('INSERT INTO col VALUES (?)', (agora - 100 * 86400,))
        c.executemany('INSERT INTO decks VALUES (?,?)', [(1, 'Legislação de Trânsito'), (2, 'Direito Penal')])
        c.execute("INSERT INTO notetypes VALUES (10, 'Básico')")
        c.executemany('INSERT INTO notes VALUES (?,?,?,?)', [
            (100, 10, 'Parada é a imobilização para <b>embarque</b>\x1fVerso', ' PRF CTB '),
            (200, 10, 'O tacógrafo registra o tempo de direção\x1fVerso', ' PRF '),
            (300, 10, 'Princípio da legalidade\x1fVerso', ' leech '),
        ])
        c.executemany('INSERT INTO cards VALUES (?,?,?,?,?,?,?,?,?)', [
            (1, 100, 1, 0, 2, 99, 5, 0, 4),
            (2, 200, 1, 0, 0, 0, 0, 0, 0),
            (3, 300, 2, 0, 2, 101, 3, 4, 12),
        ])
        ms = agora * 1000
        c.executemany('INSERT INTO revlog VALUES (?,?,?,?,?)',
                      [(ms - i * 1000, 3, 1 if i < 3 else 3, 1, 8000) for i in range(12)])
    return db


def fazer_banco(raiz):
    pasta = raiz / 'referencias'
    pasta.mkdir()
    linhas = [
        {'id': 'prio-a', 'tipo': 'prioridade', 'titulo': 'Parada', 'disciplina': 'transito', 'assunto': 'parada',
         'subassuntos': 'parada_estacionamento', 'status': 'alta', 'alvos': 'PRF', 'palavras': 'prf;prioridade'},
        {'id': 'cont-a', 'tipo': 'conteudo', 'titulo': 'Anexo I', 'disciplina': 'transito', 'assunto': 'parada',
         'subassuntos': '', 'status': 'vigente', 'alvos': 'PRF', 'palavras': 'embarque;imobilização'},
        {'id': 'prio-b', 'tipo': 'prioridade', 'titulo': 'Crimes', 'disciplina': 'transito', 'assunto': 'crimes',
         'subassuntos': 'homicidio_culposo', 'status': 'media', 'alvos': 'PRF', 'palavras': 'prf'},
        {'id': 'prio-c', 'tipo': 'prioridade', 'titulo': 'Baixa', 'disciplina': 'transito', 'assunto': 'x',
         'subassuntos': 'zzzz', 'status': 'baixa', 'alvos': 'PRF', 'palavras': ''},
    ]
    texto = '\t'.join(CAMPOS_INDICE) + '\n' + ''.join(
        '\t'.join(l.get(k, '') for k in CAMPOS_INDICE) + '\n' for l in linhas)
    (pasta / 'indice.tsv').write_text(texto, encoding='utf-8')


def test_consultas_nao_alteram_original(tmp_path):
    db = fazer_colecao(tmp_path)
    antes = sha256(db.read_bytes()).hexdigest()
    with Colecao(db) as col:
        assert [n['id'] for n in buscar(col, ['EMBARQUE'], 'legislacao de transito')] == [100]
        assert [n['id'] for n in dificeis(col, min_lapsos=2)] == [300]
        st = desempenho(col, 30)
        assert st['Direito Penal']['acerto'] == 75 and st['Legislação de Trânsito']['novos'] == 1
        try:
            col.db.execute('DELETE FROM notes')
            raise AssertionError('a cópia deveria recusar escrita')
        except sqlite3.OperationalError:
            pass
    assert sha256(db.read_bytes()).hexdigest() == antes


def test_lacunas_cruza_prioridades_com_notas(tmp_path):
    db = fazer_colecao(tmp_path)
    fazer_banco(tmp_path)
    with Colecao(db) as col:
        res = {r['id']: r for r in lacunas(col, 'PRF', raiz=tmp_path, min_notas=1)}
    assert set(res) == {'prio-a', 'prio-b'}
    assert res['prio-a']['notas'] == 1 and res['prio-a']['situacao'] == 'coberto'
    assert res['prio-b']['situacao'] == 'sem_notas'


def test_duplicatas_e_cli(tmp_path, capsys):
    db = fazer_colecao(tmp_path)
    tsv = tmp_path / 'novo.tsv'
    tsv.write_text('Parada é a imobilização para embarque\tC\tPRF\n', encoding='utf-8')
    with Colecao(db) as col:
        r = duplicatas(col, tsv)
    assert r['possiveis_duplicatas'][0]['comparado_com'] == 'anki:100'
    assert main(['--colecao', str(db), 'resumo']) == 0
    assert 'Notas: 3' in capsys.readouterr().out
