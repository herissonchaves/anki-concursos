# Roteiro curto: lote de cartões a partir de PDF

Resumo operacional das regras obrigatórias para gerar um lote exportado (R, D e Cloze) de um
PDF. Ele **substitui a leitura integral** de `nucleo-pedagogico.md`, `triagem_previa_pdf.md`,
`matriz_tipos_quantidades.md`, `cobertura-pdf.md`, `protocolo_cloze_cientifico.md`,
`protocolo-modo-estrategico.md`, `avaliacao-modo-estrategico.md`, `registro-calibracao-cebraspe.md`,
`registro-revisao-recuperacao.md` e `protocolo_visual_html_anki.md` nos casos comuns: abra o
documento completo só em dúvida, caso especial (Português, imagens, coleção existente, caderno de
erros) ou ao alterar o projeto. As regras continuam valendo; este roteiro não cria exceções.

Comandos na raiz do repositório. Arquivos temporários (texto do PDF, rascunhos) vão para o
scratchpad; o lote fica em `output/<CONCURSO>_<Tema>/`.

## 0. Economia de tokens (obrigatória; não muda o que vai no cartão)

Medido na Missão 07 (Atos Administrativos): metade do gasto veio de subagentes lendo PDF como página
da web, e outra fatia grande de retrabalho. Regras:

- **PDF nunca por leitor de página da web nem por subagente de busca**: eles devolvem bytes, não
  texto. PDF local: `extrair_pdf.py`; PDF oficial do Cebraspe: `cebraspe_cdn.py` (seção 3). Página HTML
  (Planalto, STF, verbetes): navegador embutido, extraindo só o trecho com JavaScript (artigo, seção) e
  usando `browser_batch` para navegar e extrair numa chamada.
- **Ler o PDF uma vez só**, pelo `pdf.txt`, em trechos (Read com offset e limite), também no modo de
  planejamento. Nada de imprimir páginas brutas com scripts improvisados.
- **Importar as questões do jeito certo na primeira vez** (seção 3): `--ruido` com as palavras da faixa
  lateral e as páginas comentadas no `-p`.
- **Não imprimir arquivos grandes inteiros** (JSONs de registro, listas de 40 questões): só chaves,
  contagens ou a linha que interessa (`head`, `grep`, `json` com campos escolhidos).
- **Agrupar idas e voltas**: chamadas independentes em paralelo; várias correções num patch único em
  vez de uma edição por sinal do lint; consultas ao banco num só comando. Cada ida e volta reenvia o
  contexto inteiro, e o custo cresce no fim da sessão.
- **Escrever os cartões direto no `gerar_lote.py`**, em blocos por tema, sem redigir todos antes no
  raciocínio; usar `padrao_d` e `questoes_pdf` (seção 7) para não repetir metadados.
- **Banco antes da internet, e salvar o que foi lido** (inclusive doutrina, como `conteudo`), para o
  próximo lote do mesmo tema não refazer a busca.

## 1. Ler o PDF com poucos tokens

```text
uv run --no-project --with pymupdf python -I -X utf8 skills/automacao-anki-python/scripts/extrair_pdf.py PDF -o TMP/pdf.json --texto TMP/pdf.txt [--ruido PALAVRA ...]
```

Leia `pdf.txt` (limpo: sem hashes de marca-d'água, CPF, "Página | N"; `--ruido` tira palavras da
faixa lateral) em trechos. Veja como imagem só as páginas com tabela, esquema ou figura que decidem
conteúdo. Nunca copie nome/CPF da marca-d'água para arquivo versionado.

## 2. Perfil, pertinência e coleção

- Alvo padrão PRF (Inglês; sem Espanhol); PF = Agente. Usuário sem formação em Direito: termos
  técnicos explicados no verso, sem colocar isso nos cartões.
- Disciplina → especialização (`../../perfil-carreiras-policiais/references/disciplinas.json`);
  Direito e trânsito: `../../direito-cebraspe-qualidade/SKILL.md` + skill do ramo; Português:
  `../../portugues-cebraspe-qualidade/SKILL.md` (obrigatório).
- **Banco primeiro** (os comandos abaixo bastam; abra `../../referencias-questoes/SKILL.md` só em
  dúvida e `../../referencias-questoes/references/formato.md` ao salvar itens): `referencias.py buscar --tipo
  prioridade --alvo PRF -a ASSUNTO` (a triagem parte da prioridade salva e reavalia só o novo);
  `buscar --tipo edital --alvo PRF` + `mostrar ID --secao "<disciplina>"` para o item do programa (PRF
  2021 é referência histórica; na internet, só busca rápida por edital novo ou retificação);
  `buscar --tipo conteudo -a ASSUNTO --recentes 90` e `buscar --tipo noticia -a ASSUNTO`.
