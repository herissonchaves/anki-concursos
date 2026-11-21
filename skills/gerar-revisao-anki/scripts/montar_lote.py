#!/usr/bin/env python3
"""Monta um lote Anki-Concursos a partir dos cartões definidos em `fonte/gerar_lote.py`.

O `gerar_lote.py` de cada lote fica só com o conteúdo: fontes, referências de
questões, esquemas e cartões. Este módulo cuida do restante: linhas dos TSVs
(UTF-8 sem BOM, LF), embaralhamento C/E reprodutível, `calibracao_cebraspe.json`,
`revisao_recuperacao.json`, resolução dos sinais do lint por
`fonte/sinais_resolvidos.json` e a prévia `previa_cards.html` (claro/escuro).

Convenção dos dicionários de cartão (chaves curtas):

- Todos: `k` (ID editorial: R01, D01, C01), `tags`, `b` (blocos de `html_anki`),
  `m` (texto do 💡 Memorize), `fx` (chaves de `fontes`).
- R: `g` ('C'/'E'), `f` (frente), `alvo`, `sol`, `alt`, `rec`, `fb`.
- D: `g`, `f`, `alvo`, `op`, `regra`, `dado`, `solucao`, `erro`, `conc`, `orig`,
  `refs` (IDs de `referencias`), `fid` ('comparada' com `cmp` ou 'inspiracao_geral'
  com `lim`), `rb` (use `rubrica(...)`) e, no schema 2, `refs` com questão de outra
  banca ou `obp` (outras_bancas_pendencia).
- Cloze: `t` (texto com uma omissão {{c1::…}}; várias só com a tag Mnemonico),
  `alvo`, `sol`, `alt`, `rec`, `fb`, `cob` ({'1': ['D04']}: D que cobrem cada lacuna).

`referencias`: pode ficar vazio ([]): os IDs do banco `referencias/` citados em `refs` de
qualquer cartão (R, D ou Cloze) já entram sozinhos. Questões com prova oficial (url) viram
as referências da calibração; as sem prova (url nao_localizado, comuns no PDF enviado)
entram em `referencias_sem_prova` (raiz e D), contam como inspiração e como questão de
outra banca, mas não sustentam fidelidade comparada. Dicts no formato da calibração
continuam aceitos. Ao gerar, o uso de cada ID é registrado no `usado_em` da questão
(`registrar_uso=False` desliga). Modelo pronto: `../modelos/gerar_lote_modelo.py`.

`fontes`: {chave: (url, trecho verificado)}. Os relatórios .txt continuam
escritos à mão em `lote/relatorios/`. Revisão pelo próprio agente é autorevisão;
os registros gerados não certificam conteúdo.
"""
from __future__ import annotations

import html as _html
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
SCRIPTS_REFERENCIAS = Path(__file__).resolve().parents[2] / 'referencias-questoes' / 'scripts'
from html_anki import extra_cloze, frente, verso_ce  # noqa: E402
from validar_revisao_pedagogica import batch_hash, fingerprint, signals  # noqa: E402

R_TAG = 'Tipo_Revisao_Rapida'
D_TAG = 'Tipo_Desafiadora_Cebraspe Estilo_Cebraspe'
MNEMONICO = 'Mnemonico'
CRITERIOS = ('correcao', 'determinacao', 'operacao_d', 'comparacao', 'autoria', 'feedback',
             'linguagem_didatica', 'utilidade')
REVISOR_PADRAO = 'Claude (assistente de IA) — mesmo agente que redigiu os cartões'


def rubrica(correcao, determinacao, operacao_d, comparacao, autoria, feedback, linguagem_didatica, utilidade):
    """Rubrica de calibração; comece `comparacao` com 'PENDENTE: ' para registrá-la pendente."""
    valores = (correcao, determinacao, operacao_d, comparacao, autoria, feedback, linguagem_didatica, utilidade)
    return {chave: {'resultado': 'PENDENTE' if (chave == 'comparacao' and valor.startswith('PENDENTE')) else 'PASSA',
                    'evidencia': valor.replace('PENDENTE: ', '')} for chave, valor in zip(CRITERIOS, valores)}


