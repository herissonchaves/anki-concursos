#!/usr/bin/env python3
"""Importa provas oficiais do Cebraspe (Certo/Errado) para o banco referencias/ e conta as prioridades.

Fluxo (detalhes e formato da spec em ../references/provas-oficiais.md):

  extrair CADERNO.pdf GABARITO.pdf --itens 9-120 -o ITENS.json   itens, texto-base e gabarito definitivo
  revisar ITENS.json [--completo]                                 texto-base e enunciados para conferir e classificar
  figuras CADERNO.pdf [--paginas 3,7]                             caixas de figuras (pontos) por página
  pagina CADERNO.pdf N SAIDA.png [--recorte x0,y0,x1,y1]          renderiza página ou trecho para ler fórmula ou figura
  montar PROVA ITENS.json SPEC -o NOVA.json [--atualizar-existentes]   JSON para `referencias.py nova`
  recortar CADERNO.pdf N x0,y0,x1,y1 NOME.png                     figura em referencias/imagens/
  embutir NOME.png ctx|enun ID [ID ...]                           insere ![[NOME.png]] nas questões
  prioridades PRF|PF_AGENTE [--gravar]                            conta a incidência e grava referencias/prioridades/

PDFs baixados ficam fora do repositório (scratchpad). PROVA é uma chave de `provas` em
../references/provas-oficiais.json (metadados, URLs do caderno e do gabarito); acrescente a prova nova lá.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import referencias as R  # noqa: E402

DADOS = AQUI.parent / 'references' / 'provas-oficiais.json'
CONSULTA_PADRAO = None  # data de consulta; None = hoje

# ------------------------------------------------------------------ extração do caderno
# Lixo de cabeçalho/rodapé e instruções que não pertencem ao texto-base.
LIXO_EXTRACAO = re.compile(r'^(Espaço livre|BLOCO [IV]+|-+ ?PROVA OBJETIVA ?-+|PROVA OBJETIVA|CONHECIMENTOS (BÁSICOS|ESPECÍFICOS)'
                           r'|•.*|\d{1,2}|RASCUNHO|Cargo: .*|– ?\d+ ?–|CONHECIMENTOS .*)\s*$', re.S)
LIXO_CONTEXTO = re.compile(r'^(--.*--|--\s*PROVA OBJETIVA.*|(?i:BLOCO)\s+[IVX]+\b.*|\t.*|/?\d?\s*$|TEXTO|T ¦ E X T O'
                           r'|Figura(\s+\S+)?|Cargo:.*|Gráfico para os itens.*)$')
TITULO_TEXTO = re.compile(r'^Texto (\S+)\s*$')
REF_TEXTO = re.compile(r'texto (\d+[A-Z]\w*(?:-[IVX]+)?)', re.I)
NOVA_LINHA = '⏎'  # na spec, marca quebra de linha (tabelas, código)


def _pymupdf():
    try:
        import pymupdf
    except ImportError:  # versões antigas
        import fitz as pymupdf
    return pymupdf


def _linhas(doc, topo=45, rodape=25):
    """(página, coluna, y_base, x0, texto, tamanho) em ordem de leitura de caderno em duas colunas."""
    for pn, pg in enumerate(doc):
        larg, alt = pg.rect.width, pg.rect.height
        brutas = []
        for b in pg.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                t = ''.join(s['text'] for s in l['spans'])
                if not t.strip():
                    continue
                if re.fullmatch(r'\s*\d{1,3}\s*', t) and l['spans'][0]['size'] < 6.5:
                    continue  # numeração de linhas do texto-base
                x0, y = l['bbox'][0], l['bbox'][3]  # base da linha: alinha o número do item ao texto
                if y < topo + 10 or y > alt - rodape + 8:
                    continue
                brutas.append((0 if x0 < larg / 2 - 5 else 1, y, x0, t.rstrip(), l['spans'][0]['size']))
        brutas.sort(key=lambda r: (r[0], r[1]))
        grupos = []
        for r in brutas:  # pedaços na mesma linha
            if grupos and grupos[-1][0][0] == r[0] and abs(grupos[-1][0][1] - r[1]) < 2.5:
                grupos[-1].append(r)
            else:
                grupos.append([r])
        for g in grupos:
            g.sort(key=lambda r: r[2])
            yield (pn + 1, g[0][0], min(r[1] for r in g), g[0][2], ' '.join(r[3].strip() for r in g), g[0][4])


def juntar(linhas) -> str:
    txt = ''
    for t in linhas:
        t = t.strip()
        if not txt:
            txt = t
        elif txt.endswith('-') and not txt.endswith(' -'):
            txt += t
        else:
            txt += ' ' + t
    return re.sub(r'\s+', ' ', txt).strip()


def extrair_caderno(pdf, primeiro: int, ultimo: int) -> list[dict]:
    """Itens numerados de `primeiro` a `ultimo`: o número fica na margem e as linhas seguintes têm recuo (~18 pt)."""
    doc = _pymupdf().open(str(pdf))
    linhas = list(_linhas(doc))
    margem, todas = {}, {}
    for p, c, y, x, t, s in linhas:
        todas[(p, c)] = min(todas.get((p, c), 9999), x)
        if re.match(r'^\s*\d{1,3}(\s|$)', t):
            margem[(p, c)] = min(margem.get((p, c), 9999), x)
    for k, v in todas.items():
        margem.setdefault(k, v)
    tipica = collections.defaultdict(list)
    for (p, c), v in margem.items():
        tipica[c].append(v)
    tipica = {c: sorted(v)[len(v) // 2] for c, v in tipica.items()}
    for k in margem:  # página sem item (só texto-base): usa a margem típica da coluna
        if abs(margem[k] - tipica[k[1]]) > 12:
            margem[k] = tipica[k[1]]
    esperado, itens, blocos, atual, estado, item, anterior = primeiro, [], [], None, 'ctx', None, None
    for p, c, y, x, t, s in linhas:
        m = re.match(r'^\s*(\d{1,3})(?:\s+(.*))?$', t)
        recuo = x - margem[(p, c)]
        if m and int(m[1]) == esperado <= ultimo and recuo < 6:
            if estado == 'ctx' and blocos:
                atual, blocos = blocos, []
            item = {'item': esperado, 'pagina': p, 'linhas': [m[2] or ''], 'ctx': atual}
            itens.append(item)
            esperado, estado = esperado + 1, 'item'
            continue
        if estado == 'item' and 8 < recuo < 24:
            item['linhas'].append(t)
            continue
        if estado == 'item':
            blocos, estado, anterior = [], 'ctx', None
        novo = (not blocos or recuo > 20 or TITULO_TEXTO.match(t.strip())
                or (anterior is not None and (y - anterior > 16 or y < anterior)))
        if novo:
            blocos.append([t])
        else:
            blocos[-1].append(t)
        anterior = y
    saida = []
    for it in itens:
        paras = [q for q in (juntar(b) for b in (it['ctx'] or [])) if not LIXO_EXTRACAO.match(q)]
        saida.append({'item': it['item'], 'pagina': it['pagina'], 'contexto': paras, 'enunciado': juntar(it['linhas'])})
    return saida


def ler_gabarito(pdf) -> dict[int, str]:
    """Gabarito definitivo em grade (números e letras C/E/X em blocos alternados; X = anulado)."""
    doc = _pymupdf().open(str(pdf))
    toks = [t.strip() for pg in doc for t in pg.get_text('text').splitlines() if t.strip()]
    nums = [int(t) for t in toks if re.fullmatch(r'\d{1,3}', t) and t != '0' and int(t) <= 120]
    letras = [t for t in toks if t in ('C', 'E', 'X')]
    if len(nums) != len(letras):
        raise R.ErroBanco(f'gabarito com {len(nums)} números e {len(letras)} letras: confira o PDF')
    return dict(zip(nums, letras))


# ------------------------------------------------------------------ spec e montagem
def ler_spec(texto: str):
    """Spec por item: `N assunto | sub1, sub2 | palavra; outra | operação`, `#disc ID`, `N =existente`
    e correções `!enun N texto`, `!ctx N-M p1 ¶ p2`, `!nota N texto`, `!vig N motivo`."""
    itens, fix = {}, {'enun': {}, 'ctx': {}, 'nota': {}, 'vig': {}}
    disc = None
    for n_linha, linha in enumerate(texto.splitlines(), 1):
        if not linha.strip() or linha.startswith('//'):
            continue
        if linha.startswith('#disc '):
            disc = linha.split()[1]
            continue
        if linha.startswith('!'):
            cmd, alvo, resto = (linha[1:].split(' ', 2) + [''])[:3]
            if cmd not in fix:
                raise R.ErroBanco(f'spec, linha {n_linha}: correção desconhecida !{cmd}')
            a, _, b = alvo.partition('-')
            for n in range(int(a), int(b or a) + 1):
                fix[cmd][n] = resto
            continue
        n, resto = linha.split(' ', 1)
        if resto.strip() == '=existente':
            itens[int(n)] = None
            continue
        partes = [x.strip() for x in resto.split('|')]
        if len(partes) != 4 or not disc:
            raise R.ErroBanco(f'spec, linha {n_linha}: esperado "N assunto | subs | palavras | operação" depois de #disc')
        assunto, subs, kws, op = partes
        itens[int(n)] = dict(disciplina=disc, assunto=assunto,
                             subassuntos=[s.strip() for s in subs.split(',') if s.strip()],
                             palavras_chave=[k.strip().lower() for k in kws.split(';') if k.strip()],
                             operacao_observada=op)
    return itens, fix


def matematica(t: str) -> str:
    """Letras matemáticas itálicas (U+1D400–U+1D7FF) viram letras comuns."""
    return ''.join(unicodedata.normalize('NFKC', c) if 0x1D400 <= ord(c) <= 0x1D7FF else c for c in t)


def paragrafos(ctx: list[str]) -> list[str]:
    """Limpa o texto-base: começa no título "Texto X", tira lixo e cola parágrafos quebrados no meio."""
    out = []
    tit = [i for i, q in enumerate(ctx) if TITULO_TEXTO.match(q.strip())]
    for p in ctx[tit[0]:] if tit else ctx:
        p = p.strip()
        if LIXO_CONTEXTO.match(p) or p.startswith('\\'):
            continue
        quebrado = out and (re.match(r'^[a-zà-ú(]', p) or out[-1].endswith((':', ','))
                            or re.search(r'[A-Za-zà-ú]$', out[-1]))
        if quebrado and not TITULO_TEXTO.match(out[-1]) and not p.startswith('('):
            out[-1] += ' ' + p
        else:
            out.append(p)
    return out


def _texto_fix(s: str) -> str:
    return s.strip().replace(f' {NOVA_LINHA} ', '\n').replace(NOVA_LINHA, '\n')


def dados():
    return json.loads(DADOS.read_text(encoding='utf-8'))


def trilhas() -> dict[str, set]:
    d = json.loads(R.DISCIPLINAS_JSON.read_text(encoding='utf-8'))
    out = collections.defaultdict(set)
    for s in d['subjects']:
        for t in s['tracks']:
            out[t].add(s['id'])
    return out


def montar(prova: str, itens_extraidos: list[dict], spec: str, consulta: str, raiz=None, cfg=None):
    """Devolve (novos, existentes, sem_spec). `itens_extraidos` vem de `extrair` (com 'gabarito')."""
    cfg = cfg or dados()['provas'][prova]
    itens, fix = ler_spec(spec)
    trilha = trilhas()
    novos, existentes, faltam, textos = [], [], [], {}
    for it in itens_extraidos:
        n, g = it['item'], it['gabarito']
        if n not in itens:
            faltam.append(n)
            continue
        anulado = g == 'X'
        if itens[n] is None:
            existentes.append(dict(id=f"cebraspe-{cfg['ano']}-{R.slug(cfg['orgao'])}-{n:03d}",
                                   gabarito='anulada' if anulado else g,
                                   gabarito_status='anulado' if anulado else 'definitivo',
                                   gabarito_url=cfg['gabarito_url']))
            continue
        if n in fix['ctx']:
            ctx = [_texto_fix(p) for p in fix['ctx'][n].split('¶') if p.strip()]
        else:
            ctx = paragrafos(it['contexto'])
        rot = next((TITULO_TEXTO.match(q)[1] for q in ctx if TITULO_TEXTO.match(q)), None)
        if rot:  # guarda o texto para os blocos seguintes que só o citam ("julgue ... do texto 1A18-I")
            textos[rot.lower()] = [q for q in ctx if not re.search(r'julgue', q, re.I)]
        else:
            ref = REF_TEXTO.search(' '.join(ctx))
            if ref and ref[1].lower() in textos:
                ctx = textos[ref[1].lower()] + ctx
        enun = _texto_fix(fix['enun'].get(n, it['enunciado']))
        if n in fix['nota']:
            enun += '\n\n' + fix['nota'][n].strip()
        m = itens[n]
        alvos = [cfg['alvo']] + [t for t in ('PRF', 'PF_AGENTE') if t != cfg['alvo'] and m['disciplina'] in trilha[t]]
        d = dict(banca='Cebraspe', formato='certo_errado', ano=cfg['ano'], orgao=cfg['orgao'], concurso=cfg['concurso'],
                 cargo=cfg['cargo'], caderno=cfg['caderno'], item=str(n), disciplina=m['disciplina'],
                 assunto=m['assunto'], subassuntos=m['subassuntos'], palavras_chave=m['palavras_chave'],
                 gabarito='anulada' if anulado else g, gabarito_status='anulado' if anulado else 'definitivo',
                 url=cfg['url'], gabarito_url=cfg['gabarito_url'], origem='pesquisa_internet',
                 fonte_descoberta=f"Caderno e gabarito definitivo oficiais no CDN do Cebraspe (página do concurso "
                                  f"{cfg['pasta']}), p. {it['pagina']}",
                 consulta=consulta, concursos_alvo=alvos,
                 operacao_observada=('Item anulado. ' if anulado else '') + m['operacao_observada'],
                 enunciado=matematica(enun))
        if ctx:
            d['texto_base'] = '\n\n'.join(matematica(c) for c in ctx)
        if n in fix['vig']:
            d['vigencia'], d['vigencia_nota'] = 'desatualizada', fix['vig'][n].strip()
        novos.append(d)
    return novos, existentes, faltam


def atualizar_existentes(existentes: list[dict], raiz=None) -> list[str]:
    """Questões já no banco: passa o gabarito a definitivo (ou anulado) com o link do gabarito oficial."""
    msgs = []
    for e in existentes:
        try:
            q = R.localizar([e['id']], raiz)[0]
        except R.ErroBanco:
            msgs.append(f"{e['id']}: não está no banco (tire o =existente da spec)")
            continue
        if str(q.meta['gabarito']) != e['gabarito']:
            msgs.append(f"{e['id']}: gabarito do banco {q.meta['gabarito']} ≠ oficial {e['gabarito']} — revise à mão")
            continue
        q.meta.update(gabarito_status=e['gabarito_status'], gabarito_url=e['gabarito_url'])
        rot = {'C': 'Certo', 'E': 'Errado', 'anulada': 'Anulada'}[e['gabarito']]
        q.corpo = re.sub(r'(## Gabarito\n\n)\*\*[^*]+\*\* — [^\n]*',
                         lambda m: m[1] + f"**{rot}** — {e['gabarito_status']} ([gabarito oficial]({e['gabarito_url']}))",
                         q.corpo, count=1)
        q.salvar()
        msgs.append(f"{e['id']}: gabarito {e['gabarito']} {e['gabarito_status']}")
    return msgs


# ------------------------------------------------------------------ figuras
def caixas_de_figuras(pdf, paginas=None) -> list[tuple[int, list[int]]]:
    """Agrupa imagens e desenhos vetoriais próximos; devolve (página, [x0, y0, x1, y1]) em pontos."""
    fz = _pymupdf()
    doc = fz.open(str(pdf))
    saida = []
    for pn in paginas or range(1, len(doc) + 1):
        pg = doc[pn - 1]
        rects = [fz.Rect(i['bbox']) for i in pg.get_image_info()]
        rects += [d['rect'] for d in pg.get_drawings()
                  if d['rect'].width < 500 and not (d['rect'].height < 2 and d['rect'].width > 200)
                  and d['rect'].width * d['rect'].height > 4]
        grupos: list = []
        for r in rects:
            grupos.append(fz.Rect(r))
            mudou = True
            while mudou:
                mudou = False
                for i in range(len(grupos)):
                    for j in range(i + 1, len(grupos)):
                        if (grupos[i] + (-8, -8, 8, 8)).intersects(grupos[j]):
                            grupos[i] |= grupos[j]
                            del grupos[j]
                            mudou = True
                            break
                    if mudou:
                        break
        saida += [(pn, [round(v) for v in g]) for g in grupos if g.width > 15 and g.height > 15]
    return saida


def renderizar(pdf, pagina: int, saida, recorte=None, dpi=110, cinza=False):
    fz = _pymupdf()
    pg = fz.open(str(pdf))[pagina - 1]
    clip = fz.Rect(*recorte) if recorte else None
    pix = pg.get_pixmap(dpi=dpi, clip=clip, colorspace=fz.csGRAY if cinza else fz.csRGB)
    pix.save(str(saida))
    return pix.width, pix.height


NOTA_FIGURA = re.compile(r'\[(Figura|Figuras|Gráfico|Fotografia|Fotografias|Mapa|Item formado)')


def embutir(nome: str, onde: str, ids, raiz=None) -> list[str]:
    """Insere ![[nome]] no texto-base (onde='ctx') ou depois do enunciado (onde='enun') de cada questão.

    No texto-base, entra antes da primeira nota de figura entre colchetes ou, sem nota, antes do comando
    ("julgue..."). No enunciado, antes da nota de figura ou no fim."""
    if not (R.raiz_banco(raiz) / R.IMAGENS / nome).is_file():
        raise R.ErroBanco(f'{nome} não está em {R.IMAGENS}/ (use recortar)')
    msgs = []
    for q in R.localizar(list(ids), raiz):
        if f'![[{nome}]]' in q.corpo:
            msgs.append(f'{q.id}: já tinha {nome}')
            continue
        cab, enun = q.corpo.split('## Enunciado\n\n', 1)
        enun, resto = enun.split('\n## ', 1)
        linhas = enun.rstrip('\n').split('\n')
        bq = [i for i, l in enumerate(linhas) if l.startswith('>')]
        if onde == 'ctx' and bq:
            alvo = next((i for i in bq if NOTA_FIGURA.search(linhas[i])), None)
            if alvo is None:
                alvo = max(i for i in bq if linhas[i].strip() != '>')
                while alvo > bq[0] and linhas[alvo - 1].strip() != '>':
                    alvo -= 1
            linhas[alvo:alvo] = [f'> ![[{nome}]]', '>']
        else:
            inicio = bq[-1] + 1 if bq else 0
            alvo = next((i for i in range(inicio, len(linhas)) if NOTA_FIGURA.search(linhas[i])), None)
            if alvo is None:
                linhas += ['', f'![[{nome}]]']
            else:
                linhas[alvo:alvo] = [f'![[{nome}]]', '']
        texto = '\n'.join(linhas)
        texto = re.sub(r' (do caderno oficial )?não reproduzid[ao]s?', lambda m: ' do caderno oficial' if m[1] else '', texto)
        q.corpo = cab + '## Enunciado\n\n' + texto.rstrip('\n') + '\n\n## ' + resto
        q.meta['hash'] = q.hash_corpo()
        q.salvar()
        msgs.append(f'{q.id}: {nome}')
    return msgs


# ------------------------------------------------------------------ prioridades
def _regra(nval, dval, presente, provas_disc, fora, nome_edital):
    media = nval / len(provas_disc) if provas_disc else 0
    share = nval / dval if dval else 0
    recorrente = len(presente) >= min(2, len(provas_disc))
    if fora:
        return 'baixa', f'fora do programa do {nome_edital}: {fora}'
    if (media >= 2 or share >= 0.30) and recorrente:
        return 'alta', f'{media:.1f} item(ns) válido(s) por prova e recorrente'
    if media >= 1 or len(presente) >= 2 or share >= 0.10:
        return 'media', f'{media:.1f} item(ns) válido(s) por prova'
    return 'baixa', f'{media:.1f} item(ns) válido(s) por prova, em {len(presente)} prova(s)'


REGRA_TXT = ('Regra: Alta = média ≥ 2 itens válidos por prova com a disciplina (ou ≥ 30% da disciplina) e presente em '
             '≥ 2 provas (ou em todas as que tiveram a disciplina); Média = média ≥ 1 item por prova, ou presente em '
             '≥ 2 provas, ou ≥ 10% da disciplina; Baixa = o resto, ou assunto fora do programa vigente.')
GERADA = 'Contagem das provas oficiais'  # início de fonte_descoberta dos arquivos gerados aqui
CURADA = '(atualiza a triagem'  # marca, em fonte_descoberta, a prioridade curada à mão que a contagem só atualiza


def contar(conc: str, raiz=None, dados_=None, hoje=None):
    """Documentos de prioridade (dicts para `nova`) e um resumo por (disciplina, assunto)."""
    d = dados_ or dados()
    cfg = d['concursos'][conc]
    hoje = hoje or __import__('datetime').date.today().isoformat()
    nomes = [p[0] for p in cfg['provas']]
    prova_de = {(ano, c): nome for nome, ano, cads in cfg['provas'] for c in cads}
    qs = [q for q in R.carregar(raiz)[0] if q.tipo == 'questao' and q.meta.get('orgao') == cfg['orgao']
          and (q.meta['ano'], q.meta['caderno']) in prova_de]
    tot, anu = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
    por = collections.defaultdict(lambda: collections.defaultdict(list))
    for q in qs:
        pv = prova_de[(q.meta['ano'], q.meta['caderno'])]
        (anu if q.meta['gabarito_status'] == 'anulado' else tot)[q.meta['disciplina']][pv] += 1
        por[(q.meta['disciplina'], q.meta['assunto'])][pv].append(q)
    docs, resumo = [], []
    for (disc, ass), pp in sorted(por.items()):
        val = {pv: [q for q in pp.get(pv, []) if q.meta['gabarito_status'] != 'anulado'] for pv in nomes}
        nul = {pv: [q for q in pp.get(pv, []) if q.meta['gabarito_status'] == 'anulado'] for pv in nomes}
        nval, dval = sum(map(len, val.values())), sum(tot[disc].values())
        provas_disc = [pv for pv in nomes if tot[disc][pv] or anu[disc][pv]]
        presente = [pv for pv in nomes if val[pv]]
        prio, motivo = _regra(nval, dval, presente, provas_disc, cfg.get('fora_do_edital', {}).get(f'{disc}/{ass}'),
                              cfg['nome_edital'])
        resumo.append(dict(disciplina=disc, assunto=ass, prioridade=prio, validos=nval, da_disciplina=dval,
                           provas=len(presente), provas_da_disciplina=len(provas_disc)))
        docs.append(_documento(conc, cfg, d['rotulos'], disc, ass, prio, motivo, val, nul, tot[disc], anu[disc],
                               nomes, presente, provas_disc, hoje))
    return docs, resumo


def _documento(conc, cfg, rotulos, disc, ass, prio, motivo, val, nul, totd, anud, nomes, presente, provas_disc, hoje):
    todos = [q for pv in nomes for q in val[pv]]
    anulados = [q for pv in nomes for q in nul[pv]]
    nval, dval = len(todos), sum(totd.values())
    subs = collections.Counter(s for q in todos for s in q.meta['subassuntos'])
    subs_pv = collections.defaultdict(set)
    for pv in nomes:
        for q in val[pv]:
            for s in q.meta['subassuntos']:
                subs_pv[s].add(pv)
    kws = collections.Counter(k for q in todos + anulados for k in q.meta['palavras_chave'])
    alta, media, baixa = [], [], []
    for s, n in subs.most_common():
        ids = ', '.join(q.id for q in todos if s in q.meta['subassuntos'])
        linha = f'- {s.replace("_", " ")}: {n} item(ns) em {len(subs_pv[s])} prova(s) — {ids}.'
        (alta if (n >= 2 and len(subs_pv[s]) >= 2) or n >= 3 else media if subs_pv[s] & set(nomes[1:]) else baixa).append(linha)
    baixa += [f'- {s.replace("_", " ")}: só em item anulado ({q.id}).'
              for q in anulados for s in q.meta['subassuntos'] if s not in subs]
    rotulo_prio = {'alta': 'Alta', 'media': 'Média', 'baixa': 'Baixa'}[prio]
    tabela = ['| Prova | Itens válidos do assunto | Válidos da disciplina | Anulados do assunto | Anulados da disciplina |',
              '| --- | --- | --- | --- | --- |']
    for nome, _, cads in cfg['provas']:
        if nome not in provas_disc:
            tabela.append(f'| {nome} | — | disciplina sem itens nesta prova | — | — |')
            continue
        ids_nul = f" ({', '.join(q.id for q in nul[nome])})" if nul[nome] else ''
        tabela.append(f'| {nome} ({", ".join(sorted(cads))}) | {len(val[nome])} | {totd[nome]} | '
                      f'{len(nul[nome])}{ids_nul} | {anud[nome]} |')
    corpo = '\n'.join([
        '## Avaliação', '',
        f'- Prioridade {rotulo_prio}: {motivo}.',
        f'- {nval} item(ns) válido(s) de {dval} da disciplina nas provas contadas ({nval / dval if dval else 0:.0%}); '
        f'presente em {len(presente)} de {len(provas_disc)} prova(s) com a disciplina ({", ".join(presente) or "nenhuma"}).',
        f'- Avaliado em {"/".join(reversed(hoje.split("-")))} por contagem das provas oficiais (método abaixo); reavaliar quando sair prova nova.', '',
        '## Alta', '', *(alta or ['- Nenhum subtema com recorrência (≥ 2 itens em provas diferentes, ou ≥ 3 itens).']), '',
        '## Média', '', *(media or ['- Nenhum.']), '',
        '## Baixa', '', *(baixa or ['- Nenhum.']), '',
        '## Pegadinhas recorrentes', '',
        *([f'- {q.id} (Errado): {q.meta["operacao_observada"]}' for q in todos if q.meta['gabarito'] == 'E']
          or ['- Nenhum item com gabarito Errado nas provas contadas.']), '',
        '## Incidência nas provas oficiais', '', *tabela, '',
        '- Método: o agente leu cada item das provas oficiais (cadernos e gabaritos definitivos do Cebraspe no CDN) e '
        'atribuiu disciplina e assunto pelo conteúdo cobrado, não pelo bloco do caderno. Denominador: itens válidos da '
        'disciplina na mesma prova; anulados contados à parte. ' + REGRA_TXT,
        f'- Itens válidos: {", ".join(q.id for q in todos) or "nenhum"}.',
    ])
    pv_txt = '; '.join(f'{pv}: {len(val[pv])} de {totd[pv]} válidos da disciplina'
                       + (f' (+{len(nul[pv])} anulado(s))' if nul[pv] else '') for pv in nomes if pv in provas_disc)
    rot = rotulos.get(f'{disc}/{ass}', ass.replace('_', ' '))
    disc_rot = next((s['label'] for s in json.loads(R.DISCIPLINAS_JSON.read_text(encoding='utf-8'))['subjects']
                     if s['id'] == disc), disc)
    url = next((q.meta['url'] for pv in reversed(nomes) for q in val[pv] + nul[pv]), '')
    return dict(tipo='prioridade', titulo=f'{cfg["rotulo"]} — prioridade de {disc_rot}: {rot}', disciplina=disc,
                assunto=ass, subassuntos=[s for s, _ in subs.most_common(8)] or [ass],
                palavras_chave=['prioridade', 'o que mais cai'] + [k for k, _ in kws.most_common(12)],
                concursos_alvo=[conc], concurso=conc, prioridade=prio, incidencia=f'{pv_txt}. Método no corpo.',
                evidencias=[q.id for q in todos + anulados] + [cfg['edital']], url=url,
                fonte_descoberta=f'{GERADA} (cadernos e gabaritos definitivos do Cebraspe): ' + ', '.join(nomes),
                consulta=hoje, corpo=corpo)


def _secoes(texto: str) -> dict[str, str]:
    out = {}
    for bloco in re.split(r'\n(?=## )', '\n' + texto):
        if bloco.startswith('## '):
            cab, _, resto = bloco.partition('\n')
            out[cab[3:].strip()] = resto.strip()
    return out


def gravar_prioridades(docs, raiz=None) -> list[str]:
    """Cria ou regrava cada prioridade. Arquivo curado à mão (fonte_descoberta sem "Contagem das provas
    oficiais") é atualizado: troca prioridade, incidência e evidências e mantém título, url e seções curadas."""
    existentes = {(q.meta.get('concurso'), q.meta['disciplina'], q.meta['assunto']): q
                  for q in R.carregar(raiz)[0] if q.tipo == 'prioridade'}
    msgs = []
    for d in docs:
        q = existentes.get((d['concurso'], d['disciplina'], d['assunto']))
        fonte = str(q.meta.get('fonte_descoberta', '')) if q is not None else ''
        if q is not None and fonte.startswith(GERADA) and CURADA not in fonte:
            q.caminho.unlink()  # versão anterior gerada por este script
            q = None
        if q is None:
            st, novo, erros = R.nova(dict(d), raiz)
            msgs.append(f'{st}: {novo.id if novo else d["titulo"]}' + (f' {erros}' if st != 'criada' else ''))
            continue
        sec, nova = _secoes(q.corpo), _secoes(d['corpo'])
        antiga = ' '.join(l.lstrip('- ').strip() for l in sec.get('Avaliação', '').split('\n') if l.strip())
        partes = [f'# {q.meta["titulo"]}', '', '## Avaliação', '', nova['Avaliação']]
        if antiga and 'Triagem anterior' not in antiga:
            partes.append(f'- Triagem anterior (curada): {antiga}')
        elif antiga:
            partes += [l for l in sec['Avaliação'].split('\n') if 'Triagem anterior' in l]
        for nome in ('Alta', 'Média', 'Baixa'):
            curado = next((v for k, v in sec.items() if k.startswith(nome)), '')
            curado = [l for l in curado.split('\n')
                      if l.strip() and ' item(ns) em ' not in l and 'só em item anulado' not in l]
            gerado = [l for l in nova[nome].split('\n') if l.strip() and l not in curado]
            if len(curado + gerado) > 1:  # "- Nenhum..." só quando não há outra linha
                curado = [l for l in curado if not l.startswith('- Nenhum')]
                gerado = [l for l in gerado if not l.startswith('- Nenhum')] or ([] if curado else gerado[:1])
            partes += ['', f'## {nome}', '', '\n\n'.join(x for x in ('\n'.join(curado), '\n'.join(gerado)) if x)]
        peg = '\n'.join(l for l in sec.get('Pegadinhas recorrentes', '').split('\n') if '(Errado):' not in l)
        partes += ['', '## Pegadinhas recorrentes', '', peg.strip(), nova['Pegadinhas recorrentes'],
                   '', '## Incidência nas provas oficiais', '', nova['Incidência nas provas oficiais'], '']
        q.corpo = re.sub(r'\n{3,}', '\n\n', '\n'.join(partes))
        q.meta.update(prioridade=d['prioridade'], incidencia=d['incidencia'], evidencias=d['evidencias'],
                      fonte_descoberta=fonte if CURADA in fonte else f'{d["fonte_descoberta"]} {CURADA} curada)')
        q.salvar()
        msgs.append(f'atualizada (curada): {q.id} → {d["prioridade"]}')
    return msgs


# ------------------------------------------------------------------ linha de comando
def _intervalo(txt: str) -> tuple[int, int]:
    a, _, b = txt.partition('-')
    return int(a), int(b or a)


def main(argv=None) -> int:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--raiz', help='pasta do banco (padrão: referencias/ na raiz do repositório)')
    sub = ap.add_subparsers(dest='cmd', required=True)
    ex = sub.add_parser('extrair', help='itens, texto-base e gabarito de caderno + gabarito definitivo')
    ex.add_argument('caderno')
    ex.add_argument('gabarito')
    ex.add_argument('--itens', required=True, help='ex.: 9-120 (numeração do caderno)')
    ex.add_argument('-o', '--saida', required=True)
    rv = sub.add_parser('revisar', help='imprime texto-base e enunciados para conferir e classificar')
    rv.add_argument('itens')
    rv.add_argument('--completo', action='store_true', help='texto-base inteiro (padrão: 120 caracteres por parágrafo)')
    fg = sub.add_parser('figuras', help='caixas de figuras por página (pontos), para recortar')
    fg.add_argument('caderno')
    fg.add_argument('--paginas', help='ex.: 3,7')
    pg = sub.add_parser('pagina', help='renderiza uma página ou trecho em PNG (ler fórmula, conferir figura)')
    pg.add_argument('caderno')
    pg.add_argument('numero', type=int)
    pg.add_argument('saida')
    pg.add_argument('--recorte', help='x0,y0,x1,y1 em pontos')
    pg.add_argument('--dpi', type=int, default=110)
    mo = sub.add_parser('montar', help='JSON para referencias.py nova a partir da extração e da spec')
    mo.add_argument('prova', help='chave em references/provas-oficiais.json')
    mo.add_argument('itens')
    mo.add_argument('spec')
    mo.add_argument('-o', '--saida', required=True)
    mo.add_argument('--consulta', help='AAAA-MM-DD (padrão: hoje)')
    mo.add_argument('--atualizar-existentes', action='store_true', help='grava gabarito definitivo nos itens =existente')
    rc = sub.add_parser('recortar', help='salva figura do caderno em referencias/imagens/')
    rc.add_argument('caderno')
    rc.add_argument('numero', type=int)
    rc.add_argument('recorte', help='x0,y0,x1,y1 em pontos (veja figuras)')
    rc.add_argument('nome', help='<id-da-questão>-figN.png')
    em = sub.add_parser('embutir', help='insere ![[NOME.png]] nas questões')
    em.add_argument('nome')
    em.add_argument('onde', choices=['ctx', 'enun'])
    em.add_argument('ids', nargs='+')
    pr = sub.add_parser('prioridades', help='conta a incidência por assunto e grava as prioridades do concurso')
    pr.add_argument('concurso', help='chave de concursos em references/provas-oficiais.json (PRF, PF_AGENTE)')
    pr.add_argument('--gravar', action='store_true', help='sem esta opção, só mostra a contagem')
    a = ap.parse_args(argv)
    raiz = a.raiz
    try:
        if a.cmd == 'extrair':
            ini, fim = _intervalo(a.itens)
            itens = extrair_caderno(a.caderno, ini, fim)
            gab = ler_gabarito(a.gabarito)
            for it in itens:
                it['gabarito'] = gab.get(it['item'], R.RASCUNHO)
            Path(a.saida).write_text(json.dumps(itens, ensure_ascii=False, indent=1), encoding='utf-8')
            sem = [it['item'] for it in itens if it['gabarito'] == R.RASCUNHO]
            print(f'{len(itens)} itens de {fim - ini + 1} esperados ({ini}-{fim}); sem gabarito: {sem or "nenhum"}')
            return 0 if len(itens) == fim - ini + 1 and not sem else 1
        if a.cmd == 'revisar':
            anterior = None
            for it in json.loads(Path(a.itens).read_text(encoding='utf-8')):
                if it['contexto'] != anterior:
                    anterior = it['contexto']
                    print(f'\n### texto-base antes do item {it["item"]} (p. {it["pagina"]})')
                    for p in anterior:
                        print('  ¶', p if a.completo else p[:120])
                print(f'{it["item"]:>3} [{it.get("gabarito", "?")}] {it["enunciado"]}')
        elif a.cmd == 'figuras':
            pags = [int(x) for x in a.paginas.split(',')] if a.paginas else None
            for p, caixa in caixas_de_figuras(a.caderno, pags):
                print(p, ','.join(map(str, caixa)))
        elif a.cmd == 'pagina':
            rec = [float(v) for v in a.recorte.split(',')] if a.recorte else None
            print(renderizar(a.caderno, a.numero, a.saida, rec, a.dpi))
        elif a.cmd == 'montar':
            consulta = a.consulta or __import__('datetime').date.today().isoformat()
            itens = json.loads(Path(a.itens).read_text(encoding='utf-8'))
            novos, exist, faltam = montar(a.prova, itens, Path(a.spec).read_text(encoding='utf-8'), consulta, raiz)
            Path(a.saida).write_text(json.dumps(novos, ensure_ascii=False, indent=1), encoding='utf-8')
            print(f'{len(novos)} novo(s) em {a.saida}; {len(exist)} já no banco; sem spec: {faltam or "nenhum"}')
            for e in exist:
                print('  existente:', e['id'], e['gabarito'], e['gabarito_status'])
            if a.atualizar_existentes:
                for m in atualizar_existentes(exist, raiz):
                    print('  ', m)
            return 1 if faltam else 0
        elif a.cmd == 'recortar':
            destino = R.raiz_banco(raiz) / R.IMAGENS
            destino.mkdir(parents=True, exist_ok=True)
            w, h = renderizar(a.caderno, a.numero, destino / a.nome, [float(v) for v in a.recorte.split(',')], 130, True)
            print(f'{destino / a.nome} ({w}×{h})')
        elif a.cmd == 'embutir':
            for m in embutir(a.nome, a.onde, a.ids, raiz):
                print(m)
        elif a.cmd == 'prioridades':
            docs, resumo = contar(a.concurso, raiz)
            for r in resumo:
                print(f"{r['disciplina']}/{r['assunto']}: {r['prioridade']} — {r['validos']} de {r['da_disciplina']} "
                      f"válidos, em {r['provas']} de {r['provas_da_disciplina']} prova(s)")
            if a.gravar:
                for m in gravar_prioridades(docs, raiz):
                    print(m)
    except R.ErroBanco as e:
        print(f'ERRO: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
