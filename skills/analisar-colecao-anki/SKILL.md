---
name: analisar-colecao-anki
description: Analisa backups Anki somente em leitura, distingue notas e cartões e identifica candidatos a duplicação e dificuldades sem inferir dados ausentes.
---

# analisar-colecao-anki — 2.1

Leia `../gerar-revisao-anki/references/nucleo-pedagogico.md` primeiro.

O leitor agora aceita `collection.anki21b` com descompressão Zstandard limitada.
Use Python 3.14+ ou a dependência `zstandard`; jamais recue para o stub legado
quando o banco moderno falhar. Para revisão solicitada, siga
`../gerar-revisao-anki/references/revisao-integral-e-linguagem.md`.

Inventarie modelo, campos, notas, cartões, datas e logs realmente legíveis usando os scripts de automação. Um backup moderno incompatível não representa coleção vazia; não analisar stub de compatibilidade como coleção real. Ausência de revlog não prova ausência de estudo. Similaridade lexical apenas indica candidatos: compare alvos/operações antes de recomendar manter, reformular, fundir ou suspender. Não executar essas mudanças. Para Cloze, contar e examinar cada vista. Registrar limites, evidências e recomendações priorizadas. Só gerar/reformular se solicitado. Para carga e lapsos, consultar `../orientar-estudo-anki/SKILL.md`.

## Escolha de Cloze — 2.4

Antes de criar, reformular ou aprovar omissões, ler `../gerar-revisao-anki/references/protocolo_cloze_cientifico.md`. Avaliar primeiro se o alvo merece Cloze; clareza da frase sozinha não basta. Conceitos e listas importantes são candidatos, sem obrigação de transformar todo conteúdo em lacuna. Registrar inadequação de formato separadamente de ambiguidade.
