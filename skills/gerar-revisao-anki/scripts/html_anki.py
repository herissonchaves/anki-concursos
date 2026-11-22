#!/usr/bin/env python3
"""Componentes HTML compatíveis com o Anki para versos C/E e Extras Cloze.

Estilos inline, fundos translúcidos (legíveis no modo claro e no noturno), sem
CSS externo, scripts ou mídia remota. Ver references/protocolo_visual_html_anki.md.
"""
from __future__ import annotations

import re

# tipo: (título, cor da borda/título, fundo translúcido)
PALETA = {
    'regra': ('📌 Regra', '#1e88e5', 'rgba(30,136,229,0.10)'),
    'caso': ('🔎 No caso', '#8e24aa', 'rgba(142,36,170,0.10)'),
    'erro': ('⚠️ Onde está o erro', '#e53935', 'rgba(229,57,53,0.10)'),
    'certo': ('✔️ Por que está certo', '#43a047', 'rgba(67,160,71,0.10)'),
    'esquema': ('🗺️ Esquema', '#00897b', 'rgba(0,137,123,0.08)'),
    'memorize': ('💡 Memorize', '#ef8f00', 'rgba(249,168,37,0.16)'),
    'origem': ('📚 Origem do mnemônico', '#757575', 'rgba(127,127,127,0.10)'),
}
_ORIGENS = {'encontrado': 'Encontrado em', 'adaptado': 'Adaptado de'}
_BORDA_SUAVE = 'rgba(127,127,127,0.45)'
PREFIXO = {'C': '✅ Certo<br><br>', 'E': '❌ Errado<br><br>'}


def _sem_quebras(texto: str) -> str:
    if '\t' in texto or '\n' in texto or '\r' in texto:
        raise ValueError('Campo Anki não pode conter TAB ou quebra de linha; use <br>')
    return texto


def bloco(tipo: str, corpo: str, titulo: str | None = None) -> str:
    rotulo, cor, fundo = PALETA[tipo]
    rotulo = titulo or rotulo
    return (f'<div style="border-left:4px solid {cor};background:{fundo};border-radius:6px;'
            f'padding:6px 10px;margin:8px 0;">'
            f'<div style="font-weight:bold;color:{cor};margin-bottom:2px;">{rotulo}</div>'
            f'{_sem_quebras(corpo)}</div>')


def regra(corpo: str, titulo: str | None = None) -> str: return bloco('regra', corpo, titulo)
def caso(corpo: str, titulo: str | None = None) -> str: return bloco('caso', corpo, titulo)
def erro(corpo: str, titulo: str | None = None) -> str: return bloco('erro', corpo, titulo)
def certo(corpo: str, titulo: str | None = None) -> str: return bloco('certo', corpo, titulo)
def esquema(corpo: str, titulo: str | None = None) -> str: return bloco('esquema', corpo, titulo)
def memorize(corpo: str) -> str: return bloco('memorize', corpo)


def origem_mnemonico(origem) -> str:
    """Bloco do verso que diz de onde veio o mnemônico (2.33).

    `origem`: 'autoral' ou (modo, url, nome) com modo 'encontrado' ou 'adaptado'; o link vai para a
    fonte (página do professor/curso ou imagem da internet). Na frente nunca vai a origem.
    """
    if origem == 'autoral':
        return bloco('origem', 'Autoral: criado para este card, sem fonte externa.')
    try:
        modo, url, nome = origem
    except (TypeError, ValueError):
        raise ValueError("origem do mnemônico: 'autoral' ou (\"encontrado\"|\"adaptado\", url, nome)") from None
    if modo not in _ORIGENS or not re.match(r'https?://', str(url)) or not str(nome).strip():
        raise ValueError('origem do mnemônico: modo encontrado/adaptado, url http(s) e nome da fonte')
    return bloco('origem', f'{_ORIGENS[modo]} <a href="{url}">{_sem_quebras(nome)}</a>.')


def chip(texto: str, cor: str = '#1e88e5', destaque: bool = False) -> str:
    fundo = 'background:rgba(249,168,37,0.35);font-weight:bold;' if destaque else ''
    borda = '2px solid #ef8f00' if destaque else f'1px solid {cor}'
    return (f'<span style="display:inline-block;border:{borda};border-radius:12px;{fundo}'
            f'padding:1px 8px;margin:2px 1px;white-space:nowrap;">{_sem_quebras(texto)}</span>')


