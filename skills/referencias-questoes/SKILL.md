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
| `assuntos [-d DISC] [--completo]` | Sem opção: só as disciplinas e contagens (curto). `-d DISC`: os assuntos, subassuntos, bancas e tipos da disciplina do pedido. `--completo` (árvore inteira, ~20 KB) só ao manter o banco. |
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

1. **Banco primeiro.** `assuntos -d DISC` (só a disciplina do pedido), depois, para o tema:
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

## Regras essenciais

- Questão: **só o item oficial** (texto-base, enunciado, alternativas, gabarito e fonte); nunca
  comentários, resoluções ou resumos de cursos e sites de questões.
- Remova marcas-d'água e dados pessoais; não complete trechos ilegíveis nem invente gabarito, URL,
  data ou dispositivo (`nao_localizado`/`nao_verificado`, `## Pendências`).
- `incidencia` só com contagem de provas oficiais; sem contagem, `nao_medida`.
- Questão do banco não certifica regra vigente: o fundamento vem do `conteudo` verificado ou da
  fonte primária.

Campos de cada tipo, corpo, ids, figuras e exemplo de JSON para o `nova`:
[references/formato.md](references/formato.md) — abra só ao salvar itens.
