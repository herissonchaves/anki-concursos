---
name: referencias-questoes
description: Banco de questões de concursos de referência em referencias/ (Markdown com frontmatter padronizado, índice e busca por script). Use em toda criação de cartões autorais para reaproveitar questões do arquivo enviado e do banco, salvar as questões lidas na internet e vincular as referências da calibração.
---

# Banco de questões de referência

`referencias/` (na raiz do repositório) guarda as questões de concursos já usadas como
referência ou inspiração, uma por arquivo, em
`referencias/questoes/<disciplina>/<assunto>/<id>.md`. O índice `indice.tsv` e a árvore
`assuntos.md` são gerados pelo script e servem para achar questões **sem abrir os
arquivos**. Abra o texto só das questões escolhidas, com `mostrar`.

Script (rode na raiz; `-X utf8` evita erro de acentuação no Windows):

```text
python -X utf8 skills/referencias-questoes/scripts/referencias.py COMANDO
```

| Comando | Uso |
| --- | --- |
| `assuntos` | Árvore disciplina > assunto com contagens. Leia primeiro: é curta. |
| `buscar -d DISC -a ASSUNTO -t TERMO [-t TERMO] [-b BANCA] [-f certo_errado] [--alvo PRF] [--nao-usadas] [--corpo] [-n 20]` | Uma linha por questão. `-t` procura em id, assunto, subassuntos, palavras-chave, órgão e cargo, sem acento; `--corpo` procura também no enunciado. |
| `mostrar ID [ID…] [--analise] [--meta]` | Enunciado, alternativas e gabarito. |
| `nova ARQ.json` (ou `-`) | Cria uma ou várias questões a partir de JSON; gera id e hash e recusa duplicatas, informando o id existente. `--simular` só valida. |
| `usar ID… --lote PRF/Missao_NN_Tema --cartoes D01,D02` | Registra o uso no lote (substitui o registro anterior do mesmo lote). |
| `calibracao ID…` | JSON das referências no formato do `calibracao_cebraspe.json` v2. |
| `validar` / `indexar [--atualizar-hash]` | Confere o banco / regera índice e árvore. |

`buscar` e `assuntos` regeneram o índice sozinhos quando um arquivo muda.

## Quando usar (todo cartão autoral: R, D, Cloze e caderno de erros)

1. **Arquivo enviado pelo usuário.** Antes de redigir, procure questões de concursos no
   PDF, apostila, lista ou prints (seções “questões”, “exercícios”, “gabarito”). Salve
   cada questão pertinente com `nova` e `origem: anexo_usuario` (`caderno_erros` para
   prints do caderno de erros), indicando em `fonte_descoberta` o arquivo e a página.
   Procure a prova oficial para preencher `url` e confirmar o gabarito; se não achar,
   use `nao_localizado` e `gabarito_status: nao_verificado`.
2. **Banco.** Rode `assuntos` e depois `buscar` pela disciplina, assunto e termos dos
   alvos; leia com `mostrar` só as pertinentes. Questões do banco servem de inspiração e
   de referência de forma, como as da internet; prefira as `--nao-usadas` quando houver
   escolha, para variar o repertório.
3. **Internet.** A pesquisa de questões anteriores continua obrigatória para todo D
   (Cebraspe C/E primeiro, depois outras bancas), conforme
   `../gerar-revisao-anki/references/protocolo-modo-estrategico.md`. Toda questão lida
   por inteiro e pertinente vai para o banco com `nova` e `origem: pesquisa_internet`,
   mesmo que acabe não vinculada a um cartão. Para R e Cloze, a pesquisa na internet
   de questões é opcional; a de conteúdo continua obrigatória.
4. **Vínculo.** No `gerar_lote.py`, passe os IDs do banco em `referencias` do
   `Lote(...)`; o `montar_lote.py` monta as referências da calibração e registra o uso
   (`usado_em`) ao gerar. Em entregas inline, cite os IDs na síntese de fontes.
5. **Antes do commit:** `indexar` sem erros. Versione os `.md`, `indice.tsv` e
   `assuntos.md` junto com o lote.

