#!/usr/bin/env python3
"""Gera um .colpkg novo: remove as 47 notas antigas de Matemática e adiciona as versões revisadas
como notas NOVAS (sem histórico), deixando todo o resto da coleção intacto.

Trabalha numa cópia temporária pela biblioteca oficial do Anki (testado com anki 26.9.3); o backup
original não é alterado. Depois de exportar, reimporta o pacote gerado e confere que nada além das
notas de Matemática mudou. Uso (na raiz do repositório):

    uv run --python 3.13 --with anki==26.9.3 python -X utf8 \
        lotes/PRF/Revisao_Matematica_Colecao_2026_11_20/fonte/gerar_colecao.py ORIGINAL.colpkg SAIDA.colpkg
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

from anki._backend import RustBackend
from anki.collection import Collection

AQUI = Path(__file__).resolve().parent
LOTE = AQUI.parent / 'lote'
BARALHO = 'Matemática'
CONFIG_VOLATIL = {'nextPos'}
ARQUIVOS = {'Basic': 'atualizar_certo_errado.tsv', 'Cloze': 'atualizar_cloze.tsv'}


def ler_tsvs() -> list[tuple[str, str, str, str, str]]:
    """(notetype, guid_antigo, campo1, campo2, tags) na ordem original das notas."""
    linhas = {}
    for nt, nome in ARQUIVOS.items():
        for ln in (LOTE / nome).read_text(encoding='utf-8').splitlines():
            if ln.startswith('#') or not ln:
                continue
            guid, c1, c2, tags = ln.split('\t')
            linhas[guid] = (nt, guid, c1, c2, tags)
    ordem = [b['guid'] for b in json.loads((AQUI / 'base_colecao.json').read_text(encoding='utf-8'))]
    assert set(ordem) == set(linhas) and len(ordem) == 47
    return [linhas[g] for g in ordem]


def abrir(pacote: Path, pasta: Path) -> Collection:
    # A pasta de mídia precisa ter o nome que o Anki deriva do banco (c.media), senão a
    # exportação sai sem mídia.
    (pasta / 'c.media').mkdir()
    RustBackend().import_collection_package(
        col_path=str(pasta / 'c.anki2'), backup_path=str(pacote.resolve()),
        media_folder=str(pasta / 'c.media'), media_db=str(pasta / 'c.media.db2'))
    return Collection(str(pasta / 'c.anki2'))


def retrato(col: Collection, pasta: Path, excluir_guids: set[str]) -> dict:
    """Tudo o que deve ficar igual, sem as notas de Matemática."""
    notas = {r[1]: r for r in col.db.all('select id,guid,mid,mod,usn,tags,flds,sfld,csum,flags,data from notes')}
    fora = {notas[g][0] for g in excluir_guids if g in notas}
    return {
        'notas': sorted(r for g, r in notas.items() if g not in excluir_guids),
        'cartoes': sorted(r for r in col.db.all('select * from cards') if r[1] not in fora),
        'revlog_outros': sorted(r for r in col.db.all(
            'select r.* from revlog r join cards c on c.id = r.cid where c.nid not in (%s)' % ','.join('?' * len(fora)), *fora)),
        'baralhos': sorted(col.db.all('select id,name,common,kind from decks')),
        'opcoes_baralho': sorted(col.db.all('select id,name,config from deck_config')),
        'modelos': sorted(col.db.all('select id,name,config from notetypes')),
        'campos': sorted(col.db.all('select * from fields')),
        'modelos_cartao': sorted(col.db.all('select ntid,ord,name,config from templates')),
        # nextPos (posição do próximo cartão novo) muda ao adicionar notas: é esperado.
        'config': sorted(r for r in col.db.all('select key,val from config') if r[0] not in CONFIG_VOLATIL),
        'midia': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (pasta / 'c.media').iterdir()},
    }


def main(origem: Path, saida: Path) -> None:
    if saida.exists() or saida.resolve() == origem.resolve():
        raise SystemExit('Use um caminho de saída novo; nada é sobrescrito.')
    novas = ler_tsvs()
    guids_antigos = {n[1] for n in novas}
    with tempfile.TemporaryDirectory(prefix='anki_mat_') as tmp:
        tmp = Path(tmp)
        (tmp / 'a').mkdir()
        col = abrir(origem, tmp / 'a')
        antes = retrato(col, tmp / 'a', guids_antigos)
        n_notas, n_cartoes, n_revlog = (col.db.scalar(f'select count(*) from {t}') for t in ('notes', 'cards', 'revlog'))
        did = col.decks.id_for_name(BARALHO)
        ids = col.db.list('select id from notes where guid in (%s)' % ','.join('?' * len(guids_antigos)), *guids_antigos)
        assert len(ids) == 47, ids
        assert set(col.db.list('select did from cards where nid in (%s)' % ','.join('?' * 47), *ids)) == {did}
        config_antes = col.all_config()
        col.remove_notes(ids)
        for nt, _guid, c1, c2, tags in novas:
            nota = col.new_note(col.models.by_name(nt))
            nota.fields[0], nota.fields[1] = c1, c2
            nota.tags = tags.split()
            col.add_note(nota, did)
        # add_note grava preferências de interface (último tipo de nota do baralho, último
        # baralho do tipo de nota); devolvem-se os valores originais para não mexer em nada além das notas.
        for chave, valor in col.all_config().items():
            if chave in CONFIG_VOLATIL or config_antes.get(chave) == valor:
                continue
            if chave in config_antes:
                col.set_config(chave, config_antes[chave])
            else:
                col.remove_config(chave)
        col.export_collection_package(str(saida), include_media=True, legacy=False)
        col.close()

        # ---------------------------------------------------- conferência no pacote exportado
        (tmp / 'b').mkdir()
        col = abrir(saida, tmp / 'b')
        depois = retrato(col, tmp / 'b', set())
        novas_notas = {r[0]: r for r in col.db.all('select id,guid,mid,tags,flds from notes')
                       if r[0] not in {x[0] for x in antes['notas']}}
        depois['notas'] = sorted(r for r in depois['notas'] if r[0] not in novas_notas)
        depois['cartoes'] = sorted(r for r in depois['cartoes'] if r[1] not in novas_notas)
        depois['revlog_outros'] = sorted(r for r in depois['revlog_outros'] if r[1] not in
                                         set(col.db.list('select id from cards where nid in (%s)' % ','.join('?' * len(novas_notas)), *novas_notas)))
        problemas = [k for k in antes if antes[k] != depois[k]]
        if 'config' in problemas:
            a, b = dict(antes['config']), dict(depois['config'])
            problemas.append('chaves de config: ' + ', '.join(sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))))
        esperado = sorted((c1, c2, ' '.join(sorted(t.split()))) for _nt, _g, c1, c2, t in novas)
        obtido = sorted(tuple(r[4].split('\x1f')) + (' '.join(sorted(r[3].split())),) for r in novas_notas.values())
        cartoes_novos = col.db.all('select did,type,queue,reps from cards where nid in (%s)' % ','.join('?' * len(novas_notas)), *novas_notas)
        resumo = {
            'antes': {'notas': n_notas, 'cartoes': n_cartoes, 'revlog': n_revlog},
            'depois': {k: col.db.scalar(f'select count(*) from {t}') for k, t in (('notas', 'notes'), ('cartoes', 'cards'), ('revlog', 'revlog'))},
            'resto_identico': not problemas, 'diferencas': problemas,
            'notas_novas': len(novas_notas), 'conteudo_igual_tsv': esperado == obtido,
            'cartoes_novos_no_baralho': all(c[0] == did for c in cartoes_novos) and len(cartoes_novos) == 47,
            'cartoes_novos_sem_historico': all(tuple(c[1:]) == (0, 0, 0) for c in cartoes_novos),
            'guids_antigos_ausentes': not col.db.scalar('select count(*) from notes where guid in (%s)' % ','.join('?' * 47), *guids_antigos),
            'renderizacao_ok': all(col.get_card(cid).question().strip() and col.get_card(cid).answer().strip()
                                   for cid in col.db.list('select id from cards where nid in (%s)' % ','.join('?' * len(novas_notas)), *novas_notas)),
            'midia': len(depois['midia']),
            'sha256_saida': hashlib.sha256(saida.read_bytes()).hexdigest(),
        }
        col.close()
    print(json.dumps(resumo, ensure_ascii=False, indent=1))
    ok = (resumo['resto_identico'] and resumo['conteudo_igual_tsv'] and resumo['notas_novas'] == 47
          and resumo['cartoes_novos_no_baralho'] and resumo['cartoes_novos_sem_historico']
          and resumo['guids_antigos_ausentes'] and resumo['renderizacao_ok'])
    if not ok:
        saida.unlink()
        raise SystemExit('Conferência falhou; pacote removido.')


if __name__ == '__main__':
    main(Path(sys.argv[1]), Path(sys.argv[2]))
