---
name: referencias-questoes
description: Banco de referências em referencias/ (Markdown com frontmatter padronizado, índice único e busca por script) com cinco tipos — questões de concursos, editais dos concursos-alvo, conteúdos verificados (texto normativo), notícias (alterações legais, decisões, mudanças de edital) e prioridades por concurso (o que mais cai, Alta/Média/Baixa). Use em toda criação de cartões para reaproveitar o que já foi lido e verificado, e para salvar tudo o que for pesquisado.
---

# Banco de referências

`referencias/` (na raiz do repositório) guarda, um item por arquivo Markdown, o que já foi
lido e verificado para os cartões. O índice `indice.tsv` (coluna `tipo`) e a árvore
`assuntos.md` são gerados pelo script e servem para achar itens **sem abrir os arquivos**.
Abra só os escolhidos, com `mostrar` (e `--secao` nos longos).

| tipo | pasta | para quê |
| --- | --- | --- |
| `questao` | `questoes/<disc>/<assunto>/` | item oficial de prova (forma, calibração, `refs`) |
| `edital` | `editais/<concurso>/` | programa do cargo por disciplina, etapas, retificações |
| `conteudo` | `conteudos/<disc>/<assunto>/` | texto normativo verificado por dispositivo (substitui a releitura por até 90 dias) |
| `noticia` | `noticias/<disc>/<assunto>/` | lei nova, decisão judicial, mudança de edital, com o `efeito` na prova |
| `prioridade` | `prioridades/<concurso>/<disc>/` | prioridade do assunto para o concurso, subtemas Alta/Média/Baixa, o que mais cai (contado) |

`disciplina` e `assunto` usam os mesmos nomes em todos os tipos (ex.: `transito/motorista_profissional`),
para uma busca cruzar questão, conteúdo, notícia e prioridade do mesmo tema. Edital usa `disciplina: geral`.

Script (rode na raiz; `-X utf8` evita erro de acentuação no Windows):

```text
python -X utf8 skills/referencias-questoes/scripts/referencias.py COMANDO
```

| Comando | Uso |
| --- | --- |
| `assuntos` | Árvore disciplina > assunto com contagens e tipos. Leia primeiro: é curta. |
| `buscar [--tipo T] -d DISC -a ASSUNTO -t TERMO [-b BANCA] [-f certo_errado] [--alvo PRF] [--nao-usadas] [--com-url] [--vigentes] [--recentes N] [--corpo] [-n 20]` | Uma linha por item. Questões: `sem prova`, `DESATUALIZADA`. Documentos: tipo, título, status/situação/prioridade e data. `--recentes N`: conteúdos verificados (e demais documentos consultados) há até N dias. |
| `mostrar ID [ID…] [--secao NOME] [--analise] [--meta]` | Corpo do item; `--secao` imprime só a seção `## NOME…` (ex.: a disciplina do edital, um artigo do conteúdo). |
| `fonte ID[#SEÇÃO]` | `(url, trecho)` de um conteúdo/notícia/edital para o `F = {...}` do `gerar_lote.py`. |
| `importar ARQ.pdf\|.json\|.txt -o TMP.json [-p 17-19] [-d DISC] [-a ASSUNTO] [--ruido PALAVRA]` | Rascunho JSON das questões do arquivo, sem marcas-d'água; campos de julgamento como `REVISAR` (o `nova` recusa). |
| `nova ARQ.json` (ou `-`) | Cria itens (questão ou, com `tipo`, documento); gera id e hash e recusa duplicatas. `--simular` só valida. |
| `usar ID… --lote PRF_Tema --cartoes D01,D02` | Registra o uso no lote (substitui o registro anterior do mesmo lote). |
| `calibracao ID…` | JSON das referências (só questões) no formato do `calibracao_cebraspe.json` v2. |
| `validar` / `indexar [--atualizar-hash]` | Confere o banco / regera índice e árvore. |

Prova oficial inteira do Cebraspe (caderno + gabarito definitivo do CDN), figuras recortadas e recontagem
das prioridades do concurso: `scripts/provas_oficiais.py` (`extrair`, `revisar`, `montar`, `recortar`,
`embutir`, `prioridades`), com o passo a passo e o formato da spec em
[provas-oficiais.md](references/provas-oficiais.md).

`buscar` e `assuntos` regeneram o índice sozinhos quando um arquivo muda.

## Fluxo em todo pedido de cartões (R, D, Cloze e caderno de erros)