def cloze_view(texto: str, revelar: bool) -> str:
    return re.sub(r'\{\{c1::(.*?)\}\}', (lambda m: f'<span class="cloze">{m[1]}</span>') if revelar else
                  (lambda m: '<span class="cloze">[...]</span>'), texto)


class Lote:
    def __init__(self, pasta, base_tags, fontes, hoje, referencias, R, D, CZ, semente,
                 schema_calibracao=2, revisor=REVISOR_PADRAO, titulo_previa='Prévia dos cards',
                 banco_referencias=None, registrar_uso=True):
        self.pasta, self.out = Path(pasta), Path(pasta) / 'lote'
        self.base, self.F, self.hoje = base_tags, fontes, hoje
        self.R, self.D, self.CZ, self.semente = R, D, CZ, semente
        self.schema, self.revisor, self.titulo = schema_calibracao, revisor, titulo_previa
        self.banco, self.registrar = banco_referencias, registrar_uso
        self.refs = self._resolver_refs(referencias)

    # ------------------------------------------------------------ banco de referências
    @staticmethod
    def _modulo_referencias():
        if str(SCRIPTS_REFERENCIAS) not in sys.path:
            sys.path.insert(0, str(SCRIPTS_REFERENCIAS))
        import referencias
        return referencias

    def _resolver_refs(self, referencias):
        """Monta as referências da calibração a partir dos IDs do banco.

        IDs vêm de `referencias` e dos `refs` de qualquer cartão (R, D ou Cloze). Questões com
        prova oficial (url) viram dicts completos; as sem prova (url nao_localizado, típicas do
        PDF enviado) vão para `self.refs_sem_prova` e para `referencias_sem_prova` dos D.
        """
        dicts = [r for r in referencias if not isinstance(r, str)]
        ids_dicts = {r.get('id') for r in dicts}
        ids = [r for r in referencias if isinstance(r, str)]
        for x in self.R + self.D + self.CZ:
            ids += [r for r in x.get('refs', ()) if isinstance(r, str) and r not in ids_dicts]
        self.ids_banco = list(dict.fromkeys(ids))
        self.ids_sem_prova, self.refs_sem_prova = set(), []
        if not self.ids_banco:
            return dicts
        ref = self._modulo_referencias()
        com = [i for i in self.ids_banco if ref.tem_prova(i, self.banco)]
        self.ids_sem_prova = set(self.ids_banco) - set(com)
        sem_d = sorted({i for x in self.D for i in x.get('refs', ()) if i in self.ids_sem_prova})
        self.refs_sem_prova = ref.sem_prova(*sem_d, raiz=self.banco) if sem_d else []
        return dicts + (ref.calibracao(*com, raiz=self.banco) if com else [])

    def rotulo_lote(self):
        try:
            return self.pasta.resolve().relative_to(Path(__file__).resolve().parents[3] / 'lotes').as_posix()
        except ValueError:
            return self.pasta.name

    def registrar_usos(self):
        if not (self.registrar and self.ids_banco):
            return
        ref = self._modulo_referencias()
        for ident in self.ids_banco:
            cartoes = [x['k'] for x in self.R + self.D + self.CZ if ident in x.get('refs', ())]
            if cartoes:
                ref.registrar_uso(ident, self.rotulo_lote(), cartoes, self.banco)
        ref.indexar(self.banco)

    # ------------------------------------------------------------ fontes
    def fontes(self, *keys):
        return [{'url': self.F[k][0], 'consulta': self.hoje, 'trecho': self.F[k][1]} for k in keys]

    def urls(self, *keys):
        return [self.F[k][0] for k in keys]

    # ------------------------------------------------------------ linhas
    def row_r(self, x):
        return [x['f'], verso_ce(x['g'], x['b'], x['m']), f"{self.base} {x['tags']} {R_TAG}"]

    def row_d(self, x):
        return [frente(x['f']), verso_ce(x['g'], x['b'], x['m']), f"{self.base} {x['tags']} {D_TAG}"]

    def row_c(self, x):
        return [frente(x['t']), extra_cloze(x['b'], x['m']), f"{self.base} {x['tags']}"]

    def montar_linhas(self):
        for x in self.CZ:
            if MNEMONICO not in x['tags'].split():
                assert x['t'].count('{{c1::') == 1, f"{x['k']}: uma omissão por nota (várias só com a tag Mnemonico)"
        self.ce_items = [('R', x) for x in self.R] + [('D', x) for x in self.D]
        random.Random(self.semente).shuffle(self.ce_items)
        self.ce_rows, self.line_of = [], {}
        for n, (kind, x) in enumerate(self.ce_items, 1):
            self.ce_rows.append(self.row_r(x) if kind == 'R' else self.row_d(x))
            self.line_of[x['k']] = n
        self.cz_rows = [self.row_c(x) for x in self.CZ]

    def rid(self, k):
        return f'anki_certo_errado.tsv:{self.line_of[k]}'

    def gravar_tsvs(self):
        self.out.mkdir(parents=True, exist_ok=True)
        (self.out / 'relatorios').mkdir(exist_ok=True)

        def write(name, rows):
            data = ('\n'.join('\t'.join(r) for r in rows) + '\n').encode('utf-8') if rows else b''
            (self.out / name).write_bytes(data)
            return data
        self.items = {'anki_certo_errado.tsv': write('anki_certo_errado.tsv', self.ce_rows),
                      'anki_cloze.tsv': write('anki_cloze.tsv', self.cz_rows)}

    def _json(self, name, data):
        texto = json.dumps(data, ensure_ascii=False, indent=1)
        (self.out / 'relatorios' / name).write_text(texto, encoding='utf-8', newline='\n')

    # ------------------------------------------------------------ registros
    def registro_calibracao(self):
        cal = {'schema_version': self.schema, 'referencias': self.refs, 'cartoes': []}
        if self.refs_sem_prova:
            cal['referencias_sem_prova'] = self.refs_sem_prova
        for x in self.D:
            n = self.line_of[x['k']]
            refs = list(x.get('refs', ()))
            rec = dict(id=x['k'], linha=n, sha256=fingerprint(self.ce_rows[n - 1]), gabarito=x['g'], alvo=x['alvo'],
                       operacao_autoral=x['op'], regra=x['regra'], dado_decisivo=x['dado'], solucao=x['solucao'],
                       erro_plausivel=x['erro'], leitura_concorrente=x['conc'], originalidade=x['orig'],
                       fontes_conteudo=self.urls(*x['fx']),
                       referencias=[r for r in refs if r not in self.ids_sem_prova], fidelidade=x['fid'],
                       segunda_conferencia=True, decisao='APROVAR', rubrica=x['rb'])
            if any(r in self.ids_sem_prova for r in refs):
                rec['referencias_sem_prova'] = [r for r in refs if r in self.ids_sem_prova]
            if x['fid'] == 'comparada':
                rec['comparacao'] = x['cmp']
            else:
                rec['limitacao'] = x['lim']
            if self.schema >= 2 and x.get('obp'):
                rec['outras_bancas_pendencia'] = x['obp']
            cal['cartoes'].append(rec)
        if self.D:
            self._json('calibracao_cebraspe.json', cal)
        return cal

    def registro_revisao(self, sinais_resolvidos):
        rev = {'schema_version': 1, 'sha256_lote': batch_hash(self.items), 'revisor': self.revisor,
               'tipo_revisao': 'autorevisao', 'cartoes': [], 'sinais': []}
        for x in self.R:
            rev['cartoes'].append(dict(
                id=self.rid(x['k']), sha256=fingerprint(self.ce_rows[self.line_of[x['k']] - 1]), alvo=x['alvo'],
                solucao=x['sol'], fontes=self.fontes(*x['fx']), alternativa_concorrente=x['alt'], recuperacao=x['rec'],
                feedback=x['fb'], segunda_conferencia=True, decisao='APROVAR'))
        for i, x in enumerate(self.CZ, 1):
            rev['cartoes'].append(dict(
                id=f'anki_cloze.tsv:{i}', sha256=fingerprint(self.cz_rows[i - 1]), alvo=x['alvo'], solucao=x['sol'],
                fontes=self.fontes(*x['fx']), alternativa_concorrente=x['alt'], recuperacao=x['rec'], feedback=x['fb'],
                desafiadores_por_lacuna={g: [self.rid(k) for k in ks] for g, ks in x['cob'].items()},
                segunda_conferencia=True, decisao='APROVAR'))
        editorial = {f'anki_certo_errado.tsv:{n}': k for k, n in self.line_of.items()}
        editorial.update({f'anki_cloze.tsv:{i}': x['k'] for i, x in enumerate(self.CZ, 1)})
        motivos = json.loads(Path(sinais_resolvidos).read_text(encoding='utf-8')) if Path(sinais_resolvidos).exists() else {}
        self.pendentes, detalhes = [], []
        for s in signals(self.items):
            chave = f"{editorial.get(s['id'], s['id'])}|{s['sinal']}"
            if chave in motivos:
                rev['sinais'].append({'sinal_id': s['sinal_id'], 'decisao': 'EXCECAO_JUSTIFICADA', 'motivo': motivos[chave]})
            else:
                self.pendentes.append(chave)
                detalhes.append(f"{chave} ({s.get('detalhes', '')})")
        if self.pendentes:
            print('SINAIS PENDENTES — corrija o cartão ou justifique em fonte/sinais_resolvidos.json '
                  '(chave "ID|SINAL"):\n  ' + '\n  '.join(detalhes))
        self._json('revisao_recuperacao.json', rev)
        return rev

    # ------------------------------------------------------------ prévia (não vai para o Anki)
    def gerar_previa(self):
        cards = [(x['k'], row[0], row[1], row[2]) for (_, x), row in zip(self.ce_items, self.ce_rows)]
        cards += [(x['k'], cloze_view(row[0], False), cloze_view(row[0], True) + '<hr id="answer">' + row[1], row[2])
                  for x, row in zip(self.CZ, self.cz_rows)]
        pares = ''.join(
            f'<section><h2>{k} <small>{_html.escape(t)}</small></h2><div class="lado"><div class="card">{fr}</div>'
            f'<div class="card">{(fr + "<hr id=answer>" + vs) if not k.startswith("C") else vs}</div></div></section>'
            for k, fr, vs, t in cards)
        previa = ('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                  f'<title>{_html.escape(self.titulo)}</title><style>'
                  'body{font-family:system-ui,sans-serif;margin:0;padding:16px;background:#eceff1;color:#222}'
                  'body.noite{background:#1e1e1e;color:#ddd} h1{font-size:18px} h2{font-size:14px;margin:18px 0 6px} small{opacity:.6;font-weight:normal}'
                  '.lado{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:10px}'
                  '.card{font-family:arial;font-size:20px;text-align:center;background:white;color:black;padding:14px;border-radius:8px;max-width:520px}'
                  'body.noite .card{background:#2f2f31;color:#e8e8e8} .cloze{font-weight:bold;color:blue} body.noite .cloze{color:#6ea8ff}'
                  'button{padding:6px 12px;margin-bottom:8px}</style>'
                  '<h1>Prévia dos cards (frente | verso) — imita o modelo Básico/Cloze padrão do Anki</h1>'
                  '<button onclick="document.body.classList.toggle(\'noite\')">Alternar modo noturno</button>'
                  + pares + '</html>')
        (self.pasta / 'previa_cards.html').write_text(previa, encoding='utf-8')

    # ------------------------------------------------------------ tudo
    def gerar(self, sinais_resolvidos=None, imprimir=True):
        """Gera TSVs, registros e prévia; devolve {ID editorial: ID no TSV}."""
        self.montar_linhas()
        self.gravar_tsvs()
        self.registro_calibracao()
        self.registro_revisao(sinais_resolvidos or self.pasta / 'fonte' / 'sinais_resolvidos.json')
        self.gerar_previa()
        self.registrar_usos()
        mapa = {x['k']: self.rid(x['k']) for x in self.R + self.D}
        mapa.update({x['k']: f'anki_cloze.tsv:{i}' for i, x in enumerate(self.CZ, 1)})
        if imprimir:
            print(json.dumps(mapa, ensure_ascii=False))
            print('R', len(self.R), 'C/E', sum(x['g'] == 'C' for x in self.R), sum(x['g'] == 'E' for x in self.R))
            print('D', len(self.D), 'C/E', sum(x['g'] == 'C' for x in self.D), sum(x['g'] == 'E' for x in self.D))
            print('Cloze notas', len(self.CZ))
        return mapa
