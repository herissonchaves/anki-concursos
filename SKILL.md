---
name: anki-concursos
description: Skill principal do Anki-Concursos. Use para criar, selecionar, auditar ou melhorar flashcards Anki de concursos (PRF por padrão, Agente PF e outros quando pedidos) em Certo/Errado estilo Cebraspe e Cloze, exportados em TSV; para caderno de erros, análise de backup .colpkg e orientação de estudo no Anki/FSRS. Encaminha à skill especializada e define o Git local e onde salvar os lotes.
---

# Anki-Concursos

O repositório de referência fica em `D:\NextCloud - Arquivos\IA Agents\Anki-Concursos`.
Neste computador Windows, a cópia sincronizada fica em
`C:\Users\Herisson.DESKTOP-EHB23TA\Nextcloud\IA Agents\Anki-Concursos`. A skill
de entrada instalada no Claude (`~/.claude/skills/anki-concursos/SKILL.md`) aponta
para este arquivo. Sua fonte versionada é
[`instalacao/anki-concursos/SKILL.md`](instalacao/anki-concursos/SKILL.md): ao mudar
o roteamento ou o perfil, edite a fonte e copie-a para a pasta instalada.

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
| Consultar, salvar ou vincular questões de concursos de referência | [referencias-questoes](skills/referencias-questoes/SKILL.md) |
| Orientar rotina, carga de revisão e FSRS | [orientar-estudo-anki](skills/orientar-estudo-anki/SKILL.md) |

Para os portões de cada rota, o roteamento obrigatório de Língua Portuguesa e os
casos de regressão do roteamento, veja
[orquestracao_multi_skill.md](skills/gerar-revisao-anki/references/orquestracao_multi_skill.md).

Toda criação de cartões autorais (R, D, Cloze e caderno de erros) usa também
[referencias-questoes](skills/referencias-questoes/SKILL.md): reaproveita as questões
de concursos do arquivo enviado e do banco `referencias/`, e salva ali, em Markdown
padronizado, toda questão lida no anexo ou na internet.

Para conteúdo de PRF ou Agente da Polícia Federal, use
[perfil-carreiras-policiais](skills/perfil-carreiras-policiais/SKILL.md) para
selecionar as especializações por disciplina. Considere o concurso indicado
no pedido. Na ausência de outro alvo explícito, a prioridade do projeto é PRF.

## Testes

As suítes de `automacao-anki-python` e `gerar-revisao-anki` são configuradas
no `pyproject.toml`. Rode o comando na raiz do repositório.

```bash
uv run --python 3.13 --with-requirements skills/automacao-anki-python/requirements-dev.txt pytest
```

Use Python 3.12 ou 3.13 para a suíte padrão. Para cobrir backups modernos e a ida
e volta da coleção nessas versões, inclua também
[`requirements-optional.txt`](skills/automacao-anki-python/requirements-optional.txt)
com outro `--with-requirements`. Os testes que dependem de `zstandard` ou
`anki` são pulados quando a biblioteca correspondente está ausente.

## Git local

- Consulte o Git local sempre que precisar recuperar decisões, comparar versões ou entender mudanças. Hérisson já autorizou consultas ao histórico, ao estado e aos diffs desse repositório.
- Após concluir e verificar alterações importantes do projeto, salve-as em commits locais com mensagens que descrevam a mudança. A preferência vale para as tarefas futuras desse repositório, mesmo quando o pedido não mencionar commits.
- Confira o estado e o diff antes de preparar o commit. Inclua somente mudanças da tarefa ou expressamente autorizadas. Preserve trabalho alheio e deixe backups privados do Anki, credenciais e arquivos temporários fora dos commits.
- Confira o commit e informe seu identificador no fechamento. A autorização cobre commits locais. Envio a remotos ou reescrita de histórico exige autorização própria.
- Rotina: `git status` antes de editar; `git log --oneline -- ARQUIVO` e `git show` para entender uma regra antes de mudá-la; `git diff` e testes depois de editar scripts ou regras cobertas pelos testes.
- Adicione arquivos pelo nome, sem `git add -A` às cegas. Um commit por mudança coerente, com mensagem em português no imperativo que diga o quê e por quê. Não use `--no-verify`.
- Também exigem autorização própria: `reset --hard`, `rebase`, `commit --amend` de commit existente, `checkout --`/`restore` que descarte trabalho, apagar ou trocar de branch e alterar remotos. Para mudanças grandes ou experimentais, sugira uma branch nova.
- Versione `referencias/` (banco de questões) só com o item oficial da banca: enunciado, alternativas, gabarito, fonte e metadados. Nunca comentários ou resoluções de cursos e sites de questões, nem dados pessoais de marcas-d'água; rode `referencias.py validar` antes do commit.
- Nunca versione PDFs ou materiais de cursos (direitos autorais e marcas-d'água com dados pessoais), `.colpkg`/`.apkg`/`collection.*`, pacotes `.zip` exportados, `.venv/`, `uv.lock` e caches. Se aparecerem no `git status`, proponha incluí-los no `.gitignore`.

## Onde salvar os lotes gerados

Todo arquivo gerado pelas skills (TSVs, relatórios, ZIP e o script que montou o lote) fica **dentro deste repositório**, em `lotes/<CONCURSO>/<Missao_NN_Tema>/`, por exemplo `lotes/PRF/Missao_09_Navegadores/`. Não grave lotes na pasta do material de estudo.

- `lote/`: `anki_certo_errado.tsv`, `anki_cloze.tsv` e `relatorios/` (é o diretório passado ao exportador).
- `fonte/`: script gerador e decisões sobre os sinais do lint, para refazer hashes após uma edição.
- `<CONCURSO>_<Tema>.zip`: pacote final validado, ignorado pelo Git porque se regenera a partir de `lote/`.
- Use outro concurso no lugar de `PRF` quando o alvo for outro (por exemplo `lotes/PF_Agente/`). Antes de versionar, confira que nenhum arquivo do lote contém dados pessoais copiados do material, como nome ou CPF das marcas-d'água.
- Versione `lote/` e `fonte/` no commit da geração, para manter o histórico dos cartões, junto com as questões novas ou o `usado_em` atualizado em `referencias/`.

## Banco de questões de referência

`referencias/questoes/<disciplina>/<assunto>/<id>.md` guarda as questões de concursos
usadas como referência ou inspiração; `referencias/assuntos.md` e
`referencias/indice.tsv` são gerados por
`skills/referencias-questoes/scripts/referencias.py`, que busca e mostra questões sem
abrir os arquivos. Formato e fluxo em [referencias-questoes](skills/referencias-questoes/SKILL.md).
