#!/usr/bin/env python3
"""Padrão único de formatação dos cards: CSS base dos tipos de nota exportados.

É o mesmo CSS dos tipos "Basic" e "Cloze" da coleção do usuário (Arial 20 px, entrelinha 1,5,
centralizado, preto sobre branco; Anki inverte no modo noturno), onde estão os cards de
Informática que serviram de referência visual. Os campos usam só os componentes de
`html_anki.py` por cima desta base. Não mudar tamanhos, fontes ou cores por lote.
"""
CSS_BASE = """.card {
    font-family: arial;
    font-size: 20px;
    line-height: 1.5;
    text-align: center;
    color: black;
    background-color: white;
}
"""

CSS_CLOZE = CSS_BASE + """.cloze {
    font-weight: bold;
    color: blue;
}
.nightMode .cloze {
    color: lightblue;
}
"""

# Identidade dos tipos de nota criados pelo exportador (não mudar: mudaria o tipo das notas já importadas).
MODELO_CE = (1987052101, 'Anki-Concursos - C/E')
MODELO_CLOZE = (1987052102, 'Anki-Concursos - Cloze')
