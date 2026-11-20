#!/usr/bin/env python3
"""Banco de questões de concursos de referência (`referencias/` na raiz do repositório).

Cada questão é um Markdown com frontmatter padronizado em
`referencias/questoes/<disciplina>/<assunto>/<id>.md`. O índice `indice.tsv` e a
árvore `assuntos.md` são gerados por este script e permitem localizar questões sem
abrir os arquivos. Só a biblioteca padrão é usada.

Comandos (rode na raiz do repositório):

  python -X utf8 skills/referencias-questoes/scripts/referencias.py assuntos
  ... buscar -d informatica -a correio_eletronico -t smtp [--corpo] [-n 20]
  ... mostrar ID [ID ...] [--analise] [--meta]
  ... nova QUESTOES.json            (ou "-" para ler da entrada padrão)
  ... usar ID [ID ...] --lote PRF/Missao_09_Tema --cartoes D01,D02
  ... calibracao ID [ID ...]        (JSON para calibracao_cebraspe.json v2)
  ... validar
  ... indexar [--atualizar-hash]

`--raiz PASTA` (ou a variável ANKI_REFERENCIAS) troca a pasta do banco.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

AQUI = Path(__file__).resolve()
REPO = AQUI.parents[3]
RAIZ_PADRAO = REPO / 'referencias'
DISCIPLINAS_JSON = AQUI.parents[2] / 'perfil-carreiras-policiais' / 'references' / 'disciplinas.json'

NL = 'nao_localizado'
CAMPOS = ('id', 'tipo', 'banca', 'formato', 'ano', 'orgao', 'concurso', 'cargo', 'caderno', 'item',
          'disciplina', 'assunto', 'subassuntos', 'palavras_chave', 'gabarito', 'gabarito_status',
          'url', 'gabarito_url', 'origem', 'fonte_descoberta', 'consulta', 'concursos_alvo',
          'operacao_observada', 'usado_em', 'hash')
LISTAS = {'subassuntos', 'palavras_chave', 'concursos_alvo', 'usado_em'}
FORMATOS = {'certo_errado', 'multipla_escolha'}
STATUS = {'definitivo', 'justificativa_oficial', 'nao_verificado', 'anulado'}
ORIGENS = {'anexo_usuario', 'pesquisa_internet', 'caderno_erros'}
GABARITOS = {'certo_errado': {'C', 'E', 'anulada'}, 'multipla_escolha': {'A', 'B', 'C', 'D', 'E', 'anulada'}}
COLUNAS = ('id', 'disciplina', 'assunto', 'subassuntos', 'banca', 'formato', 'ano', 'gabarito', 'status',
           'orgao', 'cargo', 'alvos', 'usos', 'palavras', 'arquivo')
SNAKE = re.compile(r'^[a-z0-9]+(?:_[a-z0-9]+)*$')
DATA = re.compile(r'^\d{4}-\d{2}-\d{2}$')
SEGURO = re.compile(r'^[A-Za-z0-9_./-]*[A-Za-z_./-][A-Za-z0-9_./-]*$')
DADOS_PESSOAIS = [
    (re.compile(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b'), 'CPF'),
    (re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'), 'e-mail'),
    (re.compile(r'licenciad[oa] para|licensed to', re.IGNORECASE), "marca-d'água de licença"),
]


class ErroBanco(Exception):
    """Falha de uso do banco (questão inexistente, dado inválido)."""


# ------------------------------------------------------------------ utilidades
def raiz_banco(raiz=None) -> Path:
    return Path(raiz or os.environ.get('ANKI_REFERENCIAS') or RAIZ_PADRAO)


def normalizar(texto: str) -> str:
    """Minúsculas sem acentos, só letras/números separados por espaço (para busca e hash)."""
    texto = unicodedata.normalize('NFKD', str(texto))
    texto = ''.join(c for c in texto if not unicodedata.combining(c)).casefold()
    return ' '.join(re.findall(r'[a-z0-9]+', texto))


def slug(texto: str) -> str:
    return normalizar(texto).replace(' ', '-')


def calcular_hash(enunciado: str, alternativas: str = '') -> str:
    return hashlib.sha256(normalizar(f'{enunciado} {alternativas}').encode('utf-8')).hexdigest()[:16]


# ------------------------------------------------------------------ frontmatter restrito
def _valor(bruto: str):
    bruto = bruto.strip()
    if bruto.startswith('"'):
        return json.loads(bruto)
    if bruto.startswith('['):
        if not bruto.endswith(']'):
            raise ValueError(f'lista sem "]": {bruto}')
        itens, resto = [], bruto[1:-1].strip()
        decod = json.JSONDecoder()
        while resto:
            if resto.startswith('"'):
                item, fim = decod.raw_decode(resto)
                resto = resto[fim:].lstrip()
            else:
                item, _, resto = resto.partition(',')
                item, resto = item.strip(), ',' + resto if _ else ''
            itens.append(item)
            resto = resto.lstrip()
            if resto.startswith(','):
                resto = resto[1:].lstrip()
            elif resto:
                raise ValueError(f'lista malformada: {bruto}')
        return itens
    if re.fullmatch(r'-?\d+', bruto):
        return int(bruto)
    return bruto


def _escrever_valor(valor) -> str:
    if isinstance(valor, list):
        return '[' + ', '.join(_escrever_valor(str(v)) for v in valor) + ']'
    if isinstance(valor, int):
        return str(valor)
    valor = str(valor)
    return valor if SEGURO.match(valor) else json.dumps(valor, ensure_ascii=False)


def ler_documento(texto: str) -> tuple[dict, str]:
    texto = texto.replace('\r\n', '\n').lstrip('﻿')
    if not texto.startswith('---\n'):
        raise ValueError('arquivo sem frontmatter (deve começar com ---)')
    fim = texto.find('\n---\n', 4)
    if fim < 0:
        raise ValueError('frontmatter sem fechamento ---')
    meta = {}
    for n, linha in enumerate(texto[4:fim].split('\n'), 2):
        if not linha.strip():
            continue
        chave, sep, bruto = linha.partition(':')
        if not sep or not re.fullmatch(r'[a-z_]+', chave):
            raise ValueError(f'linha {n} do frontmatter inválida: {linha!r}')
        meta[chave] = _valor(bruto)
    return meta, texto[fim + 5:]


def escrever_documento(meta: dict, corpo: str) -> str:
    linhas = [f'{c}: {_escrever_valor(meta[c])}' for c in CAMPOS if c in meta]
    return '---\n' + '\n'.join(linhas) + '\n---\n' + corpo.rstrip('\n') + '\n'


def secoes(corpo: str) -> dict[str, str]:
    partes, atual = {}, None
    for linha in corpo.split('\n'):
        if linha.startswith('## '):
            atual = normalizar(linha[3:])
            partes[atual] = []
        elif atual:
            partes[atual].append(linha)
    return {k: '\n'.join(v).strip() for k, v in partes.items()}


# ------------------------------------------------------------------ questões
@dataclass
class Questao:
    meta: dict
    corpo: str
    caminho: Path

    @property
    def id(self):
        return self.meta.get('id', self.caminho.stem)

    def hash_corpo(self):
        s = secoes(self.corpo)
        return calcular_hash(s.get('enunciado', ''), s.get('alternativas', ''))

    def salvar(self):
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(self.caminho, 'w', encoding='utf-8', newline='\n') as f:
            f.write(escrever_documento(self.meta, self.corpo))


def arquivos(raiz=None):
    return sorted((raiz_banco(raiz) / 'questoes').rglob('*.md'))


ESTADO = '.estado_indice'  # assinatura local dos arquivos indexados (não versionada)


def assinatura(raiz=None) -> str:
    """Resumo de caminho, mtime (ns) e tamanho de cada questão: muda a cada edição."""
    base = raiz_banco(raiz)
    partes = []
    for p in arquivos(raiz):
        st = p.stat()
        partes.append(f'{p.relative_to(base).as_posix()}|{st.st_mtime_ns}|{st.st_size}')
    return hashlib.sha256('\n'.join(partes).encode('utf-8')).hexdigest()


def ler_questao(caminho: Path) -> Questao:
    meta, corpo = ler_documento(caminho.read_text(encoding='utf-8'))
    return Questao(meta, corpo, caminho)


def carregar(raiz=None) -> tuple[list[Questao], list[str]]:
    questoes, erros = [], []
    for caminho in arquivos(raiz):
        try:
            questoes.append(ler_questao(caminho))
        except (ValueError, json.JSONDecodeError) as exc:
            erros.append(f'{caminho.name}: {exc}')
    return questoes, erros


def disciplinas_conhecidas() -> set[str]:
    try:
        dados = json.loads(DISCIPLINAS_JSON.read_text(encoding='utf-8'))
        return {s['id'] for s in dados['subjects']}
    except (OSError, KeyError, ValueError):
        return set()


def _url_ok(valor) -> bool:
    return isinstance(valor, str) and bool(re.match(r'https?://\S+$', valor))


def validar_questao(q: Questao, raiz=None) -> tuple[list[str], list[str]]:
    m, erros, avisos = q.meta, [], []
    p = f'{q.caminho.name}'
    for campo in CAMPOS:
        valor = m.get(campo)
        if campo in LISTAS:
            if not isinstance(valor, list):
                erros.append(f'{p}: {campo} deve ser lista [..]')
            elif campo != 'usado_em' and not [v for v in valor if str(v).strip()]:
                erros.append(f'{p}: {campo} vazio')
        elif valor is None or str(valor).strip() == '':
            erros.append(f'{p}: {campo} ausente ou vazio')
    extras = set(m) - set(CAMPOS)
    if extras:
        erros.append(f'{p}: campos desconhecidos {sorted(extras)}')
    if erros:
        return erros, avisos
    if m['id'] != q.caminho.stem:
        erros.append(f'{p}: id {m["id"]!r} difere do nome do arquivo')
    if m['tipo'] != 'questao':
        erros.append(f'{p}: tipo deve ser questao')
    if m['formato'] not in FORMATOS:
        erros.append(f'{p}: formato deve ser certo_errado ou multipla_escolha')
    elif str(m['gabarito']) not in GABARITOS[m['formato']]:
        erros.append(f'{p}: gabarito {m["gabarito"]!r} inválido para {m["formato"]}')
    if m['gabarito_status'] not in STATUS:
        erros.append(f'{p}: gabarito_status deve ser um de {sorted(STATUS)}')
    if m['origem'] not in ORIGENS:
        erros.append(f'{p}: origem deve ser um de {sorted(ORIGENS)}')
    ano_max = _dt.date.today().year + 1
    if not isinstance(m['ano'], int) or not 1980 <= m['ano'] <= ano_max:
        erros.append(f'{p}: ano deve ser inteiro entre 1980 e {ano_max}')
    if not DATA.match(str(m['consulta'])):
        erros.append(f'{p}: consulta deve ser AAAA-MM-DD')
    for campo in ('disciplina', 'assunto'):
        if not SNAKE.match(str(m[campo])):
            erros.append(f'{p}: {campo} deve ser snake_case sem acentos')
    for sub in m['subassuntos']:
        if not SNAKE.match(str(sub)):
            erros.append(f'{p}: subassunto {sub!r} deve ser snake_case sem acentos')
    if m['url'] != NL and not _url_ok(m['url']):
        erros.append(f'{p}: url deve ser http(s) ou {NL}')
    if m['gabarito_status'] in ('definitivo', 'justificativa_oficial'):
        if not _url_ok(m['gabarito_url']):
            erros.append(f'{p}: gabarito_url obrigatório para gabarito {m["gabarito_status"]}')
    elif m['gabarito_url'] != NL and not _url_ok(m['gabarito_url']):
        erros.append(f'{p}: gabarito_url deve ser http(s) ou {NL}')
    for uso in m['usado_em']:
        if not re.fullmatch(r'\S+#\S+', str(uso)):
            erros.append(f'{p}: usado_em {uso!r} deve ser LOTE#CARTOES (ex.: PRF/Missao_09_Tema#D01,D02)')
    esperado = Path(raiz_banco(raiz), 'questoes', str(m['disciplina']), str(m['assunto']), q.caminho.name)
    if q.caminho.resolve() != esperado.resolve():
        erros.append(f'{p}: deveria estar em questoes/{m["disciplina"]}/{m["assunto"]}/')
    s = secoes(q.corpo)
    for nome in ('enunciado', 'gabarito') + (('alternativas',) if m['formato'] == 'multipla_escolha' else ()):
        if not s.get(nome):
            erros.append(f'{p}: seção "## {nome.capitalize()}" ausente ou vazia')
    if s.get('enunciado') and m['hash'] != q.hash_corpo():
        erros.append(f'{p}: hash desatualizado (enunciado/alternativas mudaram); rode indexar --atualizar-hash')
    for padrao, nome in DADOS_PESSOAIS:
        if padrao.search(q.corpo):
            erros.append(f'{p}: possível dado pessoal ({nome}) no texto; remova antes de salvar')
    conhecidas = disciplinas_conhecidas()
    if conhecidas and m['disciplina'] not in conhecidas:
        avisos.append(f'{p}: disciplina {m["disciplina"]!r} fora de disciplinas.json (confira a grafia)')
    return erros, avisos


def validar(raiz=None) -> tuple[list[Questao], list[str], list[str]]:
    questoes, erros = carregar(raiz)
    avisos, validas, por_hash, por_id = [], [], {}, {}
    for q in questoes:
        e, a = validar_questao(q, raiz)
        erros += e
        avisos += a
        if not e:
            validas.append(q)
        h = q.meta.get('hash')
        if h in por_hash:
            erros.append(f'{q.caminho.name}: mesma questão (hash) que {por_hash[h]}')
        por_hash.setdefault(h, q.id)
        if q.id in por_id:
            erros.append(f'{q.caminho.name}: id repetido em {por_id[q.id]}')
        por_id.setdefault(q.id, str(q.caminho))
    return validas, erros, avisos


# ------------------------------------------------------------------ índice
def _celula(valor) -> str:
    if isinstance(valor, list):
        valor = ';'.join(str(v) for v in valor)
    return re.sub(r'[\t\r\n]+', ' ', str(valor)).strip()


def linha_indice(q: Questao, raiz=None) -> dict:
    m = q.meta
    return {'id': q.id, 'disciplina': m['disciplina'], 'assunto': m['assunto'], 'subassuntos': m['subassuntos'],
            'banca': m['banca'], 'formato': m['formato'], 'ano': m['ano'], 'gabarito': m['gabarito'],
            'status': m['gabarito_status'], 'orgao': m['orgao'], 'cargo': m['cargo'],
            'alvos': m['concursos_alvo'], 'usos': len(m['usado_em']), 'palavras': m['palavras_chave'],
            'arquivo': q.caminho.relative_to(raiz_banco(raiz)).as_posix()}


def _ordem(linha):
    return (linha['disciplina'], linha['assunto'], -int(linha['ano']), linha['id'])


def indexar(raiz=None, atualizar_hash=False) -> tuple[int, list[str], list[str]]:
    base = raiz_banco(raiz)
    if atualizar_hash:
        for q in carregar(raiz)[0]:
            if secoes(q.corpo).get('enunciado') and q.meta.get('hash') != q.hash_corpo():
                q.meta['hash'] = q.hash_corpo()
                q.salvar()
    validas, erros, avisos = validar(raiz)
    linhas = sorted((linha_indice(q, raiz) for q in validas), key=_ordem)
    base.mkdir(parents=True, exist_ok=True)
    with open(base / 'indice.tsv', 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(COLUNAS) + '\n')
        for linha in linhas:
            f.write('\t'.join(_celula(linha[c]) for c in COLUNAS) + '\n')
    with open(base / 'assuntos.md', 'w', encoding='utf-8', newline='\n') as f:
        f.write(arvore_assuntos(linhas))
    (base / ESTADO).write_text(assinatura(raiz), encoding='utf-8')
    return len(linhas), erros, avisos


def arvore_assuntos(linhas) -> str:
    saida = ['# Assuntos do banco de referências', '',
             'Gerado por `referencias.py indexar`; não editar à mão. '
             f'Total: {len(linhas)} questões. Formato: assunto (n): subassuntos · bancas.', '']
    discs = {}
    for l in linhas:
        discs.setdefault(l['disciplina'], {}).setdefault(l['assunto'], []).append(l)
    for disc, assuntos in sorted(discs.items()):
        saida.append(f'- **{disc}** ({sum(len(v) for v in assuntos.values())})')
        for assunto, itens in sorted(assuntos.items()):
            subs, bancas = {}, {}
            for l in itens:
                for s in l['subassuntos']:
                    subs[s] = subs.get(s, 0) + 1
                bancas[l['banca']] = bancas.get(l['banca'], 0) + 1
            fmt = lambda d: ', '.join(f'{k} {v}' for k, v in sorted(d.items(), key=lambda kv: (-kv[1], kv[0])))
            saida.append(f'  - {assunto} ({len(itens)}): {fmt(subs)} · {fmt(bancas)}')
    return '\n'.join(saida) + '\n'


def ler_indice(raiz=None, reindexar=True) -> list[dict]:
    base = raiz_banco(raiz)
    indice = base / 'indice.tsv'
    fontes = arquivos(raiz)
    linhas = indice.read_text(encoding='utf-8').splitlines() if indice.exists() else []
    estado = base / ESTADO
    gravado = estado.read_text(encoding='utf-8').strip() if estado.exists() else ''
    desatualizado = not linhas or gravado != assinatura(raiz)
    if reindexar and desatualizado and (fontes or indice.exists()):
        _, erros, _ = indexar(raiz)
        for e in erros:
            print(f'aviso: questão fora do índice: {e}', file=sys.stderr)
        linhas = indice.read_text(encoding='utf-8').splitlines()
    if not linhas:
        return []
    cab = linhas[0].split('\t')
    saida = []
    for linha in linhas[1:]:
        reg = dict(zip(cab, linha.split('\t')))
        for c in ('subassuntos', 'alvos', 'palavras'):
            reg[c] = [v for v in reg.get(c, '').split(';') if v]
        reg['ano'], reg['usos'] = int(reg['ano']), int(reg['usos'])
        saida.append(reg)
    return saida


# ------------------------------------------------------------------ consultas
def buscar(raiz=None, disciplina=None, assunto=None, termos=(), banca=None, formato=None, ano_min=None,
           alvo=None, nao_usadas=False, corpo=False) -> list[dict]:
    base = raiz_banco(raiz)
    termos = [normalizar(t) for t in termos if normalizar(t)]
    saida = []
    for reg in ler_indice(raiz):
        if disciplina and normalizar(disciplina).replace(' ', '_') != reg['disciplina']:
            continue
        if assunto and not reg['assunto'].startswith(normalizar(assunto).replace(' ', '_')):
            continue
        if banca and normalizar(banca) not in normalizar(reg['banca']):
            continue
        if formato and formato != reg['formato']:
            continue
        if ano_min and reg['ano'] < ano_min:
            continue
        if alvo and alvo.upper() not in [a.upper() for a in reg['alvos']]:
            continue
        if nao_usadas and reg['usos']:
            continue
        if termos:
            alvo_txt = normalizar(' '.join([reg['id'], reg['assunto'], *reg['subassuntos'], *reg['palavras'],
                                            reg['orgao'], reg['cargo'], reg['banca']]).replace('_', ' '))
            if corpo:
                alvo_txt += ' ' + normalizar(ler_questao(base / reg['arquivo']).corpo)
            if not all(t in alvo_txt for t in termos):
                continue
        saida.append(reg)
    return saida


def localizar(ids, raiz=None) -> list[Questao]:
    mapa = {r['id']: r['arquivo'] for r in ler_indice(raiz)}
    base, saida = raiz_banco(raiz), []
    for i in ids:
        if i in mapa:
            saida.append(ler_questao(base / mapa[i]))
            continue
        achados = [p for p in arquivos(raiz) if p.stem == i]
        if not achados:
            raise ErroBanco(f'questão {i!r} não encontrada no banco ({base})')
        saida.append(ler_questao(achados[0]))
    return saida


def calibracao(*ids, raiz=None) -> list[dict]:
    """Referências no formato de `calibracao_cebraspe.json` (schema 2) para os IDs dados."""
    refs = []
    for q in localizar(ids, raiz):
        m = q.meta
        if not _url_ok(m.get('url')):
            raise ErroBanco(f'{q.id}: sem url da prova (nao_localizado); localize a fonte oficial antes de usá-la '
                            'como referência de calibração')
        ref = {k: m[k] for k in ('banca', 'formato', 'concurso', 'cargo', 'ano', 'caderno')}
        ref = {'id': q.id, **ref, 'item': str(m['item']), 'url': m['url'], 'consulta': m['consulta'],
               'operacao_observada': m['operacao_observada'], 'gabarito_status': m['gabarito_status']}
        if _url_ok(m.get('gabarito_url')):
            ref['gabarito_url'] = m['gabarito_url']
        refs.append(ref)
    return refs


def registrar_uso(ident, lote, cartoes, raiz=None) -> bool:
    """Registra (ou substitui) o uso da questão no lote. Devolve True se o arquivo mudou."""
    q = localizar([ident], raiz)[0]
    entrada = f'{lote}#{",".join(cartoes)}'
    usos = [u for u in q.meta.get('usado_em', []) if not str(u).startswith(f'{lote}#')] + [entrada]
    if usos == q.meta.get('usado_em'):
        return False
    q.meta['usado_em'] = usos
    q.salvar()
    return True


# ------------------------------------------------------------------ criação
def _corpo_novo(d: dict) -> str:
    rotulo = {'C': 'Certo', 'E': 'Errado', 'anulada': 'Anulada'}.get(str(d['gabarito']), f'Letra {d["gabarito"]}')
    partes = [f'# {d["banca"]} {d["ano"]} — {d["orgao"]} — item {d["item"]}', '', '## Enunciado', '']
    if d.get('texto_base'):
        partes += ['> ' + l if l else '>' for l in str(d['texto_base']).strip().split('\n')] + ['']
    partes += [str(d['enunciado']).strip(), '']
    alternativas = d.get('alternativas')
    if alternativas:
        if isinstance(alternativas, dict):
            alternativas = [f'{k}) {v}' for k, v in alternativas.items()]
        partes += ['## Alternativas', ''] + [f'- {a}' for a in alternativas] + ['']
    link = f' ([gabarito oficial]({d["gabarito_url"]}))' if _url_ok(d.get('gabarito_url')) else ''
    partes += ['## Gabarito', '', f'**{rotulo}** — {d["gabarito_status"].replace("_", " ")}{link}', '']
    if d.get('analise'):
        partes += ['## Análise', '', str(d['analise']).strip(), '']
    return '\n'.join(partes)


def novo_id(d: dict, h: str, raiz=None) -> str:
    item = slug(d.get('item', '')) if str(d.get('item', NL)) != NL else h[:6]
    item = item.zfill(3) if item.isdigit() else item
    base = '-'.join(filter(None, (slug(d['banca']), str(d['ano']), slug(d['orgao']), item)))
    existentes = {p.stem for p in arquivos(raiz)}
    return base if base not in existentes else f'{base}-{h[:4]}'


def nova(dados: dict, raiz=None, gravar=True) -> tuple[str, Questao | None, list[str]]:
    """Cria uma questão a partir de um dicionário. Devolve (status, questão, mensagens).

    status: 'criada', 'duplicada' (mensagem traz o id existente) ou 'invalida'.
    Chaves: os campos do frontmatter (exceto id, tipo e hash) + `enunciado`, opcionais
    `texto_base`, `alternativas` (dict letra→texto ou lista) e `analise`.
    """
    d = dict(dados)
    if not str(d.get('enunciado', '')).strip():
        return 'invalida', None, ['enunciado ausente']
    d.setdefault('usado_em', [])
    d.setdefault('consulta', _dt.date.today().isoformat())
    for chave in ('gabarito_url', 'url', 'cargo', 'caderno'):
        d.setdefault(chave, NL)
    corpo = _corpo_novo(d) if all(k in d for k in ('banca', 'ano', 'orgao', 'item', 'gabarito', 'gabarito_status')) else ''
    if not corpo:
        return 'invalida', None, ['faltam banca, ano, orgao, item, gabarito ou gabarito_status']
    s = secoes(corpo)
    h = calcular_hash(s.get('enunciado', ''), s.get('alternativas', ''))
    for q in carregar(raiz)[0]:
        if q.meta.get('hash') == h:
            return 'duplicada', q, [f'já existe como {q.id}']
    meta = {c: d[c] for c in CAMPOS if c in d}
    meta.update(tipo='questao', hash=h, item=str(d['item']))
    meta['id'] = novo_id(d, h, raiz)
    pasta = raiz_banco(raiz) / 'questoes' / str(d.get('disciplina', '')) / str(d.get('assunto', ''))
    q = Questao(meta, corpo, pasta / f'{meta["id"]}.md')
    erros, avisos = validar_questao(q, raiz)
    if erros:
        return 'invalida', None, erros
    if gravar:
        q.salvar()
    return 'criada', q, avisos


# ------------------------------------------------------------------ CLI
def _linha_busca(r: dict) -> str:
    gab = {'certo_errado': 'CE', 'multipla_escolha': 'ME'}.get(r['formato'], r['formato'])
    return (f'{r["id"]} | {r["banca"]} {r["ano"]} {gab}={r["gabarito"]} | {r["disciplina"]}/{r["assunto"]} | '
            f'{",".join(r["subassuntos"])} | usos={r["usos"]}')


def _imprimir_questao(q: Questao, analise=False, meta=False):
    m = q.meta
    print(f'### {q.id} — {m["banca"]} {m["ano"]}, {m["orgao"]}, {m["cargo"]}, item {m["item"]} '
          f'({m["formato"]}, gabarito {m["gabarito"]}, {m["gabarito_status"]})')
    if meta:
        print(escrever_documento(m, '').strip())
    s = secoes(q.corpo)
    for nome, titulo in (('enunciado', 'Enunciado'), ('alternativas', 'Alternativas'), ('gabarito', 'Gabarito'),
                         ('analise', 'Análise')):
        if s.get(nome) and (nome != 'analise' or analise):
            print(f'**{titulo}:**\n{s[nome]}')
    print()


def main(argv=None) -> int:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--raiz', help='pasta do banco (padrão: referencias/ na raiz do repositório)')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('assuntos', help='mostra a árvore disciplina > assunto (curta)')
    b = sub.add_parser('buscar', help='filtra questões pelo índice')
    b.add_argument('-d', '--disciplina')
    b.add_argument('-a', '--assunto', help='prefixo do assunto em snake_case')
    b.add_argument('-t', '--termo', action='append', default=[], help='repita para exigir vários termos')
    b.add_argument('-b', '--banca')
    b.add_argument('-f', '--formato', choices=sorted(FORMATOS))
    b.add_argument('--ano-min', type=int)
    b.add_argument('--alvo', help='concurso-alvo, ex.: PRF')
    b.add_argument('--nao-usadas', action='store_true')
    b.add_argument('--corpo', action='store_true', help='procura os termos também no texto das questões')
    b.add_argument('--ids', action='store_true', help='imprime só os IDs')
    b.add_argument('-n', '--limite', type=int, default=20)
    mo = sub.add_parser('mostrar', help='imprime o texto das questões')
    mo.add_argument('ids', nargs='+')
    mo.add_argument('--analise', action='store_true')
    mo.add_argument('--meta', action='store_true')
    nv = sub.add_parser('nova', help='cria questões a partir de JSON (objeto ou lista)')
    nv.add_argument('json', help='arquivo .json ou "-" para a entrada padrão')
    nv.add_argument('--simular', action='store_true', help='valida sem gravar')
    us = sub.add_parser('usar', help='registra o uso das questões em um lote')
    us.add_argument('ids', nargs='+')
    us.add_argument('--lote', required=True, help='ex.: PRF/Missao_09_Navegadores')
    us.add_argument('--cartoes', required=True, help='IDs dos cartões, separados por vírgula')
    ca = sub.add_parser('calibracao', help='JSON das referências para calibracao_cebraspe.json')
    ca.add_argument('ids', nargs='+')
    sub.add_parser('validar', help='confere todas as questões')
    ix = sub.add_parser('indexar', help='valida e regera indice.tsv e assuntos.md')
    ix.add_argument('--atualizar-hash', action='store_true')
    a = ap.parse_args(argv)
    raiz = a.raiz

    try:
        if a.cmd == 'assuntos':
            ler_indice(raiz)
            caminho = raiz_banco(raiz) / 'assuntos.md'
            print(caminho.read_text(encoding='utf-8') if caminho.exists() else 'Banco vazio.')
        elif a.cmd == 'buscar':
            res = buscar(raiz, a.disciplina, a.assunto, a.termo, a.banca, a.formato, a.ano_min, a.alvo,
                         a.nao_usadas, a.corpo)
            for r in res[:a.limite]:
                print(r['id'] if a.ids else _linha_busca(r))
            if not a.ids:
                print(f'-- {len(res)} questão(ões){f"; mostrando {a.limite}" if len(res) > a.limite else ""}')
        elif a.cmd == 'mostrar':
            for q in localizar(a.ids, raiz):
                _imprimir_questao(q, a.analise, a.meta)
        elif a.cmd == 'nova':
            texto = sys.stdin.read() if a.json == '-' else Path(a.json).read_text(encoding='utf-8-sig')
            dados = json.loads(texto)
            falhas = 0
            for d in dados if isinstance(dados, list) else [dados]:
                status, q, msgs = nova(d, raiz, gravar=not a.simular)
                rotulo = q.id if q else f'item {d.get("item", "?")} ({d.get("banca", "?")} {d.get("ano", "?")})'
                print(f'{status}: {rotulo}' + (f' — {"; ".join(msgs)}' if msgs else ''))
                falhas += status == 'invalida'
            if not a.simular:
                indexar(raiz)
            return 1 if falhas else 0
        elif a.cmd == 'usar':
            cartoes = [c.strip() for c in a.cartoes.split(',') if c.strip()]
            for i in a.ids:
                print(f'{i}: {"registrado" if registrar_uso(i, a.lote, cartoes, raiz) else "já registrado"}')
            indexar(raiz)
        elif a.cmd == 'calibracao':
            print(json.dumps(calibracao(*a.ids, raiz=raiz), ensure_ascii=False, indent=1))
        elif a.cmd in ('validar', 'indexar'):
            if a.cmd == 'indexar':
                n, erros, avisos = indexar(raiz, a.atualizar_hash)
            else:
                validas, erros, avisos = validar(raiz)
                n = len(validas)
            for msg in avisos:
                print(f'aviso: {msg}')
            for msg in erros:
                print(f'ERRO: {msg}')
            print(f'{n} questão(ões) válida(s); {len(erros)} erro(s); {len(avisos)} aviso(s)')
            return 1 if erros else 0
    except ErroBanco as exc:
        print(f'ERRO: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
