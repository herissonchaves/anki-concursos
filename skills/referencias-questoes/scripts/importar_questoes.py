#!/usr/bin/env python3
"""Extrai as questões de concursos de um PDF (ou do texto dele) para um RASCUNHO JSON do banco.

O rascunho sai no formato de entrada de `referencias.py nova`, com o marcador `REVISAR`
nos campos que exigem julgamento (assunto, subassuntos, palavras-chave, operação
observada). O banco recusa qualquer questão que ainda contenha esse marcador, então
o agente só confere o texto, completa esses campos e salva com `nova`.

Funciona com o padrão comum de apostilas e cadernos:

  01. CEBRASPE – POLÍCIA RODOVIÁRIA FEDERAL – 2015:      (cabeçalho: número, banca, órgão, ano)
  Enunciado ...  (A) ... (B) ...                          (alternativas opcionais)
  01. Errado.  02. C  13-D                                 (tabela de gabarito)
  Gabarito: CERTO / Gabarito: Letra B                      (questões comentadas)

Quando a mesma questão aparece duas vezes (lista sem comentários + comentadas), fica a
primeira ocorrência; o gabarito vem da tabela ou do bloco comentado. Entrada: .pdf
(PyMuPDF ou pypdf), .json de `automacao-anki-python/scripts/extrair_pdf.py` ou .txt.
Remove marcas-d'água comuns (hashes hexadecimais, linhas com CPF ou e-mail, "Página | N").
"""
from __future__ import annotations

import datetime as _dt
import json
import re
from pathlib import Path

RASCUNHO = 'REVISAR'
HEX = re.compile(r'[0-9A-F]{32}')  # hash de marca-d'água, mesmo grudado em palavras
PESSOAL = re.compile(r'CPF|\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|[\w.+-]+@[\w-]+\.[\w.]+|licenciad[oa] para', re.I)
PAGINA = re.compile(r'P[áa]gina\s*\|\s*\d+', re.I)
CABECALHO = re.compile(
    r'^\s*(?P<num>\d{1,3})\s*[.)]\s*(?P<cab>[A-ZÀ-Ú][^\n]{2,160}?\b(?P<ano>(?:19|20)\d{2})\b)\s*[:.]?\s*',
    re.M)
ALTERNATIVA = re.compile(r'(?:^|\s)\(([A-E])\)\s*')
TABELA = re.compile(r'(?<!\d)(\d{1,3})\s*[.\-–)]\s*(Certo|Errado|[A-E])\b(?![a-zà-ú])')
LINHA_TABELA = re.compile(r'^\s*\d{1,3}\s*[.\-–)]\s*(?:Certo|Errado|[A-E])\b(?![a-zà-ú])', re.M)
COMENTADO = re.compile(r'Gabarito\s*:\s*(CERTO|ERRADO|Letra\s+[A-E]|[A-E])\b', re.I)
TRACO = re.compile(r'\s*[–—-]+\s*')


# ------------------------------------------------------------------ leitura
def paginas_de(caminho: Path) -> list[tuple[int, str]]:
    """Lista (página, texto) a partir de .pdf, .json (extrair_pdf) ou .txt."""
    sufixo = caminho.suffix.lower()
    if sufixo == '.json':
        dados = json.loads(caminho.read_text(encoding='utf-8-sig'))
        return [(int(p['pagina']), p.get('texto', '')) for p in dados['paginas']]
    if sufixo == '.txt':
        return [(1, caminho.read_text(encoding='utf-8-sig'))]
    if sufixo != '.pdf':
        raise ValueError('use .pdf, .json (extrair_pdf) ou .txt')
    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz
        except ImportError:
            fitz = None
    if fitz is not None:
        with fitz.open(caminho) as doc:
            return [(i + 1, p.get_text("text")) for i, p in enumerate(doc)]
    from pypdf import PdfReader
    return [(i + 1, p.extract_text() or '') for i, p in enumerate(PdfReader(str(caminho)).pages)]


def limpar(texto: str, ruido=()) -> str:
    """Tira marcas-d'água, rodapés e palavras de faixa lateral (ruido) do texto de uma página."""
    linhas = []
    for linha in texto.splitlines():
        if PESSOAL.search(linha):
            continue
        linha = PAGINA.sub(' ', HEX.sub(' ', linha))
        if ruido and all(tok in ruido for tok in linha.split()):
            continue  # linha só com palavras da faixa lateral
        for palavra in ruido:
            # Faixa lateral grudada no fim de outra palavra ("2023:TRÂNSITO") ou abrindo a linha
            # (só palavras longas). Não remove a palavra solta no meio do texto ("Prefeitura DE", "anexo I").
            p = re.escape(palavra)
            linha = re.sub(rf'(?<=[^\s{re.escape(palavra[0])}]){p}(?=\s|$)', ' ', linha)
            if len(palavra) >= 4:
                linha = re.sub(rf'^\s*{p}\s+', '', linha)
        linha = re.sub(r'[ \t]{2,}', ' ', linha).strip()
        if linha:
            linhas.append(linha)
    return '\n'.join(linhas)


def _intervalo(paginas: str | None):
    if not paginas:
        return None
    escolhidas = set()
    for parte in paginas.split(','):
        ini, _, fim = parte.partition('-')
        escolhidas.update(range(int(ini), int(fim or ini) + 1))
    return escolhidas


