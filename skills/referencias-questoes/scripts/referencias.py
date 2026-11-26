#!/usr/bin/env python3
"""Banco de referências (`referencias/` na raiz do repositório): questões, editais,
conteúdos verificados, notícias e prioridades por concurso.

Cada item é um Markdown com frontmatter padronizado (campo `tipo`), na pasta do tipo:
`questoes/<disciplina>/<assunto>/`, `editais/<assunto>/`, `conteudos/<disciplina>/<assunto>/`,
`noticias/<disciplina>/<assunto>/` e `prioridades/<concurso>/<disciplina>/`. O índice único
`indice.tsv` e a árvore `assuntos.md` são gerados por este script e permitem localizar
qualquer item sem abrir os arquivos. Só a biblioteca padrão é usada.

Comandos (rode na raiz do repositório):

  python -X utf8 skills/referencias-questoes/scripts/referencias.py assuntos
  ... buscar [--tipo conteudo] -d informatica -a correio_eletronico -t smtp [--recentes 90] [-n 20]
  ... mostrar ID [ID ...] [--analise] [--meta] [--secao "Legislação de Trânsito"]
  ... fonte ID                      ((url, trecho) de um conteúdo para o F do gerar_lote.py)
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
          'operacao_observada', 'vigencia', 'vigencia_nota', 'usado_em', 'hash')
LISTAS = {'subassuntos', 'palavras_chave', 'concursos_alvo', 'usado_em'}
OPCIONAIS = {'vigencia', 'vigencia_nota'}  # ausente = vigencia atual
VIGENCIAS = {'atual', 'desatualizada'}
RASCUNHO = 'REVISAR'  # marcador deixado por `importar`; o banco recusa questão que ainda o contenha
FORMATOS = {'certo_errado', 'multipla_escolha'}
STATUS = {'definitivo', 'justificativa_oficial', 'nao_verificado', 'anulado'}
ORIGENS = {'anexo_usuario', 'pesquisa_internet', 'caderno_erros'}
GABARITOS = {'certo_errado': {'C', 'E', 'anulada'}, 'multipla_escolha': {'A', 'B', 'C', 'D', 'E', 'anulada'}}
COLUNAS = ('id', 'tipo', 'titulo', 'disciplina', 'assunto', 'subassuntos', 'banca', 'formato', 'ano', 'gabarito',
           'status', 'orgao', 'cargo', 'alvos', 'usos', 'palavras', 'arquivo', 'vigencia', 'tem_url', 'data')

# ------------------------------------------------------------------ tipos além de questão
PASTAS = {'questao': 'questoes', 'edital': 'editais', 'conteudo': 'conteudos', 'noticia': 'noticias',
          'prioridade': 'prioridades'}
EXTRAS = {
    'edital': ('orgao', 'banca', 'cargo', 'ano', 'edicao', 'status', 'retificacoes'),
    'conteudo': ('norma', 'dispositivos', 'situacao', 'verificado_em'),
    'noticia': ('data_evento', 'status', 'efeito', 'normas_afetadas'),
    'prioridade': ('concurso', 'prioridade', 'incidencia', 'evidencias'),
}
LISTAS_DOC = {'subassuntos', 'palavras_chave', 'concursos_alvo', 'usado_em', 'retificacoes', 'dispositivos',
              'normas_afetadas', 'evidencias'}
LISTAS_VAZIAS = {'usado_em', 'retificacoes', 'evidencias'}
ENUMS = {('edital', 'status'): {'vigente', 'historico', 'previsto'},
         ('conteudo', 'situacao'): {'vigente', 'alterado', 'revogado'},
         ('noticia', 'status'): {'confirmada', 'pendente'},
         ('prioridade', 'prioridade'): {'alta', 'media', 'baixa'}}
DATAS_DOC = ('consulta', 'verificado_em', 'data_evento')


def campos_doc(tipo: str) -> tuple:
    return (('id', 'tipo', 'titulo', 'disciplina', 'assunto', 'subassuntos', 'palavras_chave', 'concursos_alvo')
            + EXTRAS[tipo] + ('url', 'fonte_descoberta', 'consulta', 'vigencia', 'vigencia_nota', 'usado_em', 'hash'))


def campos_de(meta: dict) -> tuple:
    tipo = meta.get('tipo', 'questao')
    return CAMPOS if tipo == 'questao' else campos_doc(tipo)
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
    linhas = [f'{c}: {_escrever_valor(meta[c])}' for c in campos_de(meta) if c in meta]
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

    @property
    def tipo(self):
        return self.meta.get('tipo', 'questao')

    def hash_corpo(self):
        if self.tipo != 'questao':
            return calcular_hash(self.meta.get('titulo', ''), self.meta.get('url', ''))
        s = secoes(self.corpo)
        return calcular_hash(s.get('enunciado', ''), s.get('alternativas', ''))

    def salvar(self):
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(self.caminho, 'w', encoding='utf-8', newline='\n') as f:
            f.write(escrever_documento(self.meta, self.corpo))


def arquivos(raiz=None):
    base = raiz_banco(raiz)
    return sorted(p for pasta in PASTAS.values() for p in (base / pasta).rglob('*.md'))


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
    if q.tipo != 'questao':
        return validar_documento(q, raiz)
    m, erros, avisos = q.meta, [], []
    p = f'{q.caminho.name}'
    for campo in CAMPOS:
        valor = m.get(campo)
        if campo in OPCIONAIS and campo not in m:
            continue
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
    if m.get('vigencia', 'atual') not in VIGENCIAS:
        erros.append(f'{p}: vigencia deve ser atual ou desatualizada')
    elif m.get('vigencia') == 'desatualizada' and not str(m.get('vigencia_nota', '')).strip():
        erros.append(f'{p}: vigencia desatualizada exige vigencia_nota com o motivo (lei, decisão, data)')
    restos = [c for c in CAMPOS if RASCUNHO in (m.get(c) if isinstance(m.get(c), list) else [str(m.get(c, ''))])]
    if restos or RASCUNHO in q.corpo:
        erros.append(f'{p}: rascunho não revisado (marcador {RASCUNHO} em {restos or ["corpo"]})')
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


IMAGENS = 'imagens'  # referencias/imagens/: figuras recortadas dos cadernos, citadas como ![[arquivo.png]]
EMBUTIDA = re.compile(r'!\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]')


def imagens_citadas(corpo: str) -> list[str]:
    """Nomes das imagens embutidas no estilo Obsidian (![[arquivo.png]] ou ![[arquivo.png|legenda]])."""
    return [m.strip() for m in EMBUTIDA.findall(corpo)]


def validar_imagens(q: Questao, raiz=None) -> list[str]:
    pasta = raiz_banco(raiz) / IMAGENS
    return [f'{q.caminho.name}: imagem {nome!r} não encontrada em {IMAGENS}/'
            for nome in imagens_citadas(q.corpo) if '/' in nome or not (pasta / nome).is_file()]


def validar(raiz=None) -> tuple[list[Questao], list[str], list[str]]:
    questoes, erros = carregar(raiz)
    avisos, validas, por_hash, por_id = [], [], {}, {}
    for q in questoes:
        e, a = validar_questao(q, raiz)
        e += validar_imagens(q, raiz)
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
    comum = {'id': q.id, 'tipo': q.tipo, 'disciplina': m['disciplina'], 'assunto': m['assunto'],
             'subassuntos': m['subassuntos'], 'alvos': m['concursos_alvo'], 'usos': len(m['usado_em']),
             'palavras': m['palavras_chave'], 'arquivo': q.caminho.relative_to(raiz_banco(raiz)).as_posix(),
             'vigencia': m.get('vigencia', 'atual'), 'tem_url': 'sim' if _url_ok(m.get('url')) else 'nao'}
    if q.tipo == 'questao':
        return {**comum, 'titulo': f'{m["banca"]} {m["ano"]} — {m["orgao"]} — item {m["item"]}',
                'banca': m['banca'], 'formato': m['formato'], 'ano': m['ano'], 'gabarito': m['gabarito'],
                'status': m['gabarito_status'], 'orgao': m['orgao'], 'cargo': m['cargo'], 'data': m['consulta']}
    status = {'edital': 'status', 'conteudo': 'situacao', 'noticia': 'status', 'prioridade': 'prioridade'}[q.tipo]
    data = {'conteudo': 'verificado_em', 'noticia': 'data_evento'}.get(q.tipo, 'consulta')
    return {**comum, 'titulo': m['titulo'], 'banca': m.get('banca', ''), 'formato': '', 'ano': m.get('ano', 0),
            'gabarito': '', 'status': m[status], 'orgao': m.get('orgao', m.get('concurso', '')),
            'cargo': m.get('cargo', m.get('norma', '')), 'data': m[data]}


def _ordem(linha):
    return (linha['disciplina'], linha['assunto'], linha['tipo'], -int(linha['ano'] or 0), linha['id'])


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
             f'Total: {len(linhas)} itens. Formato: assunto (n): subassuntos · bancas das questões · tipos '
             '(questao, edital, conteudo, noticia, prioridade).', '']
    discs = {}
    for l in linhas:
        discs.setdefault(l['disciplina'], {}).setdefault(l['assunto'], []).append(l)
    for disc, assuntos in sorted(discs.items()):
        saida.append(f'- **{disc}** ({sum(len(v) for v in assuntos.values())})')
        for assunto, itens in sorted(assuntos.items()):
            subs, bancas, tipos = {}, {}, {}
            for l in itens:
                for s in l['subassuntos']:
                    subs[s] = subs.get(s, 0) + 1
                if l['tipo'] == 'questao':
                    bancas[l['banca']] = bancas.get(l['banca'], 0) + 1
                tipos[l['tipo']] = tipos.get(l['tipo'], 0) + 1
            fmt = lambda d: ', '.join(f'{k} {v}' for k, v in sorted(d.items(), key=lambda kv: (-kv[1], kv[0])))
            extra = f' · {fmt(bancas)}' if bancas else ''
            saida.append(f'  - {assunto} ({len(itens)}): {fmt(subs)}{extra} · tipos: {fmt(tipos)}')
    return '\n'.join(saida) + '\n'


def recortar_assuntos(texto: str, disciplinas=(), completo=False) -> str:
    """Recorte barato da árvore: sem filtro, só as disciplinas; com `disciplinas`, só os blocos delas."""
    if completo:
        return texto
    linhas = texto.splitlines()
    cabecalho = [l for l in linhas[:4] if not l.startswith('- ')]
    if not disciplinas:
        corpo = [l for l in linhas if l.startswith('- **')]
        dica = 'Use `assuntos -d DISC` para ver os assuntos de uma disciplina.'
        return '\n'.join(cabecalho + corpo + ['', dica]) + '\n'
    alvo = {d.lower() for d in disciplinas}
    saida, dentro = list(cabecalho), False
    for l in linhas:
        if l.startswith('- **'):
            dentro = l[4:].split('**')[0].lower() in alvo
        if dentro and l.startswith(('- **', '  - ')):
            saida.append(l)
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
    if reindexar and tuple(cab) != COLUNAS:  # índice de versão anterior do script
        indexar(raiz)
        return ler_indice(raiz, reindexar=False)
    saida = []
    for linha in linhas[1:]:
        reg = dict(zip(cab, linha.split('\t')))
        for c in ('subassuntos', 'alvos', 'palavras'):
            reg[c] = [v for v in reg.get(c, '').split(';') if v]
        reg['ano'], reg['usos'] = int(reg['ano'] or 0), int(reg['usos'])
        reg.setdefault('vigencia', 'atual')
        reg.setdefault('tem_url', 'sim')
        saida.append(reg)
    return saida


# ------------------------------------------------------------------ consultas
def buscar(raiz=None, disciplina=None, assunto=None, termos=(), banca=None, formato=None, ano_min=None,
           alvo=None, nao_usadas=False, corpo=False, vigentes=False, com_url=False, tipo=None,
           recentes=None) -> list[dict]:
    base = raiz_banco(raiz)
    termos = [normalizar(t) for t in termos if normalizar(t)]
    hoje = _dt.date.today()
    saida = []
    for reg in ler_indice(raiz):
        if tipo and reg['tipo'] != tipo:
            continue
        if recentes is not None:
            try:
                if (hoje - _dt.date.fromisoformat(reg['data'])).days > recentes:
                    continue
            except ValueError:
                continue
        if vigentes and reg['vigencia'] != 'atual':
            continue
        if com_url and reg['tem_url'] != 'sim':
            continue
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
            alvo_txt = normalizar(' '.join([reg['id'], reg['titulo'], reg['assunto'], *reg['subassuntos'],
                                            *reg['palavras'], reg['orgao'], reg['cargo'], reg['banca']]).replace('_', ' '))
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
            raise ErroBanco(f'item {i!r} não encontrado no banco ({base})')
        saida.append(ler_questao(achados[0]))
    return saida


def alternativas(ident, raiz=None) -> list[str]:
    """Letras da seção `## Alternativas` (`- A) …`) de uma questão; [] em Certo/Errado (2.38)."""
    q = localizar([ident], raiz)[0]
    if q.tipo != 'questao':
        raise ErroBanco(f'{ident}: é {q.tipo}, não questão')
    texto = secoes(q.corpo).get('alternativas', '')
    return list(dict.fromkeys(re.findall(r'^- ([A-Z])\)', texto, flags=re.M)))


def tem_prova(ident, raiz=None) -> bool:
    """True se a questão tem url da prova (pode entrar na calibração)."""
    q = localizar([ident], raiz)[0]
    if q.tipo != 'questao':
        raise ErroBanco(f'{ident}: é {q.tipo}, não questão; use-o em fontes, não em refs de calibração')
    return _url_ok(q.meta.get('url'))


def sem_prova(*ids, raiz=None) -> list[dict]:
    """Resumo das questões sem prova oficial localizada, para `referencias_sem_prova` da calibração.

    Servem de inspiração (inclusive de outra banca), mas não sustentam fidelidade comparada.
    """
    saida = []
    for q in localizar(ids, raiz):
        m = q.meta
        saida.append({'id': q.id, 'banca': m['banca'], 'formato': m['formato'], 'ano': m['ano'],
                      'concurso': m['concurso'], 'item': str(m['item']), 'origem': m['origem'],
                      'fonte_descoberta': m['fonte_descoberta'], 'gabarito_status': m['gabarito_status'],
                      'operacao_observada': m['operacao_observada'], 'vigencia': m.get('vigencia', 'atual')})
    return saida


def calibracao(*ids, raiz=None) -> list[dict]:
    """Referências no formato de `calibracao_cebraspe.json` (schema 2) para os IDs dados."""
    refs = []
    for q in localizar(ids, raiz):
        m = q.meta
        if q.tipo != 'questao':
            raise ErroBanco(f'{q.id}: é {q.tipo}; só questões entram na calibração')
        if m.get('vigencia') == 'desatualizada':
            print(f'aviso: {q.id} está desatualizada ({m.get("vigencia_nota")}); use só como modelo de forma',
                  file=sys.stderr)
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
    orgao = slug(d['orgao']) if str(d.get('orgao', NL)) != NL else ''
    if not orgao:  # sem órgão: usa as palavras do concurso que não repetem banca nem ano
        repetidas = set(slug(d['banca']).split('-')) | {str(d['ano'])}
        orgao = '-'.join([w for w in slug(d.get('concurso', '')).split('-') if w and w not in repetidas][:4])
    base = '-'.join(filter(None, (slug(d['banca']), str(d['ano']), orgao, item)))
    existentes = {p.stem for p in arquivos(raiz)}
    return base if base not in existentes else f'{base}-{h[:4]}'


def _texto_comparavel(texto: str) -> str:
    return re.sub(r'[^0-9a-zà-ú]+', '', str(texto).lower())


def possiveis_duplicatas(itens: list[dict], raiz=None, trecho=120) -> list[tuple[str, str]]:
    """Questões do rascunho cujo final do enunciado já aparece em alguma questão do banco.

    O hash de `nova` só pega cópias exatas; aqui o comando de julgamento ("julgue o item…") e o
    texto-base podem estar separados de outro jeito. Devolve [(rótulo do rascunho, id existente)].
    """
    banco = [(q.id, _texto_comparavel(q.corpo)) for q in carregar(raiz)[0] if q.tipo == 'questao']
    saida = []
    for i in itens:
        alvo = _texto_comparavel(i.get('enunciado', ''))[-trecho:]
        if len(alvo) < 40:
            continue
        rotulo = str(i.get('fonte_descoberta', '')).split(', ')[-1].split(';')[0] or str(i.get('enunciado', ''))[:30]
        for ident, texto in banco:
            if alvo in texto:
                saida.append((rotulo, ident))
                break
    return saida


def nova(dados: dict, raiz=None, gravar=True) -> tuple[str, Questao | None, list[str]]:
    """Cria uma questão a partir de um dicionário. Devolve (status, questão, mensagens).

    status: 'criada', 'duplicada' (mensagem traz o id existente) ou 'invalida'.
    Chaves: os campos do frontmatter (exceto id, tipo e hash) + `enunciado`, opcionais
    `texto_base`, `alternativas` (dict letra→texto ou lista) e `analise`.
    """
    d = dict(dados)
    if d.get('tipo', 'questao') != 'questao':
        return nova_documento(d, raiz, gravar)
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


CAMPOS_META = ('assunto', 'subassuntos', 'palavras_chave', 'operacao_observada', 'gabarito', 'disciplina')


def completar(rascunho: list[dict], meta: dict, raiz=None, gravar=True) -> tuple[dict, list[str]]:
    """Completa os campos REVISAR do rascunho de `importar` e salva cada questão com `nova` (2.36).

    `meta`: {"assunto": padrão, "disciplina": opcional, "itens": {chave: valor}}, com a chave do rascunho
    (T01, Q05…) e valor `"skip"` (repetida, já no banco ou fora do tema), uma lista
    [subassunto ou lista, palavras_chave, operacao_observada] ou um dict com os campos de CAMPOS_META.
    Devolve ({chave: id criado ou existente}, mensagens). Toda chave do rascunho precisa estar em `itens`.
    """
    itens = meta.get('itens', {})
    faltam = [i.get('chave', '?') for i in rascunho if i.get('chave') not in itens]
    sobram = sorted(set(itens) - {i.get('chave') for i in rascunho})
    if faltam or sobram:
        raise ErroBanco(f'meta não corresponde ao rascunho: faltam {faltam or "nenhuma"}; sem questão: {sobram or "nenhuma"}')
    mapa, msgs = {}, []
    for item in rascunho:
        chave, valor = item['chave'], itens[item['chave']]
        if valor == 'skip':
            msgs.append(f'{chave}: pulada')
            continue
        if isinstance(valor, list):
            sub, pal, op = valor
            valor = {'subassuntos': [sub] if isinstance(sub, str) else sub, 'palavras_chave': pal, 'operacao_observada': op}
        d = dict(item)
        d.update({k: meta[k] for k in ('assunto', 'disciplina') if k in meta})
        d.update({k: v for k, v in valor.items() if k in CAMPOS_META})
        restos = [k for k, v in d.items() if v == RASCUNHO or (isinstance(v, list) and RASCUNHO in v)]
        if restos:
            raise ErroBanco(f'{chave}: ainda há {RASCUNHO} em {", ".join(restos)}')
        status, q, m = nova(d, raiz, gravar=gravar)
        if status == 'invalida':
            raise ErroBanco(f'{chave}: inválida — {"; ".join(m)}')
        mapa[chave] = q.id
        msgs.append(f'{chave}: {status} {q.id}' + (f' — {"; ".join(m)}' if m and status != 'duplicada' else ''))
    return mapa, msgs


# ------------------------------------------------------------------ editais, conteúdos, notícias e prioridades
def pasta_documento(meta: dict, raiz=None) -> Path:
    base, tipo = raiz_banco(raiz), meta['tipo']
    if tipo == 'edital':
        return base / 'editais' / str(meta['assunto'])
    if tipo == 'prioridade':
        return base / 'prioridades' / slug(meta['concurso']).replace('-', '_') / str(meta['disciplina'])
    return base / PASTAS[tipo] / str(meta['disciplina']) / str(meta['assunto'])


def validar_documento(q: Questao, raiz=None) -> tuple[list[str], list[str]]:
    m, erros, avisos, p = q.meta, [], [], q.caminho.name
    if m.get('tipo') not in EXTRAS:
        return [f'{p}: tipo deve ser um de {sorted(PASTAS)}'], []
    campos = campos_doc(m['tipo'])
    for campo in campos:
        if campo in OPCIONAIS and campo not in m:
            continue
        valor = m.get(campo)
        if campo in LISTAS_DOC:
            if not isinstance(valor, list):
                erros.append(f'{p}: {campo} deve ser lista [..]')
            elif campo not in LISTAS_VAZIAS and not [v for v in valor if str(v).strip()]:
                erros.append(f'{p}: {campo} vazio')
        elif valor is None or str(valor).strip() == '':
            erros.append(f'{p}: {campo} ausente ou vazio')
    extras = set(m) - set(campos)
    if extras:
        erros.append(f'{p}: campos desconhecidos {sorted(extras)}')
    if erros:
        return erros, avisos
    if m['id'] != q.caminho.stem:
        erros.append(f'{p}: id {m["id"]!r} difere do nome do arquivo')
    for (tipo, campo), valores in ENUMS.items():
        if m['tipo'] == tipo and m[campo] not in valores:
            erros.append(f'{p}: {campo} deve ser um de {sorted(valores)}')
    for campo in DATAS_DOC:
        if campo in m and not DATA.match(str(m[campo])):
            erros.append(f'{p}: {campo} deve ser AAAA-MM-DD')
    if m['tipo'] == 'edital' and (not isinstance(m['ano'], int) or not 1980 <= m['ano'] <= _dt.date.today().year + 2):
        erros.append(f'{p}: ano deve ser inteiro')
    if m.get('vigencia', 'atual') not in VIGENCIAS:
        erros.append(f'{p}: vigencia deve ser atual ou desatualizada')
    elif m.get('vigencia') == 'desatualizada' and not str(m.get('vigencia_nota', '')).strip():
        erros.append(f'{p}: vigencia desatualizada exige vigencia_nota')
    for campo in ('disciplina', 'assunto'):
        if not SNAKE.match(str(m[campo])):
            erros.append(f'{p}: {campo} deve ser snake_case sem acentos')
    if not _url_ok(m['url']):
        erros.append(f'{p}: url da fonte obrigatória (http/https)')
    if q.caminho.resolve() != (pasta_documento(m, raiz) / q.caminho.name).resolve():
        erros.append(f'{p}: deveria estar em {pasta_documento(m, raiz).relative_to(raiz_banco(raiz)).as_posix()}/')
    if not re.search(r'^## ', q.corpo, re.M):
        erros.append(f'{p}: corpo precisa de ao menos uma seção "## ..."')
    if m['hash'] != q.hash_corpo():
        erros.append(f'{p}: hash desatualizado (titulo/url mudaram); rode indexar --atualizar-hash')
    if RASCUNHO in q.corpo:
        erros.append(f'{p}: rascunho não revisado (marcador {RASCUNHO})')
    for padrao, nome in DADOS_PESSOAIS:
        if padrao.search(q.corpo):
            erros.append(f'{p}: possível dado pessoal ({nome}) no texto; remova antes de salvar')
    return erros, avisos


def nova_documento(d: dict, raiz=None, gravar=True) -> tuple[str, Questao | None, list[str]]:
    """Cria edital, conteúdo, notícia ou prioridade. Chaves: os campos do tipo (exceto id e hash) + `corpo`
    (Markdown com seções "## ..."). Duplicata = mesmo título e url."""
    corpo = str(d.pop('corpo', '')).strip()
    if not corpo:
        return 'invalida', None, ['corpo ausente']
    d.setdefault('usado_em', [])
    d.setdefault('consulta', _dt.date.today().isoformat())
    for chave in LISTAS_VAZIAS & set(EXTRAS.get(d['tipo'], ())):
        d.setdefault(chave, [])
    h = calcular_hash(d.get('titulo', ''), d.get('url', ''))
    for q in carregar(raiz)[0]:
        if q.meta.get('hash') == h and q.tipo == d['tipo']:
            return 'duplicada', q, [f'já existe como {q.id}']
    meta = {c: d[c] for c in campos_doc(d['tipo']) if c in d} if d['tipo'] in EXTRAS else dict(d)
    base = '-'.join([d['tipo']] + slug(d.get('titulo', '')).split('-')[:7])  # curto e legível
    existentes = {x.stem for x in arquivos(raiz)}
    meta.update(hash=h, id=base if base not in existentes else f'{base}-{h[:4]}')
    if d['tipo'] not in EXTRAS:
        return 'invalida', None, [f'tipo deve ser um de {sorted(PASTAS)}']
    q = Questao(meta, f'# {meta.get("titulo", "")}\n\n{corpo}\n', pasta_documento(meta, raiz) / f'{meta["id"]}.md')
    erros, avisos = validar_documento(q, raiz)
    if erros:
        return 'invalida', None, erros
    if gravar:
        q.salvar()
    return 'criada', q, avisos


def trecho_secao(corpo: str, nome: str) -> str:
    """Seção "## ..." cujo título começa com `nome` (sem acento/caixa), até a próxima de mesmo nível."""
    alvo, saida, dentro = normalizar(nome), [], False
    for linha in corpo.split('\n'):
        if linha.startswith('## '):
            dentro = normalizar(linha[3:]).startswith(alvo)
        if dentro:
            saida.append(linha)
    return '\n'.join(saida).strip() or f'(seção "{nome}" não encontrada)'


def fonte(ident, raiz=None) -> tuple[str, str]:
    """(url, trecho) de um conteúdo (ou notícia/edital) do banco, para o dicionário F do gerar_lote.py.
    `ID#seção` cita só a seção "## ..." que começa com aquele nome (ex.: "conteudo-ctb-...#Art. 67-C")."""
    ident, _, secao = str(ident).partition('#')
    q = localizar([ident], raiz)[0]
    m = q.meta
    if secao:
        titulo = trecho_secao(q.corpo, secao).split('\n')[0]
        if not titulo.startswith('## '):
            raise ErroBanco(f'{ident}: seção {secao!r} não encontrada')
        base = m.get('norma', m['titulo'])
        data = m.get('verificado_em', m['consulta'])
        return m['url'], f'{base} — {titulo[3:]} — verificado em {data} (banco {q.id})'
    if q.tipo == 'conteudo':
        return m['url'], (f'{m["norma"]}: {", ".join(m["dispositivos"])} — verificado em {m["verificado_em"]} '
                          f'({m["situacao"]}; banco {q.id})')
    if q.tipo == 'questao':
        raise ErroBanco(f'{ident}: questão vai em refs, não em fontes')
    return m['url'], f'{m["titulo"]} (banco {q.id}, consulta {m["consulta"]})'


# ------------------------------------------------------------------ CLI
def _linha_busca(r: dict) -> str:
    if r.get('tipo', 'questao') != 'questao':
        return (f'{r["id"]} | {r["tipo"]} | {r["titulo"][:70]} | {r["disciplina"]}/{r["assunto"]} | '
                f'{r["status"]} | {r["data"]} | usos={r["usos"]}'
                + (' | DESATUALIZADA' if r.get('vigencia', 'atual') != 'atual' else ''))
    gab = {'certo_errado': 'CE', 'multipla_escolha': 'ME'}.get(r['formato'], r['formato'])
    marcas = ('' if r.get('tem_url', 'sim') == 'sim' else ' | sem prova') + \
             (' | DESATUALIZADA' if r.get('vigencia', 'atual') != 'atual' else '')
    return (f'{r["id"]} | {r["banca"]} {r["ano"]} {gab}={r["gabarito"]} | {r["disciplina"]}/{r["assunto"]} | '
            f'{",".join(r["subassuntos"])} | usos={r["usos"]}{marcas}')


def _imprimir_questao(q: Questao, analise=False, meta=False, secao=None):
    m = q.meta
    if q.tipo != 'questao':
        rotulo = {'conteudo': f'verificado em {m.get("verificado_em")}, {m.get("situacao")}',
                  'noticia': f'{m.get("data_evento")}, {m.get("status")}', 'edital': f'{m.get("status")}',
                  'prioridade': f'prioridade {m.get("prioridade")}'}[q.tipo]
        print(f'### {q.id} — {q.tipo}: {m["titulo"]} ({rotulo})')
        if m.get('vigencia') == 'desatualizada':
            print(f'ATENÇÃO — DESATUALIZADA: {m.get("vigencia_nota")}')
        if meta:
            print(escrever_documento(m, '').strip())
        print(trecho_secao(q.corpo, secao) if secao else q.corpo.strip())
        print()
        return
    print(f'### {q.id} — {m["banca"]} {m["ano"]}, {m["orgao"]}, {m["cargo"]}, item {m["item"]} '
          f'({m["formato"]}, gabarito {m["gabarito"]}, {m["gabarito_status"]})')
    if m.get('vigencia') == 'desatualizada':
        print(f'ATENÇÃO — DESATUALIZADA: {m.get("vigencia_nota")}')
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
    s = sub.add_parser('assuntos', help='sem opções: só disciplinas e contagens; -d DISC: assuntos da disciplina')
    s.add_argument('-d', '--disciplina', action='append', default=[], help='repita para várias disciplinas')
    s.add_argument('--completo', action='store_true', help='árvore inteira (cara: use só ao manter o banco)')
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
    b.add_argument('--vigentes', action='store_true', help='omite questões marcadas como desatualizadas')
    b.add_argument('--com-url', action='store_true', help='só questões com prova oficial (servem à calibração)')
    b.add_argument('--tipo', choices=sorted(PASTAS), help='questao, edital, conteudo, noticia ou prioridade')
    b.add_argument('--recentes', type=int, help='só itens com data (verificação, evento ou consulta) de até N dias')
    b.add_argument('--ids', action='store_true', help='imprime só os IDs')
    b.add_argument('-n', '--limite', type=int, default=20)
    mo = sub.add_parser('mostrar', help='imprime o texto das questões')
    mo.add_argument('ids', nargs='+')
    mo.add_argument('--analise', action='store_true')
    mo.add_argument('--meta', action='store_true')
    mo.add_argument('--secao', help='imprime só a seção "## ..." que começa com este texto (editais longos)')
    fo = sub.add_parser('fonte', help='(url, trecho) de um conteúdo verificado, para o F do gerar_lote.py')
    fo.add_argument('id')
    nv = sub.add_parser('nova', help='cria questões a partir de JSON (objeto ou lista)')
    nv.add_argument('json', help='arquivo .json ou "-" para a entrada padrão')
    nv.add_argument('--simular', action='store_true', help='valida sem gravar')
    us = sub.add_parser('usar', help='registra o uso das questões em um lote')
    us.add_argument('ids', nargs='+')
    us.add_argument('--lote', required=True, help='ex.: PRF/Missao_09_Navegadores')
    us.add_argument('--cartoes', required=True, help='IDs dos cartões, separados por vírgula')
    ca = sub.add_parser('calibracao', help='JSON das referências para calibracao_cebraspe.json')
    ca.add_argument('ids', nargs='+')
    im = sub.add_parser('importar', help='rascunho JSON das questões de um PDF/JSON/TXT (revisar e salvar com nova)')
    im.add_argument('arquivo', help='.pdf, .json de extrair_pdf.py ou .txt')
    im.add_argument('-o', '--saida', required=True, help='JSON do rascunho (fora do repositório, ex.: scratchpad)')
    im.add_argument('-p', '--paginas', help='ex.: 17-19 (só a lista de questões, sem a parte comentada)')
    im.add_argument('-d', '--disciplina', default='REVISAR')
    im.add_argument('-a', '--assunto', default='REVISAR')
    im.add_argument('--alvo', default='PRF')
    im.add_argument('--ruido', action='append', default=[], help='palavra de faixa lateral a remover (repita)')
    co = sub.add_parser('completar', help='completa o rascunho de importar com um JSON de metadados e salva (2.36)')
    co.add_argument('rascunho', help='JSON gerado por importar')
    co.add_argument('meta', help='JSON {"assunto": ..., "itens": {"Q01": [sub, [palavras], operação] | "skip"}}')
    co.add_argument('--simular', action='store_true', help='valida sem gravar')
    co.add_argument('--mapa', help='grava o mapa {chave: id} neste JSON (fora do repositório)')
    sub.add_parser('validar', help='confere todas as questões')
    ix = sub.add_parser('indexar', help='valida e regera indice.tsv e assuntos.md')
    ix.add_argument('--atualizar-hash', action='store_true')
    a = ap.parse_args(argv)
    raiz = a.raiz

    try:
        if a.cmd == 'fonte':
            print(json.dumps(fonte(a.id, raiz), ensure_ascii=False))
        elif a.cmd == 'assuntos':
            ler_indice(raiz)
            caminho = raiz_banco(raiz) / 'assuntos.md'
            texto = caminho.read_text(encoding='utf-8') if caminho.exists() else ''
            print(recortar_assuntos(texto, a.disciplina, a.completo) if texto else 'Banco vazio.')
        elif a.cmd == 'buscar':
            res = buscar(raiz, a.disciplina, a.assunto, a.termo, a.banca, a.formato, a.ano_min, a.alvo,
                         a.nao_usadas, a.corpo, a.vigentes, a.com_url, a.tipo, a.recentes)
            for r in res[:a.limite]:
                print(r['id'] if a.ids else _linha_busca(r))
            if not a.ids:
                print(f'-- {len(res)} item(ns){f"; mostrando {a.limite}" if len(res) > a.limite else ""}')
        elif a.cmd == 'mostrar':
            for q in localizar(a.ids, raiz):
                _imprimir_questao(q, a.analise, a.meta, a.secao)
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
        elif a.cmd == 'importar':
            sys.path.insert(0, str(AQUI.parent))
            import importar_questoes
            avisos = []
            itens = importar_questoes.extrair(a.arquivo, a.paginas, a.ruido, a.disciplina, a.assunto, a.alvo, avisos)
            Path(a.saida).write_text(json.dumps(itens, ensure_ascii=False, indent=1), encoding='utf-8')
            pendentes = sum(json.dumps(i, ensure_ascii=False).count(RASCUNHO) for i in itens)
            for i in itens:
                print(f'{i["fonte_descoberta"].split(", ")[-1].split(";")[0]} | {i["banca"]} {i["ano"]} | {i["formato"]} | '
                      f'gab={i["gabarito"]} | {i["enunciado"][:70]}')
            for rotulo, existente in possiveis_duplicatas(itens, raiz):
                avisos.append(f'{rotulo}: parece já estar no banco como {existente} (não salve de novo; cite o ID existente)')
            for msg in avisos:
                print(f'aviso: {msg}')
            print(f'-- {len(itens)} questão(ões) em {a.saida}; {pendentes} campo(s) {RASCUNHO} a completar')
        elif a.cmd == 'completar':
            rascunho = json.loads(Path(a.rascunho).read_text(encoding='utf-8-sig'))
            meta = json.loads(Path(a.meta).read_text(encoding='utf-8-sig'))
            mapa, msgs = completar(rascunho, meta, raiz, gravar=not a.simular)
            for msg in msgs:
                print(msg)
            if not a.simular:
                indexar(raiz)
            if a.mapa:
                Path(a.mapa).write_text(json.dumps(mapa, ensure_ascii=False), encoding='utf-8')
            print(json.dumps(mapa, ensure_ascii=False))
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
            print(f'{n} item(ns) válido(s); {len(erros)} erro(s); {len(avisos)} aviso(s)')
            return 1 if erros else 0
    except ErroBanco as exc:
        print(f'ERRO: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
