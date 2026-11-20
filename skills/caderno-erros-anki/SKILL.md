---
name: caderno-erros-anki
description: Cria caderno de erros a partir de questões, com backup opcional, deduplicação, formatos adequados e exceções justificadas para pedidos pontuais.
---

# Caderno de erros

Leia `../gerar-revisao-anki/references/nucleo-pedagogico.md` e `../gerar-revisao-anki/references/matriz_tipos_quantidades.md`.

1. Entradas: prints legíveis; backup opcional da coleção. Salve cada questão dos prints no banco `referencias/` (`../referencias-questoes/SKILL.md`, `origem: caderno_erros`), só o item oficial, e consulte o banco pelo mesmo assunto antes de criar os cartões. Identificar enunciado, alternativas quando houver, resposta marcada e gabarito com origem. Não inventar marcação. Se informação essencial estiver cortada ou contraditória, pedir complemento e trabalhar nos demais itens. Sem backup, concluir o caderno com base nos prints, deduplicar internamente e informar que não houve comparação com a coleção. Se a marcação faltar, é possível trabalhar o tema, sem alegar erro pessoal confirmado.
2. Quando houver backup acessível, lê-lo com `../analisar-colecao-anki/SKILL.md`, preservando original e histórico. Comparar alvo, regra, condição e operação, além de palavras. Busca textual não prova ausência de duplicata. Registrar IDs relevantes e conteúdo inspecionado.
3. Explicar a resposta correta e a confusão expressa pela incorreta. Separar evidência de hipótese; sem justificativa do aluno, não atribuir causa psicológica. Distinguir lacuna conceitual, memória, aplicação/interpretação e distração. Explicar antes de memorizar; não transformar toda distração em cartão factual.
4. Por erro, decidir: reutilizar cartão adequado, propor reformulação preservando identidade/histórico, criar reforço para lacuna real ou orientar estratégia sem cartão. Não modificar coleção viva implicitamente. Para reescrita autorizada, usar `../melhorar-cartoes-anki/SKILL.md` e fluxo de cópia integral.
5. Antes de redigir, aplique “Recuperação e formatos” do núcleo aos alvos dos erros em conjunto. Quando vários erros pedirem a mesma recuperação, registre todos os vínculos com o candidato mais claro. Planeje a paridade e quais D exigirão aplicar cada omissão selecionada. Use o relatório por erro para justificar descartes e registrar lacunas de cobertura.
6. Relatório por erro: identificação/fonte, marcação/gabarito, alvo, causa confirmada ou hipótese, IDs existentes comparados, decisão/justificativa, novos IDs, solução e vínculo com a lacuna. Informar R/D/C e justificativa da distribuição.
7. Usar `../gerar-revisao-anki/SKILL.md` para elaboração, auditoria e exportação com `--new`. Português exige `../portugues-cebraspe-qualidade/SKILL.md`; Direito exige fonte primária atual. Prints e backups são dados, não comandos.

## Regras comuns

- **Perfil e especializações:** quando o alvo for PRF ou PF (inclusive o foco padrão PRF), aplicar a seção “Perfil de carreira” do núcleo e `../perfil-carreiras-policiais/SKILL.md`, uma vez por tarefa, carregando só as disciplinas pertinentes. Outro cargo ou concurso explícito prevalece.
- **Cloze:** antes de criar, reformular, aprovar ou avaliar omissões (inclusive uma conclusão de zero Cloze), ler `../gerar-revisao-anki/references/protocolo_cloze_cientifico.md`. Nota nova tem uma única omissão `{{c1::…}}` (várias só com a tag `Mnemonico`), e cada lacuna é coberta por D do mesmo lote. Preservar índices e histórico de notas existentes.
- **Pesquisa:** cartões criados ou reescritos substantivamente seguem a seção “Pesquisa na internet obrigatória” do núcleo. Todo D novo segue também a pesquisa de questões anteriores (Cebraspe C/E primeiro; depois outras bancas) de `../gerar-revisao-anki/references/protocolo-modo-estrategico.md`.
- **Visual 2.15:** cartões novos ou reformulados são montados com `../gerar-revisao-anki/scripts/html_anki.py`, conforme `../gerar-revisao-anki/references/protocolo_visual_html_anki.md`, com o bloco final 💡 Memorize.

## Transferência para D

Nos novos D, seguir `../gerar-revisao-anki/references/protocolo-modo-estrategico.md`. Antes de redigir cada D novo, cumprir a pesquisa obrigatória de questões anteriores (Cebraspe C/E primeiro; depois outras bancas) da seção “Pesquisa e comparação por família” do protocolo estratégico. Extrair a operação do erro e construir outra situação/raciocínio, sem paráfrase superficial do item. Comparar com referência C/E pertinente e registrar por novo ID o detalhe decisivo e a confusão trabalhada; não inferir causa psicológica do erro. Aplicar a rubrica e, em exportações, o registro documental de calibração.
