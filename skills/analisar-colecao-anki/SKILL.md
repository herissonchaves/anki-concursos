---
name: analisar-colecao-anki
description: Analisa backups Anki somente em leitura, distingue notas e cartões e identifica candidatos a duplicação e dificuldades sem inferir dados ausentes.
---

# analisar-colecao-anki

Leia `../gerar-revisao-anki/references/nucleo-pedagogico.md` primeiro.

O leitor agora aceita `collection.anki21b` com descompressão Zstandard limitada.
Use Python 3.12/3.13 com `zstandard` (`../automacao-anki-python/requirements-optional.txt`);
o 3.14+ traz `compression.zstd`, mas não é a versão testada no Windows. Jamais recue
para o stub legado quando o banco moderno falhar. Para a varredura completa, o
diagnóstico por categorias e o relatório `analise_backup_anki.txt`, siga
`../gerar-revisao-anki/references/analise-backup-anki.md`. Para revisão solicitada, siga
`../gerar-revisao-anki/references/revisao-integral-e-linguagem.md`.

Inventarie modelo, campos, notas, cartões, datas e logs realmente legíveis usando os scripts de automação. Um backup moderno incompatível não representa coleção vazia; não analisar stub de compatibilidade como coleção real. Ausência de revlog não prova ausência de estudo. Similaridade lexical apenas indica candidatos: compare alvos/operações antes de recomendar manter, reformular, fundir ou suspender. Não executar essas mudanças. Para Cloze, contar e examinar cada vista. Registrar limites, evidências e recomendações priorizadas. Só gerar/reformular se solicitado. Para carga e lapsos, consultar `../orientar-estudo-anki/SKILL.md`.

## Regras comuns

- **Cloze:** para recomendar mudança de omissões, usar `../gerar-revisao-anki/references/protocolo_cloze_cientifico.md`; contar e examinar cada vista e não remover índices sem avaliar cartões e histórico.