# ------------------------------------------------------------------ análise
def _gabarito_normalizado(bruto: str) -> str:
    b = bruto.strip().upper()
    if b.startswith('CERT'):
        return 'C'
    if b.startswith('ERRAD'):
        return 'E'
    return b.replace('LETRA', '').strip()


def _banca_orgao(cabecalho: str, ano: str) -> tuple[str, str, str]:
    """('CEBRASPE', 'POLÍCIA RODOVIÁRIA FEDERAL – CURSO DE FORMAÇÃO', concurso original)."""
    sem_ano = re.sub(rf'\s*[–—-]*\s*{ano}\s*$', '', cabecalho.strip())
    partes = [p for p in TRACO.split(sem_ano) if p.strip()]
    banca = partes[0].strip() if partes else RASCUNHO
    orgao = ' – '.join(p.strip() for p in partes[1:]) or 'nao_localizado'
    return banca, orgao, f'{" – ".join(p.strip() for p in partes)} — {ano}'


def _titulo(texto: str) -> str:
    """Título em caixa mista, preservando siglas curtas sem acento (PRF, MPU, GO, MA)."""
    pequenas = {'de', 'da', 'do', 'das', 'dos', 'e'}
    saida = []
    for i, original in enumerate(texto.split()):
        p = original.lower()
        if i and p in pequenas:
            saida.append(p)
        elif len(p) <= 3 and p.isascii() and p.isalpha():
            saida.append(p.upper())
        else:
            saida.append(p[:1].upper() + p[1:])
    return ' '.join(saida)


def extrair(caminho, paginas=None, ruido=(), disciplina=RASCUNHO, assunto=RASCUNHO, alvo='PRF') -> list[dict]:
    caminho = Path(caminho)
    escolhidas = _intervalo(paginas)
    blocos = [(n, limpar(t, ruido)) for n, t in paginas_de(caminho) if not escolhidas or n in escolhidas]
    texto, marcas = '', []  # marcas: (posição inicial, página)
    for n, t in blocos:
        marcas.append((len(texto), n))
        texto += t + '\n'

    def pagina_de(pos):
        return max((p for ini, p in marcas if ini <= pos), default=marcas[0][1] if marcas else 1)

    cabecalhos = list(CABECALHO.finditer(texto))
    questoes, comentados = {}, {}
    for i, m in enumerate(cabecalhos):
        fim = cabecalhos[i + 1].start() if i + 1 < len(cabecalhos) else len(texto)
        corpo = texto[m.end():fim]
        num = int(m['num'])
        gab = COMENTADO.search(corpo)
        if gab:
            comentados.setdefault(num, _gabarito_normalizado(gab[1]))
            corpo = corpo[:gab.start()]
        if num in questoes:
            continue
        inicio_tabela = LINHA_TABELA.search(corpo)
        corpo = corpo[:inicio_tabela.start()] if inicio_tabela else corpo
        questoes[num] = (m, corpo, pagina_de(m.start()))
    tabela = {}
    for linha in LINHA_TABELA.finditer(texto):  # só linhas que começam como tabela de gabarito
        fim_linha = texto.find('\n', linha.start())
        for num, gab in TABELA.findall(texto[linha.start():fim_linha if fim_linha >= 0 else None]):
            tabela.setdefault(int(num), _gabarito_normalizado(gab))

    rascunho = []
    hoje = _dt.date.today().isoformat()
    for num, (m, corpo, pagina) in sorted(questoes.items()):
        partes = ALTERNATIVA.split(' '.join(corpo.split()))
        enunciado = partes[0].strip()
        alternativas = {partes[j]: partes[j + 1].strip() for j in range(1, len(partes) - 1, 2)}
        formato = 'multipla_escolha' if len(alternativas) >= 2 else 'certo_errado'
        gabarito = comentados.get(num) or tabela.get(num) or RASCUNHO
        if formato == 'certo_errado' and gabarito not in ('C', 'E'):
            gabarito = RASCUNHO
        banca, orgao, concurso = _banca_orgao(m['cab'], m['ano'])
        item = {
            'banca': _titulo(banca) if banca.isupper() and len(banca) > 6 else banca,
            'formato': formato, 'ano': int(m['ano']),
            'orgao': _titulo(orgao) if orgao != 'nao_localizado' else orgao,
            'concurso': concurso, 'cargo': 'nao_localizado', 'caderno': 'nao_localizado', 'item': 'nao_localizado',
            'disciplina': disciplina, 'assunto': assunto, 'subassuntos': [RASCUNHO], 'palavras_chave': [RASCUNHO],
            'gabarito': gabarito, 'gabarito_status': 'nao_verificado', 'url': 'nao_localizado',
            'origem': 'anexo_usuario', 'fonte_descoberta': f'{caminho.name}, p. {pagina}, questão {num:02d}; gabarito do material',
            'consulta': hoje, 'concursos_alvo': [alvo], 'operacao_observada': RASCUNHO,
            'enunciado': enunciado or RASCUNHO,
        }
        if alternativas:
            item['alternativas'] = alternativas
        rascunho.append(item)
    return rascunho