- Coleção viva: `uv run --no-project python -I -X utf8 skills/automacao-anki-python/scripts/colecao_anki.py
  buscar TERMO --baralho "B"` para os termos centrais (cópia somente leitura) e excluir alvos já
  cobertos (`colecao=[IDs]`). Na exportação, o `finalizar_lote.py` compara as frentes com a coleção
  e avisa as parecidas (lista em `duplicatas_colecao.txt` na pasta do lote). Trabalhando sobre um
  backup (2.36): `colecao_anki.py --colecao BACKUP.colpkg listar --tag Direito_Penal::Principios` (a tag
  casa as filhas, como no Anki) e `finalizar_lote.py ... --colecao BACKUP.colpkg`. Vários lotes no mesmo
  pedido: `detectar_duplicatas.py output --backup BACKUP.colpkg -o TMP/dups.json` compara todos entre si
  e com a coleção numa chamada.
- **PDF já coberto pela coleção** (feito antes por outro lote): gere o lote só com a `COBERTURA` (cada
  unidade e questão com `colecao=[IDs]`) e `R = D = CZ = []`; o `finalizar_lote.py` aceita o lote sem
  cards, grava a linha do histórico e avisa que não há nada a importar.

## 3. Questões: anexo, banco, internet

1. Questões do PDF: `referencias.py importar TMP/pdf.json -o TMP/rasc.json -d DISC --ruido PALAVRA1
   --ruido PALAVRA2 ...` numa passada só, sem `-p` (as palavras da faixa lateral, ex.: `DIREITO`,
   `ADMINISTRATIVO`, `REVISÃO`, `ESQUEMATIZADA`). Desde a 2.36 o importador separa os exemplos no meio da
   teoria (chave `T01`…, mesmo com numeração repetida), a lista e as comentadas (chave `Q01`…, com o
   gabarito e a página da comentada), e ignora as questões inéditas do curso, com aviso. Confira os avisos
   (gabarito da tabela × comentário; questão que já está no banco). Complete e salve num comando:
   `referencias.py completar TMP/rasc.json TMP/meta.json --mapa TMP/ids.json`, com o meta
   `{"assunto": ..., "itens": {"Q01": [subassunto, [palavras], operação], "T02": "skip"}}` (toda chave do
   rascunho precisa estar lá; `skip` para repetida ou fora do tema; a já salva é reconhecida e mapeada ao ID
   existente). O mapa `chave → ID` vai direto para o `Q` do gerador. Salve **todas** as questões novas do PDF
   (viram card se o conteúdo for Alta ou Média). Regra revogada: `vigencia: desatualizada` + `vigencia_nota`.
2. Banco: `assuntos -d DISC` → `buscar -d DISC -t TERMO [--com-url] [--vigentes] [--nao-usadas]` → `mostrar`.
3. Internet, **questões** (obrigatória para todo D, salvo **banco suficiente**: item Cebraspe C/E com
   prova oficial do mesmo subassunto já no banco, citado em `refs` com `fid='comparada'`; para R/Cloze,
   só quando o banco não tiver questão do assunto que mostre o que se cobra): Cebraspe C/E primeiro,
   depois outras bancas. Cadernos e gabaritos oficiais pelo `cebraspe_cdn.py` (pymupdf), sem abrir o
   PDF inteiro no contexto:

   ```text
   uv run --no-project --with pymupdf python -I -X utf8 skills/referencias-questoes/scripts/cebraspe_cdn.py listar PF_18 -t "definitivo|objetiva"
   ... cebraspe_cdn.py baixar PF_18/<CADERNO.PDF> PF_18/<GABARITO.PDF> -o TMP/cdn
   ... cebraspe_cdn.py buscar TMP/cdn/<CADERNO.PDF> -t "revoga|convalida|motivo"
   ... cebraspe_cdn.py gabarito TMP/cdn/<GABARITO.PDF>
   ```

   Peça permissão antes de baixar. Para achar o concurso, uma busca restrita ao domínio
   `cdn.cebraspe.org.br` pelo tema costuma dar a pasta (ex.: `PF_18`, `tc_df_23`). Salve no banco **toda
   questão que virar referência de cartão** e todo item Cebraspe C/E oficial do tema; as demais lidas
   podem ficar só em `selecao_e_fontes.txt` (banca, ano, item, URL). Sites de questões costumam bloquear
   robôs e só trazem gabarito de usuários: prefira PDFs oficiais.

## 4. Conteúdo e atualização

