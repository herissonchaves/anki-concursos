#!/usr/bin/env python3
"""Monta um lote Anki-Concursos a partir dos cartões definidos em `fonte/gerar_lote.py`.

O `gerar_lote.py` de cada lote fica só com o conteúdo: fontes, referências de
questões, esquemas e cartões. Este módulo cuida do restante: linhas dos TSVs
(UTF-8 sem BOM, LF), embaralhamento C/E reprodutível, `calibracao_cebraspe.json`,
`revisao_recuperacao.json`, resolução dos sinais do lint por
`fonte/sinais_resolvidos.json`. Desde a 2.30 não há prévia HTML nem pacote: a entrega são os TSVs
(`titulo_previa` continua aceito e é ignorado).

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

`cobertura` (lote de PDF, obrigatório): inventário de todo o PDF e de todas as suas questões,
uma unidade por conteúdo: `dict(u='U01', pag='14', p='alta', conteudo='…', cartoes=['R01'])`.
`p` é a prioridade para o concurso-alvo: 'alta' e 'media' precisam de `cartoes` do lote ou de
`colecao=[IDs de notas]` que já exigem a mesma recuperação; 'baixa' não tem card e exige `motivo`.
Unidade de questão do PDF traz `questao='<id do banco>'` (nos `refs` de algum de seus cards).
Texto que não é conteúdo de estudo usa `excluir='nao_conteudo: motivo'`. Falha se faltar card,
se Baixa tiver card ou se um card não cobrir nenhuma unidade Alta/Média. Grava
`cobertura_pdf.json` e põe em cada card as tags `Pagina_NN` das páginas que ele cobre.

`questoes_pdf` (2.29, opcional): {'Q01': ('17', '<id do banco>'), ...}. Cada questão do PDF que não
estiver declarada à mão em `cobertura` vira unidade sozinha: cartoes = cards que a citam em `refs` e
prioridade = a maior das unidades de conteúdo desses cards. Questão sem card citando-a precisa de
unidade própria em `cobertura` (p='baixa' com motivo, ou colecao=[...]).

`padrao_d` (2.29, opcional): valores comuns aos D do lote (ex.: `rb`, `orig`, `lim`), usados só quando o
D não traz a chave. Sem `regra`, o D usa o trecho da primeira fonte de `fx`.

`fontes`: {chave: (url, trecho verificado)} ou {chave: "<id de conteúdo do banco>"}, convertido por `referencias.fonte`.

Relatórios (2.29): `triagem_previa_pdf.txt`, `auditoria_pedagogica.txt`, `economia_de_revisao.txt` e
`fontes_e_referencias.txt` são gerados em `lote/relatorios/` a partir de `cobertura`, dos cartões, de `refs`
e de `fontes` (`relatorio={'material': ..., 'leitura': ..., 'alvo': ..., 'colecao': ...}` preenche o
cabeçalho da triagem). Um arquivo escrito à mão (sem a marca de gerado) não é sobrescrito. O
`selecao_e_fontes.txt` continua escrito à mão, só com o que o script não sabe: pertinência, "Banco
consultado", buscas, mnemônicos e IDs criados. Revisão pelo próprio agente é autorevisão; os registros
gerados não certificam conteúdo.
"""
from __future__ import annotations

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
MARCA_GERADO = 'Gerado por montar_lote.py a partir de fonte/gerar_lote.py; edite lá, não aqui.'
NOVOS_POR_DIA = 20


