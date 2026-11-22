#!/usr/bin/env python3
"""Regras de tags e de Cloze mnemônico dos lotes novos (2.33). Documento: references/tags.md.

Tags de um card novo, nesta ordem:
- uma hierárquica de conteúdo `Disciplina::Assunto::Topico` (três níveis ou mais);
- o nome curto do PDF (`Missao_07`) e as `Pagina_NN`, só em card feito sobre o PDF;
- exatamente uma de tipo: `Rapida`, `Desafiadora` ou `Cloze`;
- no D, uma por questão do banco que o inspirou (nome do arquivo .md em referencias/questoes/).
Nada mais: concurso, cargo, banca, estilo, "revisão", "mnemônico" e afins são proibidos.

Os nomes antigos de tipo (`Tipo_Revisao_Rapida`, `Tipo_Desafiadora_Cebraspe`) continuam
reconhecidos só na leitura de notas e lotes antigos (`eh_rapida`, `eh_desafiadora`).
"""
from __future__ import annotations

import re

RAPIDA, DESAFIADORA, CLOZE = 'Rapida', 'Desafiadora', 'Cloze'
TIPOS = (RAPIDA, DESAFIADORA, CLOZE)
LEGADO_RAPIDA, LEGADO_DESAFIADORA = 'Tipo_Revisao_Rapida', 'Tipo_Desafiadora_Cebraspe'

# Tag inteira (sem diferenciar maiúsculas) que não pode aparecer em card novo.
PROIBIDAS = {
    # concursos, cargos e bancas
    'prf', 'pf', 'pf_agente', 'agente_pf', 'agente', 'policia_federal', 'policia_rodoviaria_federal',
    'pc', 'pm', 'pcdf', 'pmdf', 'depen', 'abin', 'inss', 'tcu', 'cgu', 'receita_federal',
    'cebraspe', 'cespe', 'fgv', 'fcc', 'vunesp', 'concurso', 'concursos',
    # genéricas
    'estilo_cebraspe', 'mnemonico', 'mnemônico', 'revisao', 'revisão', 'revisao_pdf', 'revisão_pdf',
    'pdf', 'lote', 'novo', 'novos', 'anki', 'importado', 'cloze_mnemonico', 'caderno_erros',
    'caderno_de_erros', 'questao', 'questoes', 'rapido', 'desafiador', 'desafio',
}
PREFIXOS_PROIBIDOS = ('tipo_', 'estilo_', 'revisao_', 'revisão_', 'prioridade', 'concurso_')
PAGINA = re.compile(r'Pagina_\d{2,}')
QUESTAO = re.compile(r'[a-z0-9]+(?:-[a-z0-9_]+)+')  # ex.: cebraspe-2021-prf-080


def eh_rapida(tags: str) -> bool:
    t = tags.split()
    return RAPIDA in t or LEGADO_RAPIDA in t


def eh_desafiadora(tags: str) -> bool:
    t = tags.split()
    return DESAFIADORA in t or LEGADO_DESAFIADORA in t


def proibida(tag: str) -> bool:
    baixo = tag.casefold()
    return baixo in PROIBIDAS or baixo.startswith(PREFIXOS_PROIBIDOS)


def problemas_tags(tags: str, tipo: str) -> list[str]:
    """Problemas das tags de um card novo; `tipo` é RAPIDA, DESAFIADORA ou CLOZE."""
    lista = tags.split()
    erros = [f'tag proibida "{t}" (só conteúdo, PDF, página, tipo e questão de origem)' for t in lista if proibida(t)]
    tipos = [t for t in lista if t in TIPOS]
    if tipos != [tipo]:
        erros.append(f'precisa de exatamente uma tag de tipo, "{tipo}" (achou: {", ".join(tipos) or "nenhuma"})')
    hier = [t for t in lista if '::' in t]
    if len(hier) != 1:
        erros.append(f'precisa de exatamente uma tag Disciplina::Assunto::Topico (achou {len(hier)})')
    elif len([p for p in hier[0].split('::') if p]) < 3 or '' in hier[0].split('::'):
        erros.append(f'tag "{hier[0]}" precisa de três níveis: Disciplina::Assunto::Topico')
    paginas = [t for t in lista if PAGINA.fullmatch(t)]
    questoes = [t for t in lista if QUESTAO.fullmatch(t)]
    if questoes and tipo != DESAFIADORA:
        erros.append(f'tag de questão ({", ".join(questoes)}) só em Desafiadora')
    resto = [t for t in lista if t not in tipos and t not in hier and t not in paginas and t not in questoes
             and not proibida(t)]
    if paginas and len(resto) != 1:
        erros.append('Pagina_NN exige exatamente uma tag com o nome curto do PDF (ex.: Missao_07)'
                     + (f'; sobrou: {", ".join(resto)}' if resto else ''))
    if not paginas and resto:
        erros.append(f'tag sem categoria: {", ".join(resto)} (nome do PDF só com Pagina_NN)')
    return erros


# ------------------------------------------------------------ Cloze mnemônico
TITULO_MNEMONICO = re.compile(r'^(?:<[^>]+>|\s)*Mnem[oô]nico\s+([^:<]{1,40}?)\s*:', re.I)
LACUNA = re.compile(r'\{\{c(\d+)::([^{}]*?)(?:::[^{}]*?)?\}\}')
ORIGEM = 'Origem do mnemônico'


def sigla_mnemonico(frente: str) -> str | None:
    """Sigla do título `Mnemônico SIGLA:` no início da frente, ou None se não for mnemônico."""
    m = TITULO_MNEMONICO.match(frente)
    return m.group(1).strip() if m else None


def mnemonico_fora_do_formato(frente: str) -> bool:
    """Frente que fala em dica/mnemônico/macete sem o título `Mnemônico SIGLA:` (ex.: "Dica autoral ...")."""
    return sigla_mnemonico(frente) is None and bool(
        re.search(r'dica\s+autoral|mnem[oô]nico|\bmacete\b', frente, re.I))


def problemas_mnemonico(frente: str, extra: str) -> list[str]:
    """Formato do Cloze mnemônico: título na frente, letras-pista visíveis antes de cada lacuna,
    nenhuma origem na frente e bloco de origem (autoral ou link) no Extra."""
    erros = []
    if sigla_mnemonico(frente) is None:
        erros.append('mnemônico precisa começar a frente com "Mnemônico SIGLA:"')
    if re.search(r'dica\s+autoral|\bautoral\b|\bfonte\s*:', frente, re.I):
        erros.append('origem do mnemônico (autoral/fonte) vai no verso, não na frente')
    lacunas = list(LACUNA.finditer(frente))
    if len(lacunas) < 2:
        erros.append('mnemônico omite cada termo numa lacuna própria (achou '
                     f'{len(lacunas)}); a lista inteira numa lacuna só é proibida')
    for m in lacunas:
        if not re.search(r'[A-ZÀ-Ý]$', frente[:m.start()]):
            erros.append(f'lacuna "{m.group(2)[:30]}" sem letra-pista visível colada antes (ex.: C{{{{c1::ompetência}}}})')
    if ORIGEM.casefold() not in extra.casefold():
        erros.append(f'Extra do mnemônico precisa do bloco "{ORIGEM}"')
    elif not (re.search(r'\bAutoral\b', extra) or re.search(r'<a\s[^>]*href=["\']https?://', extra, re.I)):
        erros.append('bloco de origem precisa dizer "Autoral" ou trazer o link da fonte')
    return erros
