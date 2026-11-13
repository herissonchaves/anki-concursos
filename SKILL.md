---
name: anki-concursos
description: Skill principal do Anki-Concursos. Encaminha pedidos de criação, seleção, auditoria e melhoria de flashcards para concursos, análise de backups e orientação de estudo no Anki. Define o fluxo de Git local do projeto.
---

# Anki-Concursos

O repositório de referência fica em `D:\NextCloud - Arquivos\IA Agents\Anki-Concursos`.

## Escolha do fluxo

Abra a skill correspondente ao pedido e siga suas instruções. Carregue as
demais apenas quando o pedido ou a skill escolhida exigir. Os caminhos abaixo
são relativos à raiz do projeto.

| Pedido | Skill |
| --- | --- |
| Selecionar temas de um PDF | [selecionar-conteudos-pdf-anki](skills/selecionar-conteudos-pdf-anki/SKILL.md) |
| Criar cartões C/E ou Cloze | [gerar-revisao-anki](skills/gerar-revisao-anki/SKILL.md) |
| Trabalhar questões erradas | [caderno-erros-anki](skills/caderno-erros-anki/SKILL.md) |
| Conferir a qualidade de cartões | [auditar-cartoes-anki](skills/auditar-cartoes-anki/SKILL.md) |
| Explicar ou reformular cartões existentes | [melhorar-cartoes-anki](skills/melhorar-cartoes-anki/SKILL.md) |
| Inspecionar um backup | [analisar-colecao-anki](skills/analisar-colecao-anki/SKILL.md) |
| Extrair material ou validar e exportar arquivos | [automacao-anki-python](skills/automacao-anki-python/SKILL.md) |
| Orientar rotina, carga de revisão e FSRS | [orientar-estudo-anki](skills/orientar-estudo-anki/SKILL.md) |

Para conteúdo de PRF ou Agente da Polícia Federal, use
[perfil-carreiras-policiais](skills/perfil-carreiras-policiais/SKILL.md) para
selecionar as especializações por disciplina. Considere o concurso indicado
no pedido. Na ausência de outro alvo explícito, a prioridade do projeto é PRF.

## Git local

- Consulte o Git local sempre que precisar recuperar decisões, comparar versões ou entender mudanças. Hérisson já autorizou consultas ao histórico, ao estado e aos diffs desse repositório.
- Após concluir e verificar alterações importantes do projeto, salve-as em commits locais com mensagens que descrevam a mudança. A preferência vale para as tarefas futuras desse repositório, mesmo quando o pedido não mencionar commits.
- Confira o estado e o diff antes de preparar o commit. Inclua somente mudanças da tarefa ou expressamente autorizadas. Preserve trabalho alheio e deixe backups privados do Anki, credenciais e arquivos temporários fora dos commits.
- Confira o commit e informe seu identificador no fechamento. A autorização cobre commits locais. Envio a remotos ou reescrita de histórico exige autorização própria.