1. **Banco primeiro.** `assuntos`, depois, para o tema do pedido:
   - `buscar --tipo prioridade --alvo PRF -a ASSUNTO`: a triagem começa pela prioridade salva
     e reavalia só o que for novo;
   - `buscar --tipo edital --alvo PRF` e `mostrar ID --secao "<disciplina>"`: pertinência
     pelo programa salvo; na internet, só uma busca rápida por edital novo ou retificação;
   - `buscar --tipo conteudo -a ASSUNTO --recentes 90` e `buscar --tipo noticia -a ASSUNTO`;
   - `buscar -a ASSUNTO -t TERMO` para questões (prefira `--nao-usadas` quando houver escolha).
2. **Reuso de conteúdo verificado (até 90 dias).** Conteúdo com `situacao: vigente` e
   `verificado_em` há até 90 dias substitui a releitura da fonte, com uma **checagem
   rápida**: uma busca por alteração da norma desde aquela data (lei nova, decisão do STF,
   notícia no banco). Sem novidade, registre em `selecao_e_fontes.txt`: "conteúdo do banco
   <ID>, verificado em <data>; checagem de alterações em <hoje> sem novidade". Com novidade,
   prazo vencido ou dispositivo que o arquivo não cobre: releia a fonte primária e atualize
   o arquivo (`verificado_em`, seções). Use `fonte ID#Art. N` no `F` do gerador.
3. **Arquivo enviado pelo usuário.** Extraia as questões com `importar` (prints do caderno
   de erros: transcreva), revise os campos `REVISAR` e salve **todas** com `nova`
   (`origem: anexo_usuario`; `caderno_erros` para prints). Na revisão de PDF, questão de
   conteúdo Alta ou Média precisa de card que a cite em `refs`
   (`../gerar-revisao-anki/references/cobertura-pdf.md`).
4. **Internet.** A pesquisa de questões anteriores continua obrigatória para todo D
   (Cebraspe C/E primeiro), conforme `../gerar-revisao-anki/references/protocolo-modo-estrategico.md`;
   a de conteúdo, salvo o reuso do passo 2.
5. **Salvar tudo o que foi pesquisado (obrigatório).** Ao final de todo pedido em que a IA
   pesquisou informação nova, ela salva o resultado no banco com `nova` (ou atualiza o arquivo
   existente) e roda `indexar`:
   - edital ou retificação → `edital` (programa por disciplina);
   - leitura de fonte primária (lei, decreto, resolução, súmula) → `conteudo`;
   - alteração legal, decisão judicial, mudança de edital → `noticia` (com `efeito`), e o
     `conteudo`/as questões afetados ganham `vigencia_nota`/`vigencia: desatualizada`;
   - triagem Alta/Média/Baixa do pedido → `prioridade` (cria ou atualiza);
   - questões: obrigatório salvar (a) toda questão citada em `refs` e (b) todo item Cebraspe
     C/E oficial do tema com caderno e gabarito localizados; as demais podem ficar só citadas
     em `selecao_e_fontes.txt`.
   Liste em `selecao_e_fontes.txt` os IDs criados ou atualizados. Pesquisa feita e não salva
   é falha do fluxo.
6. **Vínculo.** No `gerar_lote.py`, IDs de questões nos `refs` de cada cartão; IDs de
   conteúdo (`"ID#Seção"`) como valores de `F`. O `montar_lote.py` monta as referências da
   calibração (questões com prova; sem prova em `referencias_sem_prova`), converte os
   conteúdos em `(url, trecho)` e registra o uso (`usado_em`) de todos ao gerar.
7. **Antes do commit:** `validar` e `indexar` sem erros; versione os `.md`, `indice.tsv` e
   `assuntos.md` junto com o lote.

## Prioridade e "o que mais cai"

- `prioridade` (alta/media/baixa) vale para o assunto no concurso; o corpo traz os subtemas
  Alta, Média e Baixa com motivo, pegadinhas recorrentes e a data da avaliação.
- `incidencia` só com evidência contada: provas oficiais (e questões do banco), com anos,
  cargos, denominador e método; itens anulados à parte. Análise de curso entra só como fonte
  secundária identificada. Sem contagem: `incidencia: nao_medida` — nunca estimar.
- `evidencias`: IDs do banco (questões, editais) que sustentam a avaliação.

## Formato

Campos comuns a todos os tipos: `id` (gerado, igual ao nome do arquivo), `tipo`,
`disciplina`, `assunto`, `subassuntos`, `palavras_chave` (minúsculas), `concursos_alvo`,
`url`, `fonte_descoberta`, `consulta` (AAAA-MM-DD), `usado_em` (`LOTE#CARTOES`, preenchido
pelo script), `hash`, e os opcionais `vigencia`/`vigencia_nota`.

