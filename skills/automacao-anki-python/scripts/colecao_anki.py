#!/usr/bin/env python3
"""Consulta SOMENTE LEITURA da coleção viva do Anki deste computador.

Copia `collection.anki2` (e o `-wal`, se houver) para uma pasta temporária e lê
a cópia com `PRAGMA query_only`; o arquivo original nunca é aberto pelo SQLite.
Funciona com o Anki aberto (mostra o último estado gravado em disco).

Comandos (perfil padrão `concursos`; `--colecao CAMINHO` usa outro arquivo):
  resumo                         baralhos, novos, suspensos, lapsos, tags mais usadas
  buscar TERMO [TERMO…]          notas com todos os termos (sem acento/caixa)
  listar [--tag T] [--saida f]   despejar notas (id, baralho, lapsos, tags, campos)
  dificeis [--min-lapsos 2]      notas com mais lapsos ou tag leech
  desempenho [--dias 30]         por disciplina: vencidos, acerto, segundos/revisão
  duplicatas ARQ.tsv -o f.json   frentes do TSV parecidas com notas da coleção
  lacunas [--alvo PRF]           prioridades Alta/Média do banco referencias/ × notas da coleção

Exemplo (na raiz do repositório):
  uv run --no-project python -I -X utf8 skills/automacao-anki-python/scripts/colecao_anki.py buscar estacionamento --baralho "Legislação de Trânsito"
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anki_utils import MAX_SQLITE_UNCOMPRESSED, decompress_database, normalized, plain, register_read_collations  # noqa: E402

RAIZ = Path(__file__).resolve().parents[3]
PERFIL_PADRAO = 'concursos'
GENERICAS = {'prf', 'pf', 'prioridade', 'o que mais cai', 'triagem', 'cebraspe', 'ctb', 'edital', 'programa'}


def anki_base() -> Path:
    if sys.platform.startswith('win'):
        return Path(os.environ.get('APPDATA', Path.home() / 'AppData/Roaming')) / 'Anki2'
    if sys.platform == 'darwin':
        return Path.home() / 'Library/Application Support/Anki2'
    return Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'Anki2'


def find_collection(perfil: str | None = PERFIL_PADRAO, caminho: str | Path | None = None) -> Path:
    if caminho:
        p = Path(caminho)
        if not p.is_file():
            raise SystemExit(f'ERRO: coleção não encontrada: {p}')
        return p
    p = anki_base() / (perfil or PERFIL_PADRAO) / 'collection.anki2'
    if not p.is_file():
        perfis = sorted(x.parent.name for x in anki_base().glob('*/collection.anki2'))
        raise SystemExit(f'ERRO: perfil {perfil!r} sem collection.anki2 em {anki_base()}. Perfis: {perfis}')
    return p


def extrair_colpkg(pacote: Path, destino: Path) -> None:
    """Grava em `destino` o banco SQLite de um backup .colpkg (anki21b descomprimido ou anki2)."""
    import zipfile
    with zipfile.ZipFile(pacote) as z:
        nomes = set(z.namelist())
        membro = next((m for m in ('collection.anki21b', 'collection.anki21', 'collection.anki2') if m in nomes), None)
        if membro is None:
            raise SystemExit(f'ERRO: {pacote} sem banco do Anki')
        if z.getinfo(membro).file_size > MAX_SQLITE_UNCOMPRESSED:
            raise SystemExit('ERRO: banco excede o limite de segurança')
        with z.open(membro) as origem:
            if membro.endswith('21b'):
                decompress_database(origem, destino)
            else:
                with destino.open('wb') as saida:
                    shutil.copyfileobj(origem, saida, length=1024 * 1024)


def tem_tag(tags: str, alvo: str) -> bool:
    """Como no Anki: a tag casa com ela mesma e com as filhas (Direito_Penal casa Direito_Penal::Principios)."""
    alvo = alvo.casefold().rstrip(':')
    return any(t == alvo or t.startswith(alvo + '::') for t in tags.casefold().split())


class Colecao:
    """Cópia temporária da coleção, aberta só para consulta."""

    def __init__(self, src: Path):
        self.src = Path(src)
        self.tmp = tempfile.TemporaryDirectory(prefix='anki_ro_')
        dst = Path(self.tmp.name) / 'collection.anki2'
        if self.src.suffix.lower() == '.colpkg':  # 2.36: backup .colpkg também serve de coleção de consulta
            extrair_colpkg(self.src, dst)
        else:
            shutil.copyfile(self.src, dst)
            wal = Path(str(self.src) + '-wal')
            if wal.is_file():
                shutil.copyfile(wal, str(dst) + '-wal')
        self.db = sqlite3.connect(dst)
        self.db.execute('PRAGMA query_only = ON')
        register_read_collations(self.db)
        tabelas = {r[0] for r in self.db.execute("select name from sqlite_master where type='table'")}
        if 'decks' in tabelas:
            self.decks = {d: n.replace('\x1f', '::') for d, n in self.db.execute('select id, name from decks')}
            self.models = dict(self.db.execute('select id, name from notetypes'))
        else:
            decks_j, models_j = self.db.execute('select decks, models from col').fetchone()
            self.decks = {int(k): v['name'] for k, v in json.loads(decks_j).items()}
            self.models = {int(k): v['name'] for k, v in json.loads(models_j).items()}

    def close(self):
        self.db.close()
        self.tmp.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def deck_ids(self, baralho: str | None):
        if not baralho:
            return None
        b = normalized(baralho)
        ids = {d for d, n in self.decks.items() if normalized(n) == b or normalized(n.split('::')[0]) == b}
        if not ids:
            raise SystemExit(f'ERRO: baralho {baralho!r} não encontrado. Baralhos: {sorted(self.decks.values())}')
        return ids

    def notes(self, baralho: str | None = None):
        ids = self.deck_ids(baralho)
        q = ('select n.id, n.mid, n.flds, n.tags, min(coalesce(nullif(c.odid, 0), c.did)), max(c.lapses), '
             'sum(c.reps), min(c.queue), max(c.ivl) from notes n join cards c on c.nid = n.id group by n.id')
        for nid, mid, flds, tags, did, lapses, reps, queue, ivl in self.db.execute(q):
            if ids is not None and did not in ids:
                continue
            campos = flds.split('\x1f')
            yield {'id': nid, 'modelo': self.models.get(mid, str(mid)), 'campos': campos,
                   'texto': normalized(' '.join(campos)), 'tags': tags.strip(),
                   'baralho': self.decks.get(did, str(did)), 'lapsos': lapses or 0, 'revisoes': reps or 0,
                   'suspenso': queue == -1, 'intervalo': ivl or 0}


def buscar(col: Colecao, termos, baralho=None):
    termos = [normalized(t) for t in termos if normalized(t)]
    if not termos:
        raise SystemExit('ERRO: informe ao menos um termo.')
    return [n for n in col.notes(baralho) if all(t in n['texto'] for t in termos)]


def dificeis(col: Colecao, baralho=None, min_lapsos=2):
    itens = [n for n in col.notes(baralho) if n['lapsos'] >= min_lapsos or 'leech' in n['tags'].lower().split()]
    return sorted(itens, key=lambda n: (-n['lapsos'], n['intervalo']))


def desempenho(col: Colecao, dias: int = 30, agora: float | None = None) -> dict:
    """Por baralho de topo: cartões, novos, suspensos, vencidos, revisões e acerto no período."""
    agora = time.time() if agora is None else agora
    agora_ms = int(agora * 1000)
    crt = col.db.execute('select crt from col').fetchone()[0]
    hoje = int((agora - crt) // 86400)
    topo = {d: n.split('::')[0] for d, n in col.decks.items()}
    st: dict[str, dict] = {}

    def s(did):
        return st.setdefault(topo.get(did, str(did)), {
            'cartoes': 0, 'novos': 0, 'suspensos': 0, 'vencidos': 0, 'vence_7d': 0,
            'revisoes': 0, 'rev_aprendidos': 0, 'novamente': 0, 'tempo_ms': 0})

    for did, odid, queue, due in col.db.execute('select did, odid, queue, due from cards'):
        d = s(odid or did)
        d['cartoes'] += 1
        if queue == 0:
            d['novos'] += 1
        elif queue < 0:
            d['suspensos'] += 1
        elif queue == 1:
            d['vencidos'] += 1
        elif queue in (2, 3):
            if due <= hoje:
                d['vencidos'] += 1
            elif due <= hoje + 7:
                d['vence_7d'] += 1
    q = ('select r.ease, r.type, r.time, c.did, c.odid from revlog r join cards c on c.id = r.cid '
         'where r.id > ?')
    for ease, rtype, tms, did, odid in col.db.execute(q, (agora_ms - dias * 86_400_000,)):
        if rtype not in (0, 1, 2) or ease == 0:
            continue
        d = s(odid or did)
        d['revisoes'] += 1
        d['tempo_ms'] += min(tms or 0, 60_000)
        if rtype == 1:
            d['rev_aprendidos'] += 1
            d['novamente'] += ease == 1
    for d in st.values():
        d['acerto'] = round(100 * (1 - d['novamente'] / d['rev_aprendidos'])) if d['rev_aprendidos'] >= 10 else None
        d['seg_por_revisao'] = round(d['tempo_ms'] / d['revisoes'] / 1000, 1) if d['revisoes'] else None
    return st


def prioridades_do_banco(alvo: str = 'PRF', raiz: Path = RAIZ):
    """Prioridades Alta/Média de referencias/indice.tsv com os termos do mesmo assunto."""
    indice = Path(raiz) / 'referencias' / 'indice.tsv'
    if not indice.is_file():
        return []
    with indice.open(encoding='utf-8', newline='') as f:
        linhas = list(csv.DictReader(f, delimiter='\t'))
    termos: dict[tuple, set] = {}
    for l in linhas:
        chave = (l['disciplina'], l['assunto'])
        bruto = l['palavras'].split(';') + l['subassuntos'].replace('_', ' ').split(';')
        termos.setdefault(chave, set()).update(
            t for t in (normalized(x) for x in bruto) if len(t) >= 4 and t not in GENERICAS)
    alvo = alvo.upper()
    saida = []
    for l in linhas:
        if l['tipo'] != 'prioridade' or l['status'] not in ('alta', 'media'):
            continue
        if alvo not in l['alvos'].upper().split(';'):
            continue
        saida.append({'id': l['id'], 'titulo': l['titulo'], 'prioridade': l['status'],
                      'disciplina': l['disciplina'], 'assunto': l['assunto'],
                      'termos': sorted(termos.get((l['disciplina'], l['assunto']), ()))})
    return sorted(saida, key=lambda p: (p['prioridade'] != 'alta', p['disciplina'], p['assunto']))


def baralhos_por_disciplina(raiz: Path = RAIZ) -> dict[str, list[str]]:
    """id da disciplina -> nomes de baralho aceitos (`baralhos` de disciplinas.json, ou o rótulo)."""
    arq = Path(raiz) / 'skills' / 'perfil-carreiras-policiais' / 'references' / 'disciplinas.json'
    if not arq.is_file():
        return {}
    dados = json.loads(arq.read_text(encoding='utf-8'))
    return {s['id']: s.get('baralhos') or [s['label']] for s in dados.get('subjects', [])}


def _tem_termo(texto: str, termo: str) -> bool:
    return f' {termo} ' in f' {texto} '  # palavra ou expressão inteira, não pedaço de palavra


def lacunas(col: Colecao, alvo: str = 'PRF', raiz: Path = RAIZ, min_notas: int = 3, max_freq: float = 0.3):
    """Cruza prioridades do banco com a coleção (casamento de palavras: indício, não prova).

    Cada disciplina só é comparada com o(s) próprio(s) baralho(s) (`baralhos` em disciplinas.json);
    disciplina sem baralho na coleção fica `sem_baralho`. Termos presentes em mais de `max_freq` das
    notas do baralho (palavras comuns como "que", "isso") são descartados.
    """
    mapa = baralhos_por_disciplina(raiz)
    topo = {normalized(n.split('::')[0]) for n in col.decks.values()}
    notas = list(col.notes())
    res = []
    for p in prioridades_do_banco(alvo, raiz):
        nomes = {normalized(b) for b in mapa.get(p['disciplina'], [])}
        do_baralho = [n for n in notas if normalized(n['baralho'].split('::')[0]) in nomes]
        if not (nomes & topo):
            res.append({**p, 'notas': 0, 'lapsos': 0, 'termos': [], 'situacao': 'sem_baralho'})
            continue
        termos = [t for t in p['termos']
                  if sum(_tem_termo(n['texto'], t) for n in do_baralho) <= max_freq * max(len(do_baralho), 1)]
        achadas = [n for n in do_baralho if any(_tem_termo(n['texto'], t) for t in termos)]
        lap = sum(n['lapsos'] for n in achadas)
        situacao = ('sem_notas' if not achadas else 'poucas_notas' if len(achadas) < min_notas
                    else 'muitos_lapsos' if lap >= 2 * len(achadas) else 'coberto')
        res.append({**p, 'notas': len(achadas), 'lapsos': lap, 'termos': termos[:12], 'situacao': situacao})
    ordem = {'sem_baralho': 0, 'sem_notas': 1, 'poucas_notas': 2, 'muitos_lapsos': 3, 'coberto': 4}
    return sorted(res, key=lambda r: (ordem[r['situacao']], r['prioridade'] != 'alta', r['disciplina']))


def duplicatas(col: Colecao, tsv: Path, limiar=88.0, limite=100):
    from detectar_duplicatas import find_duplicates, fronts_tsv
    antigos = [(str(n['id']), plain(n['campos'][0])) for n in col.notes()]
    return {'novos_tsv': str(tsv), 'notas_colecao': len(antigos), 'limiar': limiar,
            'possiveis_duplicatas': find_duplicates(list(fronts_tsv(tsv)), antigos, limiar, limite),
            'alerta': 'Similaridade de texto não prova redundância: compare o que a frente exige lembrar ou decidir.'}


def _curto(n, campo=0, tam=300):
    return plain(n['campos'][campo])[:tam] if len(n['campos']) > campo else ''


def main(argv=None):
    p = argparse.ArgumentParser(description='Consulta somente leitura da coleção viva do Anki')
    p.add_argument('--perfil', default=PERFIL_PADRAO)
    p.add_argument('--colecao', help='collection.anki2 ou backup .colpkg (padrão: perfil do Anki deste PC)')
    sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('resumo')
    b = sub.add_parser('buscar'); b.add_argument('termos', nargs='+'); b.add_argument('--baralho'); b.add_argument('-n', '--limite', type=int, default=20)
    l = sub.add_parser('listar'); l.add_argument('--baralho'); l.add_argument('--tag'); l.add_argument('--saida', type=Path); l.add_argument('-n', '--limite', type=int, default=30)
    d = sub.add_parser('dificeis'); d.add_argument('--baralho'); d.add_argument('--min-lapsos', type=int, default=2); d.add_argument('-n', '--limite', type=int, default=30)
    de = sub.add_parser('desempenho'); de.add_argument('--dias', type=int, default=30)
    du = sub.add_parser('duplicatas'); du.add_argument('tsv', type=Path); du.add_argument('-o', '--saida', type=Path, required=True); du.add_argument('--limiar', type=float, default=88.0)
    la = sub.add_parser('lacunas'); la.add_argument('--alvo', default='PRF'); la.add_argument('--min-notas', type=int, default=3)
    a = p.parse_args(argv)

    with Colecao(find_collection(a.perfil, a.colecao)) as col:
        print(f'Coleção: {col.src} (cópia temporária, somente leitura)')
        if a.cmd == 'resumo':
            db = col.db
            n_notas, n_cards = db.execute('select (select count(*) from notes), (select count(*) from cards)').fetchone()
            print(f'Notas: {n_notas} | Cartões: {n_cards}\n\nBaralho | cartões | novos | suspensos | com lapsos | lapsos')
            rows = db.execute('select coalesce(nullif(odid, 0), did), count(*), sum(queue=0), sum(queue=-1), '
                              'sum(lapses>0), sum(lapses) from cards group by 1').fetchall()
            for did, n, novos, susp, cl, lap in sorted(rows, key=lambda r: col.decks.get(r[0], '')):
                print(f'{col.decks.get(did, did)} | {n} | {novos} | {susp} | {cl} | {lap}')
            tags: dict[str, int] = {}
            for (t,) in db.execute('select tags from notes'):
                for x in t.split():
                    tags[x] = tags.get(x, 0) + 1
            print('\nTags mais usadas:', ', '.join(f'{k} ({v})' for k, v in sorted(tags.items(), key=lambda kv: -kv[1])[:30]))
        elif a.cmd == 'buscar':
            achados = buscar(col, a.termos, a.baralho)
            print(f'{len(achados)} nota(s) com: {", ".join(a.termos)}')
            for n in achados[:a.limite]:
                print(f'[{n["id"]}] {n["baralho"]} | lapsos {n["lapsos"]} | {n["tags"]}\n  F: {_curto(n)}\n  V: {_curto(n, 1, 200)}')
            if len(achados) > a.limite:
                print(f'... +{len(achados) - a.limite} (use -n)')
        elif a.cmd == 'listar':
            itens = [n for n in col.notes(a.baralho) if not a.tag or tem_tag(n['tags'], a.tag)]
            linhas = [f'{n["id"]}\t{n["baralho"]}\t{n["lapsos"]}\t{n["tags"]}\t' + '\t'.join(plain(c) for c in n['campos'][:2]) for n in itens]
            if a.saida:
                a.saida.parent.mkdir(parents=True, exist_ok=True)
                a.saida.write_text('id\tbaralho\tlapsos\ttags\tcampo1\tcampo2\n' + '\n'.join(linhas) + '\n', encoding='utf-8')
                print(f'{len(linhas)} nota(s) em {a.saida}')
            else:
                for x in linhas[:a.limite]:
                    print(x[:400])
                if len(linhas) > a.limite:
                    print(f'... +{len(linhas) - a.limite} (use --saida)')
        elif a.cmd == 'dificeis':
            itens = dificeis(col, a.baralho, a.min_lapsos)
            print(f'{len(itens)} nota(s) com >= {a.min_lapsos} lapso(s) ou tag leech')
            for n in itens[:a.limite]:
                print(f'[{n["id"]}] {n["baralho"]} | lapsos {n["lapsos"]} | intervalo {n["intervalo"]}d'
                      f'{" | SUSPENSO" if n["suspenso"] else ""}\n  F: {_curto(n)}')
        elif a.cmd == 'desempenho':
            st = desempenho(col, a.dias)
            print(f'Últimos {a.dias} dias; acerto = revisões de cartões aprendidos que não foram "Novamente" (mín. 10)\n')
            print('Disciplina | cartões | novos | vencidos | próx. 7 d | revisões | acerto | s/revisão')
            for nome in sorted(st, key=lambda k: (st[k]['acerto'] is None, st[k]['acerto'] or 0)):
                d = st[nome]
                print(f'{nome} | {d["cartoes"]} | {d["novos"]} | {d["vencidos"]} | {d["vence_7d"]} | {d["revisoes"]} | '
                      f'{str(d["acerto"]) + "%" if d["acerto"] is not None else "pouco dado"} | {d["seg_por_revisao"] or "-"}')
        elif a.cmd == 'duplicatas':
            r = duplicatas(col, a.tsv, a.limiar)
            a.saida.parent.mkdir(parents=True, exist_ok=True)
            a.saida.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print(json.dumps({'possiveis_duplicatas': len(r['possiveis_duplicatas']), 'saida': str(a.saida)}, ensure_ascii=False))
        elif a.cmd == 'lacunas':
            res = lacunas(col, a.alvo, min_notas=a.min_notas)
            if not res:
                print(f'Nenhuma prioridade Alta/Média para {a.alvo} em referencias/. Rode uma triagem e salve-a como prioridade.')
            print(f'Prioridades {a.alvo} do banco × coleção (casamento de palavras: indício, confira com buscar)\n')
            sem = {}
            for r in res:
                if r['situacao'] == 'sem_baralho':
                    sem.setdefault(r['disciplina'], []).append(r)
            if sem:
                print('Disciplinas sem baralho na coleção (nada estudado no Anki):')
                for disc, itens in sorted(sem.items()):
                    altas = [r['assunto'] for r in itens if r['prioridade'] == 'alta']
                    print(f'  {disc}: {len(itens)} assunto(s) Alta/Média; Alta: {", ".join(altas) or "-"}')
                print()
            print('situação | prioridade | disciplina/assunto | notas | lapsos | prioridade (ID)')
            for r in res:
                if r['situacao'] != 'sem_baralho':
                    print(f'{r["situacao"]} | {r["prioridade"]} | {r["disciplina"]}/{r["assunto"]} | {r["notas"]} | {r["lapsos"]} | {r["id"]}')
            print('\nAssuntos do edital sem prioridade salva não aparecem aqui: veja o edital no banco e triagens futuras.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
