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
   (o conteúdo de cada uma vira card, salvo nota da coleção). Regra revogada: `vigencia: desatualizada` + `vigencia_nota`.
2. Banco: `assuntos -d DISC` → `buscar -d DISC -t TERMO [--com-url] [--vigentes] [--nao-usadas]` → `mostrar`.
3. Internet, **questões** (2.37: obrigatória para **todo card** cujo conteúdo não tenha questão real no
   banco ou no PDF — todo card cita em `refs` ao menos uma questão que cobra o seu conteúdo; no D, salvo
   **banco suficiente**: item Cebraspe C/E com prova oficial do mesmo subassunto já no banco, citado em
   `refs` com `fid='comparada'`): Cebraspe C/E primeiro, depois outras bancas e outros cargos (o que se
   cobra em concursos diversos). Uma questão sustenta vários cards só se cobrar aquele fato ou termo.
   Sem questão depois da busca, o conceito do PDF continua ganhando R (Baixa, 2.39); registre as
   buscas no `motivo`. Anote também os tópicos que as questões do assunto cobram e o PDF não traz:
   são os candidatos a complemento (seção 4). Cadernos e gabaritos oficiais pelo `cebraspe_cdn.py` (pymupdf), sem abrir o
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

**Complementos da internet (2.39):** compare o inventário com o item do edital do mesmo assunto
(`mostrar EDITAL --secao "<disciplina>"`) e com os candidatos da seção 3. Tópico do programa, cobrado
em questão real e ausente do PDF (ou desatualizado nele de modo que muda o gabarito) entra como
unidade `X01`… (`extra`, seção 7), com a fonte lida na pesquisa de conteúdo acima e salva no banco.
Só o mesmo assunto do material; sem questão real, não entra.

## 5. Triagem e composição

- **Cobertura total** (`cobertura-pdf.md`): inventário de todo o PDF e de todas as suas questões;
  cada unidade é **Alta** (questão real do cargo/banca-alvo ou núcleo do cargo), **Média** (questão
  real de outras bancas/cargos) ou **Baixa** (sem questão localizada, com as buscas no motivo). **Toda
  unidade ganha ao menos um card** (2.39), salvo nota da coleção que já exija a mesma recuperação
  (busque antes, em leitura): Alta e Média em qualquer formato, Baixa só em R ou Cloze. Mais os complementos
  `X01`… (seção 4). Teto menor que a cobertura: avisar e perguntar.
- Inventário página por página (`triagem_previa_pdf.txt`): unidade, página, prioridade e motivo,
  formato e card(s) ou nota da coleção; o mesmo inventário vira o bloco `COBERTURA` do gerador.
- **Evidência (2.37):** R e D com questão real em `refs`. D sem questão não existe; núcleo do cargo
  sem questão localizada vira R com `nucleo='motivo'`; conceito Baixa vira R sem `refs` (2.39). Cloze
  (2.40) não exige questão: `refs` e `cobra` só quando houver.
- **Alternativas (2.38):** questão de múltipla escolha nos `refs` de um D → ao menos um card por
  alternativa (R, D ou Cloze; a correta e cada distrator). Os cards entram na paridade 50/50 de R e de D
  (um distrator pode virar um Certo com a regra correta). Sem card, só fora do programa ou sem conteúdo.
- **R (modo rápido, 2.39):** memorização, fácil de responder. Frente afirmativa de **8 a 15 palavras**
  (o lint avisa acima de 20) com um fato só; sem caso, personagem, exceção, negação ou dupla negação;
  termo técnico só se for o próprio alvo. O Errado troca **um** elemento (prazo, número, sujeito,
  consequência, termo) por uma confusão real. Lista ou enumeração longa: um R por item (ou Cloze
  mnemônico, se cobrada). D: caso curto com dado decisivo, uma
  decisão real (aplicar, distinguir, exceção), reconstruído da operação de uma questão real; definição
  disfarçada vira R.
