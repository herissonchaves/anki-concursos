# Arquivos gerados e Git local

Leia ao gravar arquivos de um pedido ou ao preparar um commit. O `SKILL.md` da raiz traz só o
resumo.

## Onde salvar o que as skills geram

Tudo fica **dentro deste repositório**. Não grave lotes nem entregáveis na pasta do material de
estudo, na Área de Trabalho ou em outro local. Rascunhos (texto do PDF, JSON de importação de
questões) vão para o scratchpad da sessão.

**Lote em geração e entregáveis:** `output/<CONCURSO>_<Tema>/`, por exemplo
`output/PRF_Navegadores/` ou `output/PF_Agente_Inquerito/`. A pasta `output/` é ignorada pelo Git.

- `fonte/gerar_lote.py` (copiado de `skills/gerar-revisao-anki/modelos/gerar_lote_modelo.py`) e
  `fonte/sinais_resolvidos.json`;
- `lote/`: `anki_certo_errado.tsv`, `anki_cloze.tsv` e `relatorios/`, gravados pelo `montar_lote.py`
  e conferidos pelo `finalizar_lote.py` (desde a 2.30 sem prévia HTML, ZIP ou APKG);
- na raiz da pasta, só o que for de atualização de notas existentes (`.colpkg`, TSVs) e o
  `duplicatas_colecao.txt` do `finalizar_lote.py`.

Regras:
- Hérisson importa os dois TSVs de `lote/` e depois apaga a pasta inteira. Depois de importado, o card vive na
  coleção do Anki: correções usam `melhorar-cartoes-anki` sobre a coleção, não o lote. Pasta
  vazia ou ausente é o estado normal; crie-a quando for gravar.
- Enquanto a pasta existir, ela é a fonte do lote (correções antes da importação regeneram a partir
  de `fonte/`). Não apague nem sobrescreva entregáveis que ainda estejam ali: o `finalizar_lote.py`
  não grava nada fora de `lote/` além do `duplicatas_colecao.txt`.
- No fechamento, informe o caminho completo dos dois TSVs a importar, o baralho e o tipo de nota de cada um.

**O que fica versionado de cada lote:** só o que serve a pedidos futuros, em `referencias/`:
questões, conteúdos, notícias e prioridades novos ou atualizados, o `usado_em` gravado pelo
`montar_lote.py` e a linha do lote em `referencias/historico_lotes.tsv` (gravada pelo
`finalizar_lote.py`: data, lote, baralho, totais R/D/Cloze e IDs do banco usados). Lotes antigos
em `lotes/` saíram do Git na 2.24; o histórico deles continua em `git log -- lotes/`.

## Git local

- Consulte o Git local sempre que precisar recuperar decisões, comparar versões ou entender mudanças. Hérisson já autorizou consultas ao histórico, ao estado e aos diffs desse repositório.
- Após concluir e verificar alterações importantes do projeto, salve-as em commits locais com mensagens que descrevam a mudança. A preferência vale para as tarefas futuras desse repositório, mesmo quando o pedido não mencionar commits.
- Confira o estado e o diff antes de preparar o commit. Inclua somente mudanças da tarefa ou expressamente autorizadas. Preserve trabalho alheio e deixe backups privados do Anki, credenciais e arquivos temporários fora dos commits.
- Confira o commit e informe seu identificador no fechamento. A autorização cobre commits locais. Envio a remotos ou reescrita de histórico exige autorização própria.
- Rotina: `git status` antes de editar; `git log --oneline -- ARQUIVO` e `git show` para entender uma regra antes de mudá-la; `git diff` e testes depois de editar scripts ou regras cobertas pelos testes.
- Adicione arquivos pelo nome, sem `git add -A` às cegas. Um commit por mudança coerente, com mensagem em português no imperativo que diga o quê e por quê. Não use `--no-verify`.
- Também exigem autorização própria: `reset --hard`, `rebase`, `commit --amend` de commit existente, `checkout --`/`restore` que descarte trabalho, apagar ou trocar de branch e alterar remotos. Para mudanças grandes ou experimentais, sugira uma branch nova.
- Versione `referencias/` (banco de referências, inclusive `referencias/imagens/` com as figuras recortadas dos cadernos oficiais); nas questões, só o item oficial da banca: enunciado, alternativas, gabarito, fonte e metadados. Nunca comentários ou resoluções de cursos e sites de questões, nem dados pessoais de marcas-d'água; rode `referencias.py validar` antes do commit.
- Nunca versione PDFs ou materiais de cursos (direitos autorais e marcas-d'água com dados pessoais), `output/`, `.colpkg`/`.apkg`/`collection.*`, pacotes `.zip` exportados, `.venv/`, `uv.lock` e caches. Se aparecerem no `git status`, proponha incluí-los no `.gitignore`.
- Num pedido de cartões, o commit leva só `referencias/` (e as mudanças de regras ou scripts, se houver); nunca o conteúdo de `output/`.