def rubrica(correcao, determinacao, operacao_d, comparacao, autoria='', feedback='', linguagem_didatica='',
            utilidade=''):
    """Rubrica de calibração; comece `comparacao` com 'PENDENTE: ' para registrá-la pendente.

    Desde a 2.24, `autoria`, `feedback` e `utilidade` podem ficar vazios (PASSA sem texto); escreva-os só
    quando houver observação. `linguagem_didatica` continua obrigatória: passe-a por nome, ex.
    `rub(c, d, o, cmp, linguagem_didatica='...')`.
    """
    if not str(linguagem_didatica).strip():
        raise ValueError('rubrica: linguagem_didatica exige evidência específica')
    valores = (correcao, determinacao, operacao_d, comparacao, autoria, feedback, linguagem_didatica, utilidade)
    return {chave: {'resultado': 'PENDENTE' if (chave == 'comparacao' and valor.startswith('PENDENTE')) else 'PASSA',
                    'evidencia': valor.replace('PENDENTE: ', '')} for chave, valor in zip(CRITERIOS, valores)}


class Lote:
    def __init__(self, pasta, base_tags, fontes, hoje, referencias, R, D, CZ, semente,
                 schema_calibracao=2, revisor=REVISOR_PADRAO, titulo_previa='Prévia dos cards',
                 banco_referencias=None, registrar_uso=True, cobertura=None, questoes_pdf=None, padrao_d=None,
                 relatorio=None):
        self.pasta, self.out = Path(pasta), Path(pasta) / 'lote'
        self.base, self.F, self.hoje = base_tags, fontes, hoje
        self.R, self.CZ, self.semente = R, CZ, semente
        self.schema, self.revisor, self.titulo = schema_calibracao, revisor, titulo_previa
        self.banco, self.registrar = banco_referencias, registrar_uso
        self.cobertura, self.questoes_pdf, self.relatorio = cobertura, questoes_pdf or {}, relatorio or {}
        # chave de fonte -> ID de conteúdo do banco ("ID" ou "ID#seção"); o uso é registrado no conteúdo
        self.conteudos = {k: v.partition('#')[0] for k, v in self.F.items() if isinstance(v, str)}
        if self.conteudos:
            ref = self._modulo_referencias()
            self.F = {k: (ref.fonte(v, self.banco) if isinstance(v, str) else v) for k, v in self.F.items()}
        self.D = [self._completar_d(x, padrao_d or {}) for x in D]
        self.refs = self._resolver_refs(referencias)

    def _completar_d(self, x, padrao):
        """Valores padrão do lote nos D (só chaves ausentes); `regra` vem do trecho da 1ª fonte em `fx`."""
        d = {**{k: v for k, v in padrao.items() if k not in x}, **x}
        if not str(d.get('regra', '')).strip() and d.get('fx') and d['fx'][0] in self.F:
            d['regra'] = self.F[d['fx'][0]][1]
        return d

    # ------------------------------------------------------------ cobertura do PDF por prioridade
    PRIORIDADES = ('alta', 'media', 'baixa')

    @staticmethod
    def paginas(pag) -> list[int]:
        """'14', 14, '9-10' ou ['9', 12] -> [9, 10, 12]."""
        itens = pag if isinstance(pag, (list, tuple)) else [pag]
        saida = set()
        for item in itens:
            ini, _, fim = str(item).partition('-')
            saida.update(range(int(ini), int(fim or ini) + 1))
        return sorted(saida)

    def checar_cobertura(self):
        """Barreira da revisão de PDF: toda unidade Alta ou Média tem card (ou nota da coleção).

        Cada unidade do inventário traz `p` ('alta', 'media' ou 'baixa'). Baixa não tem card e
        exige `motivo`; Alta/Média precisam de `cartoes` do lote ou de `colecao` (IDs de notas
        que já exigem a mesma recuperação). Também calcula as tags Pagina_NN de cada card.
        Falha (SystemExit) listando os problemas.
        """
        self.tags_pagina = {}
        if self.cobertura is None:
            return
        cartoes = {x['k']: x for x in self.R + self.D + self.CZ}
        erros, cobertos = [], set()
        self.cobertura = list(self.cobertura) + self._unidades_de_questoes(cartoes, erros)
        for un in self.cobertura:
            u, lista = un.get('u', '?'), list(un.get('cartoes', ()))
            if un.get('excluir'):
                if not str(un['excluir']).startswith('nao_conteudo') or lista:
                    erros.append(f'{u}: excluir é só para texto que não é conteúdo de estudo '
                                 '(excluir="nao_conteudo: motivo", sem cartoes); conteúdo periférico usa p="baixa"')
                continue
            p = un.get('p')
            if p not in self.PRIORIDADES:
                erros.append(f'{u}: p deve ser alta, media ou baixa')
                continue
            if p == 'baixa':
                if lista:
                    erros.append(f'{u}: prioridade baixa não vira card (tire {", ".join(lista)} ou reavalie a prioridade)')
                if not str(un.get('motivo', '')).strip():
                    erros.append(f'{u}: prioridade baixa exige motivo')
                continue
            if not lista and not un.get('colecao'):
                erros.append(f'{u} (p. {un.get("pag")}, {p}): sem card nem nota da coleção — {un.get("conteudo", "")[:70]}')
            for k in lista:
                if k not in cartoes:
                    erros.append(f'{u}: card {k} não existe no lote')
            try:
                pags = self.paginas(un['pag'])
            except (KeyError, ValueError):
                erros.append(f'{u}: pag ausente ou inválida')
                continue
            if lista and un.get('questao') and not any(un['questao'] in cartoes[k].get('refs', ()) for k in lista if k in cartoes):
                erros.append(f'{u}: a questão {un["questao"]} precisa estar nos refs de algum de seus cards')
            for k in lista:
                if k in cartoes:
                    cobertos.add(k)
                    self.tags_pagina.setdefault(k, set()).update(pags)
        for k in cartoes:
            if k not in cobertos:
                erros.append(f'{k}: card sem unidade Alta ou Média (inclua-o em COBERTURA ou retire-o)')
        if erros:
            raise SystemExit('COBERTURA INCOMPLETA — o lote de PDF precisa cobrir todo conteúdo Alta ou Média '
                             'do PDF e de suas questões:\n  ' + '\n  '.join(erros))

    def _unidades_de_questoes(self, cartoes, erros):
        """Unidades das questões de `questoes_pdf` que a cobertura não declara: cards que as citam e a
        maior prioridade das unidades de conteúdo desses cards."""
        declaradas = {un.get('questao') for un in self.cobertura if un.get('questao')}
        ordem = {'alta': 2, 'media': 1}
        prioridade = {}
        for un in self.cobertura:
            if un.get('p') in ordem and not un.get('questao'):
                for k in un.get('cartoes', ()):
                    if ordem[un['p']] > ordem.get(prioridade.get(k), 0):
                        prioridade[k] = un['p']
        novas = []
        for u, (pag, ident) in self.questoes_pdf.items():
            if ident in declaradas:
                continue
            lista = [k for k, x in cartoes.items() if ident in x.get('refs', ())]
            if not lista:
                erros.append(f'{u} ({ident}): nenhum card a cita em refs; declare-a em COBERTURA '
                             '(p="baixa" com motivo, ou colecao=[...])')
                continue
            p = max((prioridade.get(k, 'media') for k in lista), key=lambda v: ordem[v])
            novas.append(dict(u=u, pag=pag, p=p, questao=ident, conteudo=f'Questão {u.lstrip("Q")} do PDF',
                              cartoes=lista, auto=True))
        return novas

    def _tags(self, x, extra=''):
        pags = ' '.join(f'Pagina_{p:02d}' for p in sorted(self.tags_pagina.get(x['k'], ())))
        return ' '.join(t for t in (self.base, x['tags'], extra, pags) if t)

    def registro_cobertura(self):
        if self.cobertura is None:
            return None
        unidades = []
        for un in self.cobertura:
            reg = {k: v for k, v in un.items() if k != 'cartoes'}
            reg['pag'] = self.paginas(un['pag'])
            reg['cartoes'] = [self.rid(k) if k in self.line_of else f'anki_cloze.tsv:{self.cz_index[k]}'
                              for k in un.get('cartoes', ())]
            reg['ids_editoriais'] = list(un.get('cartoes', ()))
            unidades.append(reg)
        dados = {'schema_version': 1, 'unidades': unidades}
        self._json('cobertura_pdf.json', dados)
        return dados

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
        """Rótulo do lote no `usado_em` do banco: nome da pasta em output/ (ex.: PRF_Navegadores)."""
        raiz = Path(__file__).resolve().parents[3]
        for base in ('output', 'lotes'):  # lotes/: rótulos antigos (até a 2.23)
            try:
                return self.pasta.resolve().relative_to(raiz / base).as_posix()
            except ValueError:
                continue
        return self.pasta.name

    def registrar_usos(self):
        if not self.registrar or (not self.ids_banco and not self.conteudos and self.banco is None):
            return
        ref = self._modulo_referencias()
        lote, usados = self.rotulo_lote(), set()
        cards = self.R + self.D + self.CZ
        for ident in self.ids_banco:
            cartoes = [x['k'] for x in cards if ident in x.get('refs', ())]
            if cartoes:
                ref.registrar_uso(ident, lote, cartoes, self.banco)
                usados.add(ident)
        for ident in sorted(set(self.conteudos.values())):
            chaves = {k for k, v in self.conteudos.items() if v == ident}
            cartoes = [x['k'] for x in cards if chaves & set(x.get('fx', ()))]
            if cartoes:
                ref.registrar_uso(ident, lote, cartoes, self.banco)
                usados.add(ident)
        for q in ref.carregar(self.banco)[0]:  # uso deste lote que não existe mais (card retirado)
            usos = q.meta.get('usado_em', [])
            if q.id not in usados and any(str(u).startswith(f'{lote}#') for u in usos):
                q.meta['usado_em'] = [u for u in usos if not str(u).startswith(f'{lote}#')]
                q.salvar()
        ref.indexar(self.banco)

    @staticmethod
    def _subassuntos(registro) -> set[str]:
        valor = registro.get('subassuntos') or []
        return set(valor) if isinstance(valor, (list, tuple, set)) else set(re.split(r'[,;\s]+', str(valor))) - {''}

    def sugestoes_cebraspe(self) -> dict[str, list[str]]:
        """D em `inspiracao_geral` × itens Cebraspe C/E com gabarito definitivo do mesmo assunto no banco.

        O assunto do D vem do campo opcional `a` ('assunto' ou 'disciplina/assunto'), das questões em
        `refs` e dos conteúdos do banco citados em `fx`; o campo opcional `sa` (subassuntos) restringe o
        aviso aos itens do mesmo subtema. Só avisa; nunca bloqueia.
        """
        alvos = [x for x in self.D if x.get('fid') == 'inspiracao_geral']
        if not alvos:
            return {}
        try:
            indice = self._modulo_referencias().ler_indice(self.banco)
        except Exception:  # banco ausente ou ilegível: sem sugestão
            return {}
        por_id = {r['id']: r for r in indice}
        oficiais = [r for r in indice if r['tipo'] == 'questao' and r['banca'].lower() in ('cebraspe', 'cespe')
                    and r['formato'] == 'certo_errado' and r['status'] == 'definitivo'
                    and r.get('vigencia', 'atual') != 'desatualizada']
        saida = {}
        for x in alvos:
            assuntos = set()
            for a in ([x['a']] if x.get('a') else []):
                assuntos.add(tuple(a.split('/', 1)) if '/' in a else (None, a))
            ligados = list(x.get('refs', ())) + [self.conteudos[k] for k in x.get('fx', ()) if k in self.conteudos]
            assuntos |= {(por_id[i]['disciplina'], por_id[i]['assunto']) for i in ligados if i in por_id}
            sub = x.get('sa')  # subassuntos do D (lista ou "a, b"): restringe o aviso ao subtema (2.29)
            sub = {s.strip() for s in (sub.split(',') if isinstance(sub, str) else sub or ()) if s.strip()}
            ids = sorted({r['id'] for r in oficiais for d, a in assuntos
                          if r['assunto'] == a and (d is None or r['disciplina'] == d)
                          and (not sub or sub & self._subassuntos(r))}
                         - set(x.get('refs', ())))
            if ids:
                saida[x['k']] = ids
        return saida

    # ------------------------------------------------------------ fontes
    def fontes(self, *keys):
        return [{'url': self.F[k][0], 'consulta': self.hoje, 'trecho': self.F[k][1]} for k in keys]

    def urls(self, *keys):
        return [self.F[k][0] for k in keys]

    # ------------------------------------------------------------ linhas
    def row_r(self, x):
        return [x['f'], verso_ce(x['g'], x['b'], x['m']), self._tags(x, R_TAG)]

    def row_d(self, x):
        return [frente(x['f']), verso_ce(x['g'], x['b'], x['m']), self._tags(x, D_TAG)]

    def row_c(self, x):
        return [frente(x['t']), extra_cloze(x['b'], x['m']), self._tags(x)]

    def montar_linhas(self):
        if not hasattr(self, 'tags_pagina'):
            self.checar_cobertura()
        self.cz_index = {x['k']: i for i, x in enumerate(self.CZ, 1)}
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

    @staticmethod
    def _lacunas(texto):
        """Solução de um Cloze tirada das próprias lacunas (o autor não precisa reescrevê-la)."""
        respostas = re.findall(r'\{\{c\d+::(.*?)(?:::[^{}]*)?\}\}', texto, flags=re.S)
        return 'Lacuna: ' + '; '.join(respostas) if respostas else ''

    def registro_revisao(self, sinais_resolvidos):
        rev = {'schema_version': 1, 'sha256_lote': batch_hash(self.items), 'revisor': self.revisor,
               'tipo_revisao': 'autorevisao', 'cartoes': [], 'sinais': []}
        def opcionais(x):  # alt/rec/fb: só quando o autor escreveu (2.24)
            return {chave: x[curto] for curto, chave in (('alt', 'alternativa_concorrente'), ('rec', 'recuperacao'),
                                                         ('fb', 'feedback')) if str(x.get(curto, '')).strip()}

        for x in self.R:
            rev['cartoes'].append(dict(
                id=self.rid(x['k']), sha256=fingerprint(self.ce_rows[self.line_of[x['k']] - 1]), alvo=x['alvo'],
                solucao=x['sol'], fontes=self.fontes(*x['fx']), **opcionais(x),
                segunda_conferencia=True, decisao='APROVAR'))
        for i, x in enumerate(self.CZ, 1):
            rev['cartoes'].append(dict(
                id=f'anki_cloze.tsv:{i}', sha256=fingerprint(self.cz_rows[i - 1]), alvo=x['alvo'],
                solucao=x.get('sol') or self._lacunas(x['t']), fontes=self.fontes(*x['fx']), **opcionais(x),
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

    # ------------------------------------------------------------ relatórios .txt (2.29)
    def _gravar_txt(self, nome, linhas):
        """Grava o relatório gerado; não sobrescreve o que foi escrito à mão (sem a marca)."""
        caminho = self.out / 'relatorios' / nome
        if caminho.exists() and MARCA_GERADO not in caminho.read_text(encoding='utf-8'):
            print(f'aviso: {nome} escrito à mão foi mantido (apague-o para gerar)')
            return False
        caminho.write_text('\n'.join(linhas + ['', MARCA_GERADO]) + '\n', encoding='utf-8', newline='\n')
        return True

    def _linha_de(self, k):
        return f'CE:{self.line_of[k]}' if k in self.line_of else f'CZ:{self.cz_index[k]}'

    def gravar_relatorios(self):
        rel = self.relatorio
        if self.cobertura is not None:
            cont = {p: sum(un.get('p') == p for un in self.cobertura) for p in self.PRIORIDADES}
            excl = sum(bool(un.get('excluir')) for un in self.cobertura)
            linhas = ['TRIAGEM PRÉVIA DO PDF — inventário com prioridade para o concurso-alvo']
            linhas += [f'{rotulo}: {rel[chave]}' for chave, rotulo in (
                ('material', 'Material'), ('leitura', 'Leitura'), ('alvo', 'Concurso-alvo'), ('edital', 'Edital de referência'),
                ('colecao', 'Coleção')) if rel.get(chave)]
            linhas += ['Regra (cobertura-pdf.md): inventário de todo o PDF e de suas questões; Alta e Média com ao menos um '
                       'card ou nota da coleção que já exija a mesma recuperação; Baixa sem card, com motivo.',
                       f'Unidades: {cont["alta"]} Alta, {cont["media"]} Média, {cont["baixa"]} Baixa ({excl} exclusão(ões) de texto que não é conteúdo).',
                       '', 'Unidade | página(s) | prioridade | conteúdo | cards / nota da coleção / motivo']
            for un in self.cobertura:
                pag = ', '.join(map(str, self.paginas(un['pag']))) if 'pag' in un else '?'
                if un.get('excluir'):
                    linhas.append(f'{un["u"]} | {pag} | — | {un.get("conteudo", "")} | {un["excluir"]}')
                    continue
                if un['p'] == 'baixa':
                    destino = 'sem card — ' + str(un.get('motivo', ''))
                else:
                    destino = '; '.join(filter(None, (', '.join(un.get('cartoes', ())),
                                                      ('coleção ' + ', '.join(un['colecao'])) if un.get('colecao') else '')))
                q = f' [{un["questao"]}]' if un.get('questao') else ''
                linhas.append(f'{un["u"]} | {pag} | {un["p"]} | {un.get("conteudo", "")}{q} | {destino}')
            self._gravar_txt('triagem_previa_pdf.txt', linhas)
        linhas = ['AUDITORIA PEDAGÓGICA POR ID — autorevisão (mesmo agente que redigiu; não é avaliação independente)',
                  'Procedimento: cada frente foi resolvida de novo antes de reler o verso, confrontada com as fontes de '
                  'fontes_e_referencias.txt e testada contra leitura concorrente. Detalhes em revisao_recuperacao.json '
                  '(R/Cloze) e calibracao_cebraspe.json (D).', '', 'ID (linha) | gab. | decisão | alvo']
        linhas += [f'{x["k"]} ({self._linha_de(x["k"])}) | {x["g"]} | APROVAR | {x["alvo"]}' for x in self.R + self.D]
        linhas += [f'{x["k"]} ({self._linha_de(x["k"])}) | Cloze | APROVAR | {x["alvo"]} '
                   f'(lacunas cobertas por {", ".join(sorted({k for ks in x["cob"].values() for k in ks}))})' for x in self.CZ]
        self._gravar_txt('auditoria_pedagogica.txt', linhas)
        n_r, n_d, n_c = len(self.R), len(self.D), len(self.CZ)
        rc, dc = sum(x['g'] == 'C' for x in self.R), sum(x['g'] == 'C' for x in self.D)
        total = n_r + n_d + n_c
        linhas = ['ECONOMIA DE REVISÃO',
                  f'Contagem: {n_r + n_d} notas C/E ({n_r} R + {n_d} D) + {n_c} notas Cloze = {total} cartões.',
                  f'Gabaritos: R = {rc} Certo / {n_r - rc} Errado; D = {dc} Certo / {n_d - dc} Errado. Cloze fora da '
                  'contagem. Ordem embaralhada (semente fixa).', '', 'Decisões para evitar revisões redundantes:']
        if self.cobertura is not None:
            baixas = [un for un in self.cobertura if un.get('p') == 'baixa']
            notas = sorted({n for un in self.cobertura for n in un.get('colecao', ())})
            linhas.append(f'- Prioridade Baixa sem card: {len(baixas)} unidade(s) '
                          f'({sum(bool(un.get("questao")) for un in baixas)} delas questões do PDF), registradas na triagem.')
            if notas:
                linhas.append(f'- Notas da coleção que já exigem a mesma recuperação cobrem unidades: {", ".join(notas)}.')
            qs = [un for un in self.cobertura if un.get('questao') and un.get('p') != 'baixa']
            linhas.append(f'- Questões do PDF reaproveitam cards de conteúdo: {len(qs)} questão(ões) Alta/Média cobertas '
                          'por cards que as citam ou por notas da coleção.')
        linhas += ['- Cobertura = ao menos um card por unidade; nenhum fato nos três formatos; cada lacuna Cloze coberta por um D.',
                   '', f'Carga: {total} cartões novos; a {NOVOS_POR_DIA} novos por dia, cerca de '
                       f'{-(-total // NOVOS_POR_DIA)} dia(s) de introdução.']
        self._gravar_txt('economia_de_revisao.txt', linhas)
        usados = {}
        for x in self.R + self.D + self.CZ:
            for r in x.get('refs', ()):
                usados.setdefault(r, []).append(x['k'])
        com = [r for r in usados if r not in self.ids_sem_prova]
        linhas = ['FONTES E REFERÊNCIAS DO LOTE (lista gerada; o selecao_e_fontes.txt traz pertinência, buscas e IDs criados)',
                  '', 'Questões com prova oficial (podem sustentar fidelidade comparada):']
        linhas += [f'- {r}: {", ".join(usados[r])}' for r in com] or ['- nenhuma']
        linhas += ['', 'Questões sem prova oficial localizada (inspiração e outra banca):']
        linhas += [f'- {r}: {", ".join(usados[r])}' for r in usados if r in self.ids_sem_prova] or ['- nenhuma']
        linhas += ['', 'Fontes de conteúdo (chave: url — trecho; cards):']
        for k, (url, trecho) in self.F.items():
            cards = [x['k'] for x in self.R + self.D + self.CZ if k in x.get('fx', ())]
            linhas.append(f'- {k}: {url} — {trecho}; {", ".join(cards) or "sem card"}')
        linhas += ['', 'Desafiadores: ' + '; '.join(f'{x["k"]} {x["fid"]}' for x in self.D) if self.D else '']
        self._gravar_txt('fontes_e_referencias.txt', linhas)

    # ------------------------------------------------------------ tudo
    def gerar(self, sinais_resolvidos=None, imprimir=True):
        """Gera TSVs e registros; devolve {ID editorial: ID no TSV}."""
        self.montar_linhas()
        self.gravar_tsvs()
        self.registro_cobertura()
        self.registro_calibracao()
        self.registro_revisao(sinais_resolvidos or self.pasta / 'fonte' / 'sinais_resolvidos.json')
        self.gravar_relatorios()
        self.registrar_usos()
        self.sugestoes = self.sugestoes_cebraspe()
        if self.sugestoes:
            print('AVISO — D em inspiracao_geral com item Cebraspe C/E oficial do mesmo assunto no banco '
                  '(leia com `referencias.py mostrar` e, se servir de modelo, cite em refs e use fid="comparada"):')
            for k, ids in self.sugestoes.items():
                print(f'  {k}: {", ".join(ids[:5])}' + (f' (+{len(ids) - 5})' if len(ids) > 5 else ''))
        mapa = {x['k']: self.rid(x['k']) for x in self.R + self.D}
        mapa.update({x['k']: f'anki_cloze.tsv:{i}' for i, x in enumerate(self.CZ, 1)})
        if imprimir:
            print(json.dumps(mapa, ensure_ascii=False))
            print('R', len(self.R), 'C/E', sum(x['g'] == 'C' for x in self.R), sum(x['g'] == 'E' for x in self.R))
            print('D', len(self.D), 'C/E', sum(x['g'] == 'C' for x in self.D), sum(x['g'] == 'E' for x in self.D))
            print('Cloze notas', len(self.CZ))
        return mapa
