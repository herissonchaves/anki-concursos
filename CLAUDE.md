# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ponto de partida

Este repositório é um conjunto de **skills** (instruções em Markdown + scripts Python) para gerar,
auditar e manter flashcards Anki de concursos policiais (PRF por padrão; Agente PF quando pedido)
no estilo Cebraspe. Responda e escreva em português.

**Sempre comece por [`SKILL.md`](SKILL.md) na raiz**: ele tem o perfil do usuário, a tabela de
roteamento pedido → skill em `skills/<nome>/SKILL.md`, a versão do projeto e as regras de Git. Não
duplique aqui regras que ficam lá; ao mudar regras, scripts ou fluxos, suba a **versão única** no
`SKILL.md` da raiz no mesmo commit (os demais `SKILL.md` e `references/` não levam versão).

`instalacao/anki-concursos/SKILL.md` é só o lançador copiado para `~/.claude/skills/`; recopie-o
apenas quando a descrição (gatilhos) ou o caminho do repositório mudar.

## Testes

Da raiz do repositório (Python 3.12 ou 3.13; o 3.15 não tem wheel do PyYAML no Windows):

```bash
uv run --python 3.13 --with-requirements skills/automacao-anki-python/requirements-dev.txt pytest
# um arquivo ou um teste
uv run --python 3.13 --with-requirements skills/automacao-anki-python/requirements-dev.txt pytest skills/gerar-revisao-anki/tests/test_tags_233.py -k NOME
# backups modernos e ida e volta da coleção (zstandard, anki==26.9.3)
uv run --python 3.13 --with-requirements skills/automacao-anki-python/requirements-dev.txt --with-requirements skills/automacao-anki-python/requirements-optional.txt pytest
```

O `pyproject.toml` define as três suítes (`automacao-anki-python`, `gerar-revisao-anki`,
`referencias-questoes`) e o `pythonpath` com as pastas `scripts/` e fixtures, por isso os testes
importam os scripts pelo nome do módulo. Testes que dependem de `zstandard`/`anki` são pulados sem a
biblioteca: declare-os como não executados. `test_estrutura.py` confere que todo caminho citado nas
instruções Markdown existe — ao renomear ou mover arquivos, atualize os links e rode a suíte. Suíte
verde não é aprovação pedagógica (`skills/automacao-anki-python/references/testes-desenvolvimento.md`).

Scripts avulsos rodam com `uv run --no-project python -I -X utf8 <script>` (com `--with pymupdf` para
`extrair_pdf.py` e `cebraspe_cdn.py`).

## Arquitetura

- **Pipeline de lote** (resumo operacional e comandos em
  `skills/gerar-revisao-anki/references/roteiro-lote-pdf.md`, que substitui a leitura das demais
  referências nos casos comuns):
  1. `extrair_pdf.py` gera texto limpo do PDF; `referencias.py importar` + `completar` extraem e salvam
     as questões no banco.
  2. Copia-se `skills/gerar-revisao-anki/modelos/gerar_lote_modelo.py` para
     `output/<CONCURSO>_<Tema>/fonte/gerar_lote.py`, que contém **só conteúdo** (fontes, `COBERTURA`,
     cartões R/D/Cloze como dicts de chaves curtas, blocos de `html_anki.py`).
  3. `montar_lote.py` (classe `Lote`) faz o resto: TSVs, embaralhamento C/E, tags (regras em
     `regras_tags.py` / `references/tags.md`), calibração, revisão, cobertura do PDF, relatórios em
     `lote/relatorios/` e registro de `usado_em` no banco. Falha em violações (Alta/Média sem card, tag
     proibida, questão não citada). Os validadores `validar_*.py` e `auditar_clareza.py` são chamados por ele.
  4. `skills/automacao-anki-python/scripts/finalizar_lote.py` valida tudo, avisa duplicatas na coleção
     e grava a linha em `referencias/historico_lotes.tsv`. A entrega são os dois TSVs de `lote/`
     (desde a 2.30 sem prévia HTML, ZIP ou APKG).
- **Formatação única** dos cards: CSS de `skills/gerar-revisao-anki/scripts/estilo_anki.py`
  (Arial 20 px); só os componentes de `html_anki.py`, nunca estilos próprios no lote.
- **Banco de referências** `referencias/` (versionado): um Markdown por item — `questoes/`, `editais/`,
  `conteudos/`, `noticias/`, `prioridades/`, `imagens/`. `indice.tsv` e `assuntos.md` são **gerados**
  por `skills/referencias-questoes/scripts/referencias.py` (`buscar`, `mostrar`, `nova`, `indexar`,
  `validar`…); não edite-os à mão. Formato em `skills/referencias-questoes/references/formato.md`.
  Consulte o banco antes da internet e salve no banco tudo o que for pesquisado.
- **Coleção do Anki** (perfil `concursos`): lida só em cópia temporária por
  `skills/automacao-anki-python/scripts/colecao_anki.py` (`buscar`, `listar`, `dificeis`, `desempenho`,
  `lacunas`, `--colecao BACKUP.colpkg`). Nunca alterar, importar nem sincronizar a coleção; a exceção
  (`reconstruir_colpkg.py` sobre um backup enviado) está no `SKILL.md` da raiz.
- **Skills de disciplina** (`direito-*-cebraspe`, `informatica-policiais`, `portugues-cebraspe-qualidade`
  etc.) são escolhidas via `skills/perfil-carreiras-policiais/references/disciplinas.json`; Português
  tem roteamento obrigatório (`references/orquestracao_multi_skill.md`).

## Arquivos e Git

Regras completas em [`GIT_E_ARQUIVOS.md`](GIT_E_ARQUIVOS.md). Essenciais:

- `output/` (lotes em geração), PDFs/materiais de cursos, `.colpkg`/`.apkg`, `.venv/`, `uv.lock` nunca
  entram no Git. Rascunhos (texto do PDF, JSONs de importação) vão para o scratchpad.
- Commits locais autorizados ao concluir mudanças importantes, seguidos de `git push` para `origin`
  `master`; mensagens em português no imperativo; `git add` por nome. Rode `referencias.py validar`
  antes de commitar `referencias/`. Num pedido de cartões, o commit leva só `referencias/` (e
  mudanças de regras/scripts, se houver).
- Force push, `reset --hard`, `rebase`, `--amend`, troca de branch/remoto exigem autorização própria.