**Reuso do banco:** conteúdo `vigente` verificado há até 90 dias substitui a releitura, com uma
checagem rápida de alterações desde `verificado_em` (lei nova, STF, notícia no banco); registre
"conteúdo do banco <ID>, verificado em <data>; checagem em <hoje> sem novidade" e use
`F = {'chave': 'ID#Art. N'}` no gerador. Com novidade, prazo vencido ou dispositivo fora do arquivo:
pesquisa real, como abaixo, e atualização do arquivo.

Internet, **conteúdo** (obrigatória para todo cartão, R, D ou Cloze): fora do reuso, pesquisa real
na fonte; com reuso válido, só a checagem rápida acima. Direito: fonte primária vigente (Planalto, STF, STJ),
redação atual, alterações dos últimos anos e decisões de inconstitucionalidade; `radar_juridico.txt`
com status (vigente, vacatio, julgado, pendente). Tema só doutrinário (sem lei): `buscar --tipo conteudo
-a ASSUNTO` acha a doutrina já salva (`norma: "Doutrina — …"`); se faltar, leia obra aberta confiável
(ex.: Enciclopédia Jurídica da PUC-SP) e salve-a como `conteudo`. Corrija o PDF quando estiver
desatualizado e avise no verso. Cloze: pesquise mnemônicos; sem fonte confiável, crie um **autoral**. Formato e origem (só no verso, com link quando houver fonte): `references/tags.md`.

## 5. Triagem e composição

- **Cobertura por prioridade** (`cobertura-pdf.md`): inventário de todo o PDF e de todas as suas
  questões; cada unidade é **Alta**, **Média** ou **Baixa** para o concurso-alvo (com motivo). Alta e
  Média: ao menos um card, salvo nota da coleção que já exija a mesma recuperação (busque antes, em
  leitura). Baixa: sem card. Teto menor que a cobertura Alta + Média: avisar e perguntar.
- Inventário página por página (`triagem_previa_pdf.txt`): unidade, página, prioridade e motivo,
  formato e card(s) ou nota da coleção; o mesmo inventário vira o bloco `COBERTURA` do gerador.
- R: um alvo, frase curta, sem pegadinha. D: caso curto com dado decisivo, uma decisão real
  (aplicar, distinguir, exceção); definição disfarçada vira R. Cloze: uma omissão `{{c1::…}}` por
  nota (várias só em mnemônico, no formato de `references/tags.md`: título `Mnemônico SIGLA:`, letras visíveis, resto de cada termo em c1, origem só no verso), conceito/número que precisa ser lembrado; números só se
  relevantes e verificados; cada lacuna coberta por um D (`cob`).
- **50% Certo e 50% Errado em R e, separadamente, em D**; em total ímpar, diferença de 1 (não crie card só para equilibrar). Errados com um
  erro central plausível; sem absolutos como pista; ordem embaralhada pelo montador.
- Não repetir o mesmo fato nos três formatos; teto pedido conta todos os cartões.

## 6. Redação (montar com `scripts/html_anki.py`)