- **Cloze (modo Cloze, 2.40):** memorização por omissão, sem exigir questão real nem D. Dois tipos
  (`protocolo_cloze_cientifico.md`): **mnemônico** de lista ou sequência (várias c1, formato de
  `references/tags.md`: título `Mnemônico SIGLA:`, letras visíveis, resto de cada termo em c1, origem só no
  verso; **sem limite de palavras**) ou **conceito-chave** do material ou do programa (uma omissão
  `{{c1::…}}` no núcleo do conceito, frase curta; o lint avisa acima de 30 palavras). Extra: regra em uma
  frase + Memorize. Com questão, `refs` + `cobra`; com D que aplica a lacuna, `cob` (opcionais). Números e
  prazos só se forem núcleo de conceito do programa e estiverem verificados.
- **50% Certo e 50% Errado em R e, separadamente, em D**; em total ímpar, diferença de 1 (não crie card só para equilibrar). Errados com um
  erro central plausível; sem absolutos como pista; ordem embaralhada pelo montador.
- Não repetir o mesmo fato nos três formatos; teto pedido conta todos os cartões.

## 6. Redação (montar com `scripts/html_anki.py`)

Verso C/E: `regra` → (`caso` em D) → `erro` (Errado) ou `certo` (confusão afastada) → `esquema`
(tabela/fluxo) quando ajudar → `m` = 💡 Memorize em 1–2 frases (no Errado, a formulação correta).
Verso do R (2.39): `regra` em uma frase (no Errado, o elemento trocado e o correto) + `m`; `erro`/`certo`
só se acrescentarem algo; esquema só como tabela curta que poupe cards (o lint avisa acima de 80
palavras).
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
  ID), ...}` e viram unidade sozinhas (cards que as citam em `refs`, prioridade herdada). Unidade Baixa:
  `cartoes=['R07']` (R com `refs=[]`) e `motivo` com as buscas. Complemento:
  `dict(u='X01', extra='edital: <item>', fx=['chave'], p='media', conteudo='…', cartoes=['R08'])`, sem `pag`.
  O montador falha se uma unidade ficar sem card nem nota da coleção, se Baixa tiver D/Cloze, se o
  complemento não tiver `fx` ou questão nos cards ou se uma questão não for citada, e monta as tags de
  `references/tags.md`: `ASSUNTO::<tags do card>`
  (`Disciplina::Assunto::Topico`), `PDF` (ex.: `Missao_07`) e `Pagina_NN` só nos cards que cobrem página,
  o tipo (`Rapida`, `Desafiadora` ou `Cloze`) e, nos D, uma tag por ID de `refs` (o nome do arquivo da
  questão, ex.: `cebraspe-2021-prf-080`). Tag de concurso, `Estilo_Cebraspe`, `Revisao_PDF`, `Mnemonico` ou
  outra genérica faz o montador falhar. Questão sem prova oficial vai para `referencias_sem_prova`
  (inspiração e outra banca; nunca fidelidade comparada).
- `padrao_d=dict(rb=rub(...), orig='Caso autoral.', ...)` guarda os valores comuns dos D; sem `regra`, o D
  usa o trecho da primeira fonte de `fx`. Escreva por D só o que é dele (`alvo`, `op`, `dado`, `solucao`,
  `erro`, `conc`, `cmp`/`lim`). `sa=[subassuntos]` no D restringe o aviso de itens Cebraspe ao subtema.
- Alternativas: cada card diz as letras que trabalha, `alts={ID: 'AC'}` (a questão também nos `refs`
  dele); dispensa em `Lote(..., alternativas_sem_card={ID: {'E': 'fora_do_programa: motivo'}})` ou
  `'sem_conteudo: motivo'`. O montador lê as letras no banco e falha com a alternativa que faltar.
- D: `refs` com questão real sempre (vira tag); `fid='comparada'` só com Cebraspe C/E oficial em
  `refs`; senão (questão de outra banca ou sem prova) `inspiracao_geral` + `lim`. O
  montador avisa quando um D em inspiração geral tem item Cebraspe C/E oficial do mesmo assunto no
  banco (pelo `a='disc/assunto'`, pelos `refs` ou pelos conteúdos em `fx`): leia-o e use-o antes de
  aceitar a inspiração geral.
  Com Cebraspe e sem questão de outra banca em `refs`: `obp` com as buscas (complemento; nunca substitui
  a questão). Rubrica curta: correção,
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
