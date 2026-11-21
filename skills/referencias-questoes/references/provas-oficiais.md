# Provas oficiais do Cebraspe no banco

Como importar uma prova Certo/Errado inteira (caderno + gabarito definitivo do CDN do Cebraspe) para
`referencias/questoes/` e recontar as prioridades do concurso. Script:
`skills/referencias-questoes/scripts/provas_oficiais.py`; dados das provas já importadas, concursos
contados, assuntos fora do edital e rótulos: `skills/referencias-questoes/references/provas-oficiais.json`.

Rode na raiz do repositório. Comandos que leem PDF precisam do PyMuPDF:

```text
uv run --no-project --with pymupdf python -X utf8 skills/referencias-questoes/scripts/provas_oficiais.py COMANDO
```

## 1. Achar e baixar os PDFs

- A página do concurso no site do Cebraspe é dinâmica; a lista de arquivos vem da API
  `https://apis.cebraspe.org.br/cebraspe/eventos/<PASTA>` (ex.: `PRF_21`, `PF_25`), campo `arquivosGabarito`,
  com `nomeArquivo` servido em `https://cdn.cebraspe.org.br/concursos/<PASTA>/arquivos/<nomeArquivo>`.
  Concursos antigos (ex.: `DPRF_13`) têm página estática em `https://cdn.cebraspe.org.br/concursos/<PASTA>/`.
- Pegue o caderno do cargo e o **gabarito definitivo** (não o preliminar). Prova em vários cadernos (blocos,
  língua estrangeira) é uma entrada por caderno.
- Peça permissão ao usuário antes de baixar (nome, origem, tamanho) e grave só no scratchpad: PDF nunca é versionado.
- `scripts/cebraspe_cdn.py listar <PASTA> -t "definitivo|objetiva"` lista os arquivos pela API, e
  `baixar <PASTA>/<ARQUIVO> -o <scratchpad>/cdn` grava os PDFs (com pymupdf, mostra páginas e cargo).
  Nunca leia PDF por leitor de página da web: ele devolve bytes, não texto.
- Acrescente a prova em `provas` do JSON: `ano` (de aplicação), `orgao`, `pasta`, `caderno`, `url`,
  `gabarito_url`, `concurso`, `cargo`, `alvo` e `itens` (numeração do caderno, ex.: `9-120`).

## 2. Extrair e conferir

```text
provas_oficiais.py extrair CADERNO.pdf GABARITO.pdf --itens 9-120 -o ITENS.json
provas_oficiais.py revisar ITENS.json            (texto-base de cada bloco + item + gabarito)
provas_oficiais.py figuras CADERNO.pdf           (caixas de figuras por página, em pontos)
provas_oficiais.py pagina CADERNO.pdf 4 P4.png --recorte 300,300,595,842
```

`extrair` lê o caderno em duas colunas (número do item na margem, linhas seguintes com recuo), junta o
texto-base que antecede cada bloco e casa o gabarito (X = anulado). Confira sempre com `revisar` e, onde o
texto do PDF sai corrompido (fórmulas, símbolos lógicos, tabelas, código, ícones), renderize a página com
`pagina` e transcreva na spec.

## 3. Classificar (spec)

Um arquivo de texto por caderno, fora do repositório:

```text
#disc portugues
9 interpretacao | inferencia | polícia; prevenção do crime | Julga se o texto descreve mudança de paradigma.
#disc rlm
27 =existente
!enun 52 A proposição ... (~Q)↔(~R).
!ctx 45-47 Primeiro parágrafo do texto-base ¶ | tabela | em |⏎| --- | --- | ¶ Comando "julgue os itens".
!nota 43 [Figura do caderno oficial: bloco preso à mola.]
!vig 86 Lei n.º 4.898/1965 revogada pela Lei n.º 13.869/2019.
```

- `#disc` usa os ids de `skills/perfil-carreiras-policiais/references/disciplinas.json`; o assunto segue o
  **conteúdo** do item, não o bloco do caderno, e reaproveita os assuntos já existentes (`referencias.py assuntos`).
- Linha do item: `N assunto | subassuntos (vírgula) | palavras-chave (ponto e vírgula) | operação observada`.
  A operação diz o que o item cobra, em palavras próprias, sem antecipar o gabarito. Não use `|` dentro dos campos.
- `=existente`: o item já está no banco; `montar --atualizar-existentes` só passa o gabarito a definitivo.
- Correções: `!enun` troca o enunciado, `!ctx` troca o texto-base (parágrafos separados por `¶`), `!nota`
  acrescenta nota ao enunciado, `!vig` marca `vigencia: desatualizada` com o motivo (só quando a mudança é certa).
  Em todas, `⏎` é quebra de linha (tabelas Markdown e blocos de código).
- Texto-base longo (Português, Inglês) aparece completo em cada item; blocos seguintes que só citam o texto
  ("julgue ... do texto 1A18-I") recebem o texto automaticamente.

## 4. Montar, gravar e figuras

```text
provas_oficiais.py montar prf21 ITENS.json PRF21.spec -o NOVA.json --atualizar-existentes
python -X utf8 skills/referencias-questoes/scripts/referencias.py nova NOVA.json --simular
python -X utf8 skills/referencias-questoes/scripts/referencias.py nova NOVA.json
provas_oficiais.py recortar CADERNO.pdf 3 34,155,286,224 cebraspe-2021-prf-043-fig1.png
provas_oficiais.py embutir cebraspe-2021-prf-043-fig1.png ctx cebraspe-2021-prf-043 cebraspe-2021-prf-044
python -X utf8 skills/referencias-questoes/scripts/referencias.py indexar --atualizar-hash
```

- Figura comum a vários itens é um arquivo só (nome pelo primeiro item), embutido em todos. `ctx` põe a figura
  no texto-base; `enun`, depois do enunciado (itens formados por figura, ícones na frase). Confira o recorte
  renderizando antes com `pagina`.
- Mantenha ao lado da figura uma descrição curta entre colchetes (valores do gráfico, conteúdo da tela).

## 5. Prioridades

```text
provas_oficiais.py prioridades PRF              (mostra a contagem)
provas_oficiais.py prioridades PRF --gravar     (cria/regrava referencias/prioridades/prf/)
```

- Conta, por disciplina e assunto, os itens válidos de cada prova listada em `concursos` (denominador: válidos
  da disciplina na mesma prova; anulados à parte) e grava um arquivo de prioridade por assunto, com as
  evidências (IDs). Inclua a prova nova na lista do concurso antes de recontar.
- Regra: Alta = média ≥ 2 itens válidos por prova com a disciplina (ou ≥ 30% da disciplina) e presente em ≥ 2
  provas; Média = média ≥ 1, ou presente em ≥ 2 provas, ou ≥ 10%; Baixa = o resto ou assunto listado em
  `fora_do_edital` (programa vigente).
- Arquivos gerados pelo script são regravados; prioridade curada à mão (`fonte_descoberta` sem "Contagem das
  provas oficiais", ou com "(atualiza a triagem") é só atualizada: prioridade, incidência e evidências mudam,
  título e seções curadas ficam.
- Depois: `referencias.py validar` e `indexar`, e `colecao_anki.py lacunas --alvo PRF` para ver o que estudar.