## Formato do arquivo

Frontmatter obrigatório e completo (o script recusa campo vazio ou fora do padrão):

| Campo | Valor |
| --- | --- |
| `id` | Gerado: `banca-ano-orgao-item` (sufixo de hash em colisão); igual ao nome do arquivo |
| `tipo` | `questao` |
| `banca`, `orgao`, `concurso`, `cargo` | Como na prova; `cargo` pode ser `nao_localizado` |
| `formato` | `certo_errado` ou `multipla_escolha` |
| `ano` | Inteiro (ano do edital/prova) |
| `caderno`, `item` | Identificação na prova; `nao_localizado` se não houver |
| `disciplina` | id de `../perfil-carreiras-policiais/references/disciplinas.json` (`informatica`, `portugues`…); outra disciplina em snake_case gera aviso |
| `assunto`, `subassuntos` | snake_case sem acento; reaproveite os nomes que `assuntos` já mostra |
| `palavras_chave` | Lista em minúsculas: termos que alguém usaria para achar a questão |
| `gabarito` | `C`/`E`/`anulada` (C/E) ou `A`–`E`/`anulada` (múltipla escolha) |
| `gabarito_status` | `definitivo`, `justificativa_oficial`, `nao_verificado` ou `anulado` |
| `url`, `gabarito_url` | Prova e gabarito oficiais; `gabarito_url` obrigatório se o status for definitivo ou justificativa oficial |
| `origem` | `anexo_usuario`, `pesquisa_internet` ou `caderno_erros` |
| `fonte_descoberta` | Onde a questão foi encontrada (arquivo e página, ou site de busca) |
| `consulta` | AAAA-MM-DD |
| `concursos_alvo` | Concursos para os quais é pertinente (`PRF`, `PF_AGENTE`…) |
| `operacao_observada` | O que a questão exige (operação, dado decisivo, pegadinha), em uma frase |
| `usado_em` | `LOTE#CARTOES`, preenchido por `usar`/`montar_lote.py` |
| `hash` | Gerado a partir do enunciado e das alternativas (deduplicação) |

Corpo: `## Enunciado` (texto-base em citação `>` antes, quando houver),
`## Alternativas` (múltipla escolha), `## Gabarito` e, opcional, `## Análise` em
palavras próprias.

Exemplo de entrada para `nova` (JSON; pode ser uma lista):

```json
{"banca": "Cebraspe", "formato": "certo_errado", "ano": 2024, "orgao": "MPTO",
 "concurso": "MPTO — Edital nº 1/2024", "cargo": "Técnico Ministerial", "caderno": "952_MP_TO_016_01",
 "item": "99", "disciplina": "informatica", "assunto": "correio_eletronico",
 "subassuntos": ["protocolos"], "palavras_chave": ["smtp", "pop3"], "gabarito": "E",
 "gabarito_status": "definitivo", "url": "https://…", "gabarito_url": "https://…",
 "origem": "pesquisa_internet", "fonte_descoberta": "Caderno oficial no site da banca",
 "consulta": "2026-11-20", "concursos_alvo": ["PRF"],
 "operacao_observada": "Troca as funções de SMTP e POP3.",
 "enunciado": "Texto integral do item.", "analise": "Opcional."}
```

## Regras de conteúdo

- Salve **só o item oficial**: texto-base, enunciado, alternativas, gabarito e fonte.
  Nunca copie comentários, resoluções ou resumos de cursos e de sites de questões; a
  análise, quando houver, é escrita com palavras próprias.
- Remova marcas-d'água e dados pessoais (nome, CPF, e-mail) do texto copiado de PDFs; o
  `validar` recusa CPF, e-mail e “licenciado para”.
- Transcreva o item fielmente; não complete trechos ilegíveis nem invente gabarito, URL,
  cargo ou caderno: use `nao_localizado` e `nao_verificado`.
- Simulados autorais de cursos não são questões de banca e não entram no banco.
- Questão do banco não dispensa ler a fonte de conteúdo atual: prova antiga não
  certifica regra vigente.