Verso C/E: `regra` → (`caso` em D) → `erro` (Errado) ou `certo` (confusão afastada) → `esquema`
(tabela/fluxo) quando ajudar → `m` = 💡 Memorize em 1–2 frases (no Errado, a formulação correta).
Cloze: Extra com `regra` + Memorize. Negrito só no termo-chave do verso; nada na frente que revele
o gabarito. Frente autossuficiente, sem depender do PDF. **Formatação única** (seção "Padrão único
de formatação" de `protocolo_visual_html_anki.md`): só os componentes do helper sobre o CSS de
`scripts/estilo_anki.py` (Arial 20 px); nunca mudar tamanho, fonte ou cor no lote.

## 7. Montagem, revisão e registros

- Copie `../modelos/gerar_lote_modelo.py` para `output/<CONCURSO>_<Tema>/fonte/gerar_lote.py`
  (pasta de trabalho fora do Git; Hérisson a apaga depois de importar).
  Cartões citam IDs do banco em `refs`; `referencias` pode ficar `[]`. Preencha `COBERTURA`
  (`Lote(..., cobertura=COBERTURA)`, com `p` por unidade) só com as unidades de **conteúdo**, as questões
  Baixa e as cobertas por nota da coleção; as demais questões do PDF vão em `questoes_pdf={'Q01': ('17',
  ID), ...}` e viram unidade sozinhas (cards que as citam em `refs`, prioridade herdada). O montador
  falha se Alta/Média ficar sem card nem nota da coleção, se Baixa tiver card ou se uma questão não for
  citada, e monta as tags de `references/tags.md`: `ASSUNTO::<tags do card>`
  (`Disciplina::Assunto::Topico`), `PDF` (ex.: `Missao_07`) e `Pagina_NN` só nos cards que cobrem página,
  o tipo (`Rapida`, `Desafiadora` ou `Cloze`) e, nos D, uma tag por ID de `refs` (o nome do arquivo da
  questão, ex.: `cebraspe-2021-prf-080`). Tag de concurso, `Estilo_Cebraspe`, `Revisao_PDF`, `Mnemonico` ou
  outra genérica faz o montador falhar. Questão sem prova oficial vai para `referencias_sem_prova`
  (inspiração e outra banca; nunca fidelidade comparada).
- `padrao_d=dict(rb=rub(...), orig='Caso autoral.', ...)` guarda os valores comuns dos D; sem `regra`, o D
  usa o trecho da primeira fonte de `fx`. Escreva por D só o que é dele (`alvo`, `op`, `dado`, `solucao`,
  `erro`, `conc`, `cmp`/`lim`). `sa=[subassuntos]` no D restringe o aviso de itens Cebraspe ao subtema.
- D: `fid='comparada'` só com Cebraspe C/E oficial em `refs`; senão `inspiracao_geral` + `lim`. O
  montador avisa quando um D em inspiração geral tem item Cebraspe C/E oficial do mesmo assunto no
  banco (pelo `a='disc/assunto'`, pelos `refs` ou pelos conteúdos em `fx`): leia-o e use-o antes de
  aceitar a inspiração geral.
  Sem questão de outra banca em `refs`: `obp` com as buscas. Rubrica curta: correção,
  determinação, operação, comparação e `linguagem_didatica` com evidência própria; autoria, feedback
  e utilidade só com observação. `comparacao` pode ser `PENDENTE: ...` só na inspiração geral.
- Resolva cada frente de novo antes de reler o verso e procure leitura concorrente. Registre `conc`
  em todo D; nos R e Cloze, `alt`/`rec`/`fb` só quando houver algo real (leitura concorrente
  achada, pista, confusão corrigida). Metadados não aparecem no card: escreva-os curtos. Revisão do
  próprio agente = autorevisão (declarar).
- Rode o gerador; para cada sinal pendente impresso, corrija o cartão ou justifique em
  `fonte/sinais_resolvidos.json` com motivo específico.

## 8. Relatórios, exportação e commit

- **Salvar no banco tudo o que foi pesquisado neste pedido** (obrigatório): edital/retificação →
  `edital`; fonte primária lida → `conteudo` (novo ou atualizado); alteração legal ou decisão →
  `noticia` (+ `vigencia_nota` no que ela afeta); triagem → `prioridade` (cria ou atualiza); questões
  conforme a seção 3. `nova` + `indexar`. Pesquisa feita e não salva é falha do fluxo.
- `lote/relatorios/`: o montador **gera** `triagem_previa_pdf.txt`, `auditoria_pedagogica.txt`,
  `economia_de_revisao.txt` e `fontes_e_referencias.txt` (questões com e sem prova por card, fontes e
  fidelidade dos D); o cabeçalho da triagem vem de `Lote(..., relatorio={'material': ..., 'leitura': ...,
  'alvo': ..., 'edital': ..., 'colecao': ...})`. Escreva à mão só o `selecao_e_fontes.txt` (linha
  `Banco consultado: <comandos ou IDs>` antes de qualquer fonte da internet — o `finalizar_lote.py`
  avisa se faltar —, pertinência, buscas feitas e sem resultado, "banco suficiente", mnemônicos e
  **IDs criados ou atualizados neste pedido**) e, em Direito, `radar_juridico.txt` (status das normas e
  divergências com o PDF).
- Validar em uma chamada (2.30: sem prévia, ZIP ou APKG; a entrega são os dois TSVs de `lote/`): confere
  os relatórios obrigatórios, estrutura, calibração, revisão, a cobertura do PDF e o banco
  (`referencias.py validar`), avisa duplicatas na coleção e a falta do registro do banco, grava a linha
  do lote em `referencias/historico_lotes.tsv` e imprime os caminhos dos TSVs e como importá-los:

```text
uv run --no-project python -I -X utf8 skills/automacao-anki-python/scripts/finalizar_lote.py output/<CONCURSO>_<Tema> --baralho "Nome do baralho"
```

- Commit só de `referencias/` desta tarefa (questões, documentos, `usado_em`, `historico_lotes.tsv`);
  nunca `output/`, PDFs ou dados pessoais. Entregar o caminho dos dois TSVs, o baralho e o tipo de
  nota de cada um (C/E no Básico do projeto, sem inverso; Cloze no Cloze).
