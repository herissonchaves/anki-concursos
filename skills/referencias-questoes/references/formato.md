# Formato dos itens do banco de referências

Abra ao salvar ou atualizar itens com `referencias.py nova` (comandos e fluxo em `../SKILL.md`).

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

Questão: `disciplina` é id de `../../perfil-carreiras-policiais/references/disciplinas.json`;
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

## Conteúdo doutrinário

Para temas sem lei (atributos, classificação e espécies do ato, por exemplo), a doutrina lida também vira
`conteudo`, para o reuso de 90 dias valer como vale para a lei:

- `norma: "Doutrina — Autor, obra ou verbete, publicação"`; `dispositivos`: os tópicos cobertos (ex.:
  `["presunção de legitimidade", "tipicidade"]`); `situacao: vigente` (posição atual da doutrina).
- Corpo em **paráfrase com palavras próprias**, nunca cópia: doutrina tem direito autoral (ao contrário
  da lei). Seções `## Escopo e método` (o que foi lido, e se a fonte é secundária), `## <tópico>` e
  `## Alterações conhecidas`. Registre divergências doutrinárias quando houver.
- Fonte secundária (resumo de curso, artigo) só quando a obra original não estiver acessível, dito no
  escopo. Prefira obras abertas confiáveis (ex.: Enciclopédia Jurídica da PUC-SP).
- No gerador, use `F = {'chave': 'ID#Tópico'}` como para lei.

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