def fluxo(etapas: list[str], seta: str = '➜', destaque: set[int] | None = None) -> str:
    """Etapas em etiquetas; `destaque` marca (por índice) a etapa em foco no cartão."""
    if len(etapas) < 2:
        raise ValueError('Fluxo requer ao menos duas etapas')
    marcadas = destaque or set()
    sep = f'<span style="margin:0 3px;opacity:0.7;">{seta}</span>'
    return '<div style="line-height:2;">' + sep.join(chip(e, destaque=i in marcadas) for i, e in enumerate(etapas)) + '</div>'


def tabela(cabecalho: list[str], linhas: list[list[str]]) -> str:
    if not cabecalho or any(len(l) != len(cabecalho) for l in linhas):
        raise ValueError('Todas as linhas da tabela precisam ter o tamanho do cabeçalho')
    cel = f'border:1px solid {_BORDA_SUAVE};padding:4px 6px;vertical-align:top;'
    head = ''.join(f'<th style="{cel}background:rgba(0,137,123,0.18);text-align:left;">{_sem_quebras(h)}</th>'
                   for h in cabecalho)
    body = ''.join('<tr>' + ''.join(f'<td style="{cel}">{_sem_quebras(c)}</td>' for c in linha) + '</tr>'
                   for linha in linhas)
    return (f'<table style="border-collapse:collapse;width:100%;font-size:0.92em;margin:4px 0;">'
            f'<tr>{head}</tr>{body}</table>')


def _wrapper(conteudo: str) -> str:
    return f'<div style="text-align:left;line-height:1.45;font-size:0.92em;">{conteudo}</div>'


def frente(texto: str) -> str:
    """Frente alinhada à esquerda para situações longas (D) e textos Cloze."""
    return f'<div style="text-align:left;line-height:1.5;">{_sem_quebras(texto)}</div>'


def verso_ce(gabarito: str, blocos: list[str], resumo: str) -> str:
    """Prefixo exato do gabarito + blocos + Memorize obrigatório no fim."""
    if gabarito not in PREFIXO:
        raise ValueError('Gabarito deve ser C ou E')
    if not blocos:
        raise ValueError('Verso precisa de ao menos o bloco da regra')
    if not resumo.strip():
        raise ValueError('Memorize obrigatório: resumo da explicação')
    texto = PREFIXO[gabarito] + _wrapper(''.join(blocos) + memorize(resumo))
    erros = problemas_html(texto)
    if erros:
        raise ValueError('; '.join(erros))
    return texto


def extra_cloze(blocos: list[str], resumo: str, origem=None) -> str:
    """Extra do Cloze; `origem` (só mnemônico) põe o bloco de origem antes do Memorize."""
    if not blocos or not resumo.strip():
        raise ValueError('Extra Cloze precisa de explicação e Memorize')
    fim = (origem_mnemonico(origem) if origem is not None else '') + memorize(resumo)
    texto = _wrapper(''.join(blocos) + fim)
    erros = problemas_html(texto)
    if erros:
        raise ValueError('; '.join(erros))
    return texto


# ------------------------------------------------------------ segurança/compatibilidade
PROIBIDOS = [
    (re.compile(r'<\s*(script|iframe|object|embed|link|style|meta|form)\b', re.I), 'tag proibida no Anki'),
    (re.compile(r'\son[a-z]+\s*=', re.I), 'atributo de evento (on...=) proibido'),
    (re.compile(r'javascript\s*:', re.I), 'URL javascript: proibida'),
    (re.compile(r'\bsrc\s*=\s*["\']?\s*(?:https?:)?//', re.I), 'mídia remota; incorporar arquivo local'),
    (re.compile(r'position\s*:\s*(?:fixed|absolute)', re.I), 'position fixed/absolute quebra o leitor'),
    (re.compile(r'@import|url\s*\(', re.I), 'CSS externo/url() proibido'),
]
_PARES = ('div', 'span', 'table', 'tr', 'td', 'th', 'b', 'i', 'u', 'ul', 'ol', 'li', 'p')


def problemas_html(texto: str) -> list[str]:
    """Lista problemas de segurança/compatibilidade; vazio quando o HTML passa."""
    erros = [msg for padrao, msg in PROIBIDOS if padrao.search(texto)]
    if '\t' in texto or '\n' in texto:
        erros.append('TAB ou quebra de linha dentro do campo')
    for tag in _PARES:
        abre = len(re.findall(rf'<{tag}(?:\s[^>]*)?>', texto, re.I))
        fecha = len(re.findall(rf'</{tag}\s*>', texto, re.I))
        if abre != fecha:
            erros.append(f'tag <{tag}> desbalanceada ({abre} abertas, {fecha} fechadas)')
    return erros