| tipo | campos próprios | corpo |
| --- | --- | --- |
| `questao` | `banca, formato, ano, orgao, concurso, cargo, caderno, item, gabarito, gabarito_status, gabarito_url, origem, operacao_observada` | `## Enunciado` (texto-base em `>` antes), `## Alternativas`, `## Gabarito`, `## Análise` opcional |
| `edital` | `titulo, orgao, banca, cargo, ano, edicao, status` (`vigente`/`historico`/`previsto`), `retificacoes` | `## Dados gerais` + `## <Disciplina>` com o programa literal |
| `conteudo` | `titulo, norma, dispositivos, situacao` (`vigente`/`alterado`/`revogado`), `verificado_em` | `## Escopo e método`, `## Art. N — tema` (paráfrase fiel; literal entre aspas), `## Alterações conhecidas` |
| `noticia` | `titulo, data_evento, status` (`confirmada`/`pendente`), `efeito`, `normas_afetadas` | `## Resumo` (palavras próprias), `## Efeito na prova`, `## Fontes`/`## Pendências` |
| `prioridade` | `titulo, concurso, prioridade, incidencia, evidencias` | `## Avaliação`, `## Alta`, `## Média`, `## Baixa`, `## Pegadinhas recorrentes`, `## Incidência…` |

Questão: `disciplina` é id de `../perfil-carreiras-policiais/references/disciplinas.json`;
`gabarito` `C`/`E`/`anulada` ou `A`–`E`; `gabarito_status` `definitivo`, `justificativa_oficial`,
`nao_verificado` ou `anulado` (`gabarito_url` obrigatório nos dois primeiros); `origem`
`anexo_usuario`, `pesquisa_internet` ou `caderno_erros`; id `banca-ano-orgao-item`; hash do
enunciado e das alternativas. Documento: id `tipo-<7 palavras do título>`; hash do título + url.

Entrada para `nova` (JSON; pode ser uma lista). Questão: os campos acima + `enunciado`
(e `alternativas`, `analise`). Documento: `tipo`, os campos acima e `corpo` (Markdown com
seções `## `), por exemplo:

```json
{"tipo": "conteudo", "titulo": "CTB — condução por motoristas profissionais (arts. 67-A a 67-E)",
 "disciplina": "transito", "assunto": "motorista_profissional", "subassuntos": ["tempo_de_direcao"],
 "palavras_chave": ["ctb", "5 h 30"], "concursos_alvo": ["PRF"],
 "url": "https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm",
 "fonte_descoberta": "Texto compilado do Planalto", "consulta": "2026-11-21",
 "norma": "CTB, arts. 67-A a 67-E", "dispositivos": ["art. 67-C"], "situacao": "vigente",
 "verificado_em": "2026-11-21", "corpo": "## Art. 67-C — tempo de direção\n\n- Caput: ..."}
```

## Regras de conteúdo

- Questão: **só o item oficial** (texto-base, enunciado, alternativas, gabarito e fonte).
  Nunca copie comentários, resoluções ou resumos de cursos e de sites de questões; a análise
  é escrita com palavras próprias. Simulados autorais de cursos não entram.
- Lei, decreto e decisão judicial são de domínio público (texto literal permitido); edital
  pode ser transcrito no trecho do programa; notícia é resumo com palavras próprias e link.
- Questão com figura (gráfico, foto, tela de programa, ícone, desenho): recorte a figura do caderno
  oficial em PNG (tons de cinza, cerca de 130 dpi), salve em `referencias/imagens/<id-da-questão>-figN.png`
  e embuta no estilo Obsidian, `![[<id-da-questão>-figN.png]]`, no ponto em que ela aparece: no texto-base
  (linha `> ![[...]]`) ou depois do enunciado. Figura comum a vários itens é um arquivo só, citado em
  todos. Ao lado, uma descrição curta entre colchetes (valores de gráfico, conteúdo da tela) para a busca
  por texto. O `validar` recusa imagem citada que não exista em `imagens/`.
- Remova marcas-d'água e dados pessoais (nome, CPF, e-mail); o `validar` recusa CPF, e-mail
  e “licenciado para”.
- Não complete trechos ilegíveis nem invente gabarito, URL, data ou dispositivo: use
  `nao_localizado`/`nao_verificado` nas questões e `## Pendências` nos documentos; o que não
  foi conferido palavra a palavra é marcado como tal no texto.
- Questão do banco não certifica regra vigente: o fundamento do gabarito vem do `conteudo`
  verificado (≤ 90 dias, com a checagem rápida) ou da fonte primária.
