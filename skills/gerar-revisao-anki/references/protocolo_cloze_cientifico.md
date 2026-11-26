# Cloze: escolher o alvo antes de omitir

Leia `nucleo-pedagogico.md`. Uma frase gramatical com lacuna não é, por isso, um bom cartão. Cloze é condicional, sem cota mínima. Aplicar este protocolo na geração, caderno de erros, melhoria e auditoria.


## Modo Cloze: memorização por omissão (2.40)

O Cloze serve para **memorizar conceitos e mnemônicos omitindo palavras**. Não exige questão real de concurso, `nucleo`, `cobra` nem Desafiador associado: basta que o alvo mereça memorização (portão de adequação abaixo) e pertença ao material ou ao programa do concurso-alvo. Todo Cloze novo é de um destes dois tipos; fora deles, o alvo vira R, D ou nenhum card.

1. **Mnemônico** — formato preferido para lista, sequência, requisitos ou elementos de um conceito (o que não se delega, requisitos do ato, etapas de um procedimento). Pesquise antes um mnemônico já usado (seção "Mnemônicos pesquisados"); sem fonte confiável, crie um autoral. Formato em `references/tags.md`. **Sem limite de palavras**: a frente traz a lista inteira e o Extra explica cada termo, uma linha por termo.
2. **Conceito-chave** — a lacuna é o núcleo de um conceito do material ou do programa: o termo a partir da sua definição, a propriedade distintiva, a classificação, o prazo ou número indispensável. Termo que as questões trocam ("delegar" × "avocar", "30 dias" × "60 dias") é ótimo candidato; palavra secundária da frase, nunca.

**Questão real (opcional):** quando houver questão que cobra o termo, cite-a em `refs` e diga em `cobra` como ela o cobra, por exemplo `cobra='cebraspe-2021-prf-080 troca avocação por delegação'`. Isso dá prioridade Alta ou Média à unidade e é registrado na revisão; a falta dela não bloqueia o Cloze.

**Escrita fácil:** o Cloze de conceito-chave é uma frase curta (até ~25 palavras; o lint avisa acima de 30) com uma única omissão; o contexto determina a resposta sem entregá-la. O Extra traz a regra em uma frase e termina no 💡 Memorize. O mnemônico fica fora desse limite.

## Cloze para memorizar conceitos importantes

Todo Cloze novo deve servir à memorização de um **conceito importante para o conteúdo e o concurso estudados**. Selecionar primeiro o conceito e, depois, omitir a **palavra, expressão ou frase curta importante que precisa ser lembrada**. A lacuna recupera o núcleo do conhecimento, não uma palavra secundária escolhida só para completar a frase.

Preferir definição, função, propriedade distintiva ou relação curta que permita recordar o conceito sem resolver um caso. Omitir o termo completo quando tiver várias palavras; não cortar uma expressão técnica nem impor uma palavra como tamanho máximo. Uma frase curta pode ser a resposta se expressar uma única ideia central e determinada. Manter visíveis o contexto e as condições, sem expor a resposta, iniciais reveladoras fora de um exercício mnemônico ou uma lista que permita acertar por eliminação.

**Uma omissão por nota.** Cada nota Cloze nova tem **exatamente uma** marcação `{{c1::…}}`, que oculta um único alvo de recuperação. **Mais de uma omissão só é permitida em nota de mnemônico** (as letras ou pistas do auxílio ficam visíveis e cada termo vira uma marcação c1), no formato de `references/tags.md`: frente iniciada por `Mnemônico SIGLA:`, letra(s) visível(is) colada(s) à lacuna e origem (autoral ou link) só no verso. Não há tag `Mnemonico`. Listas, pares (por exemplo, duas portas), etapas de um processo e condições complementares que não formem mnemônico viram notas separadas, uma por alvo, ou outro formato (R/D). O validador `validar_anki.py --new` reprova nota nova com várias omissões fora desse formato e qualquer "Dica autoral" na frente. Usar o Extra para explicar o termo omitido. Evitar parágrafos, justificativas inteiras e dados periféricos.

Antes de aprovar: **o que é importante memorizar? A parte omitida é precisamente esse conhecimento? O contexto determina a resposta sem entregá-la? O Extra ensina o conceito?** Se falhar, reformular, escolher outro formato ou não criar. Importância e correção exigem auditoria de conteúdo; sintaxe válida não as comprova.

## Seleção ativa de candidatos e decisão de zero Cloze

Ler este protocolo ANTES de decidir a composição do lote, inclusive quando nenhum Cloze será criado. Não restringir a busca a prazos, números e listas. Na triagem dos alvos prioritários, examinar também conceitos definidos por propriedades distintivas, classificações, relações e condições curtas cuja recuperação de memória tenha utilidade demonstrada. Não transformar todo termo técnico em candidato aprovado; não há quantidade mínima de candidatos ou Clozes.

Para cada candidato plausível encontrado, aplicar o portão abaixo e comparar o ganho de recuperação com a carga de revisão. Registrar no relatório de seleção/auditoria já existente: ID e página/fonte; alvo; resposta e equivalentes aceitos; operação exigida; referência ao cartão existente, quando houver; decisão C, R, D, não criar ou pendente, com motivo específico. Em entrega pequena inline, basta registro conciso junto à seleção; não criar arquivo adicional só para cumprir esta etapa. Se não houver candidato plausível, indicar quais alvos prioritários foram examinados e por que exigem outro formato ou não merecem memorização.

### Deduplicação por alvo, operação e direção

- Mesmo tema ou palavras semelhantes não demonstram duplicidade. Comparar o que a frente exige produzir: reconhecer a verdade de uma afirmação, recuperar um termo a partir de sua definição ou aplicar uma regra a dados.
- Um C/E que já apresenta o nome do conceito não testa necessariamente lembrar esse nome sem pista. Avaliar um Cloze definição → termo quando essa recuperação for útil; não rejeitá-lo automaticamente como duplicata.
- Um termo explicado apenas no verso/Extra não está necessariamente sendo recuperado ativamente. Inspecionar a frente e a operação, não apenas a presença da palavra na nota.
- Diferença de formato ou direção também não prova ganho suficiente. Se duas notas exigem essencialmente a mesma recuperação, preferir a melhor e rejeitar a redundante. Registrar ID/trecho e operação do cartão comparado; sem acesso ao backup, declarar deduplicação limitada ao lote.
- Quando um D do lote aplicar o conhecimento omitido, registrar o vínculo em `cob` (opcional desde a 2.40). Explicitar o ganho de recuperar a resposta e o de aplicar o conhecimento.
- Na preparação de notas novas, considerar substituir um R por Cloze mais adequado antes de acrescentar outra revisão. Escolher pelo alvo e depois recalcular composição e equilíbrio conforme `matriz_tipos_quantidades.md`; não trocar tags para contornar regras nem alterar cartões existentes por implicação.

### Quando zero Cloze é uma conclusão válida

Zero continua permitido, sem cota mínima. A conclusão precisa decorrer da avaliação concreta dos candidatos plausíveis: recuperação já coberta, baixo valor, resposta indeterminada mesmo após tentativa de reformulação, necessidade de inferência/aplicação ou verificação pendente. Distinguir ausência de alvo adequado de pendência de fonte; esta última não autoriza apresentar o lote como final verificado.

“Os números já existem no backup”, “o assunto já aparece em C/E” e “o conteúdo está nos versos” não bastam para eliminar todos os Clozes. Antes da entrega, revisar decisões globais desse tipo e conferir se conceitos, relações e condições prioritários foram considerados. Não criar lacunas só para evitar zero nem afirmar benefício de aprendizagem comprovado pela própria avaliação editorial.

Casos de decisão para revisão desta política: `avaliacao-cloze.md`.

## Portão de adequação obrigatório

Registrar no relatório por nota/vista: alvo de memória, relevância, por que a omissão ajuda, resposta/equivalentes e decisão de formato. Não inserir essa burocracia na frente.

1. O conteúdo merece memorização? Conceitos centrais, definições distintivas, classificações relevantes, listas delimitadas, sequências necessárias, fórmulas, relações, condições e prazos indispensáveis são candidatos. Ser termo técnico ou número não basta.
2. A lacuna pede conhecimento ou só uma palavra da redação? Rejeitar conectivos, pronomes, verbos genéricos e fragmentos previsíveis, salvo se a forma linguística for o próprio conteúdo estudado.
3. Exige lembrar ou resolver um caso? Narrativas com seleção de regra, ponderação de dados, cálculo ou inferência devem preferencialmente virar D/C/E aplicado ou pergunta aberta conforme o pedido. Não esconder apenas o nome da conclusão. Exemplo curto pode contextualizar um conceito quando não exige cadeia de decisão; não proibir exemplos mecanicamente.
4. A resposta é determinada? Imaginar alternativas corretas. Conceitos distintos que também completam a frase exigem reformulação ou outro formato; sinônimos legítimos devem ser aceitos.
5. Há pista que substitui a recuperação? Rejeitar resposta repetida, inicial reveladora fora de um exercício mnemônico, fragmento óbvio, expansão de sigla visível ou vazamento entre lacunas. Concordância natural isolada não reprova: avaliar se permite adivinhar sem saber o conteúdo.
6. A omissão é uma unidade útil? Ocultar o termo ou expressão completo quando essa for a unidade de memória. Não impor contagem fixa de palavras nem esconder justificativa, explicação inteira ou parágrafo.

Se falhar, REFORMULAR ou MUDAR FORMATO; descartar apenas conteúdo sem utilidade ou redundante. Omissão curta e resposta única não bastam para aprovar.

## Mnemônicos pesquisados

Ao criar Cloze, pesquisar na internet mnemônicos já usados para o conteúdo (termos como “mnemônico”, “macete” ou “decoreba” com o assunto e o concurso), em páginas de professores, cursos e materiais de estudo, e ler a página que o explica.

1. **Conferir a correção:** cada letra ou pista deve corresponder a um termo correto, completo e atual segundo a fonte primária (lei, documentação, norma). Mnemônico que omite item, inclui item errado ou reflete regra revogada é rejeitado ou corrigido e declarado como adaptação.
2. **Avaliar a utilidade:** o mnemônico deve ser curto, fácil de lembrar e levar a um alvo que mereça memorização exata (lista, sequência, elementos de um conceito). Não forçar mnemônico em conteúdo que se aprende melhor por compreensão.
3. **Usar:** em nota de mnemônico (formato de `references/tags.md`: título `Mnemônico SIGLA:`, assunto e letras visíveis, o resto de cada termo em c1) ou como dica no Extra ou no 💡 Memorize de um R/Cloze. Não copiar a explicação do curso: o Extra é redigido com palavras próprias.
4. **Registrar:** colocar a URL de onde veio o mnemônico entre as `fontes` da nota e em `mn=dict(..., origem=('encontrado'|'adaptado', url, nome))`, que gera o link no verso, e citar no relatório de seleção se ele foi usado como encontrado, adaptado ou rejeitado (com o motivo). Sem mnemônico confiável, criar um autoral (identificado como tal no verso, nunca na frente) ou não usar mnemônico; nunca atribuir a um professor ou curso um mnemônico inventado.

## Agrupamento, mnemônicos e desafiadores

- Usar uma única `{{c1::resposta}}` por nota, com uma palavra, expressão ou frase curta. Repetir c1 **somente em mnemônico** (formato de `references/tags.md`); condições complementares de uma regra, pares e listas viram notas próprias. Cada nota nova gera um cartão. Evitar colocar uma lista inteira em uma única lacuna.
- Em um mnemônico cujo alvo seja recuperar os termos, mostrar o assunto e manter as letras ou pistas que compõem o auxílio. Omitir cada termo separadamente. Exemplo de estrutura: `<b>Mnemônico PE:</b><br>P{{c1::romulgada}}<br>E{{c1::scrita}}`: a letra fica visível, colada à lacuna, e a lacuna guarda o resto do termo (nunca o termo inteiro repetindo a letra, nem a lista inteira numa lacuna só). Conferir que a pista ainda exige lembrar o termo e que a leitura após revelar a resposta fica correta.
- No Extra, explicar cada resposta, seu papel e sua relação com a pista e com o conjunto. Para mnemônicos, desenvolver o significado de cada termo e mostrar como usar a associação para lembrar o conteúdo.
- Ao preparar Cloze, pesquisar mnemônicos na internet (seção “Mnemônicos pesquisados” abaixo) antes de criar um autoral.
- O Cloze vale sozinho (2.40): não é preciso criar D para ele. Se um D do lote aplicar uma ou mais lacunas, registrar em `cob` só essas lacunas (`{'1': ['D02']}`; `{'*': [...]}` para todas). Menção no enunciado, coincidência de assunto e repetição literal não fazem um D aplicar a lacuna.
- Verificar as fontes de cada resposta. Em exportações, o vínculo por lacuna, quando houver, vai em `desafiadores_por_lacuna` (`registro-revisao-recuperacao.md`); o montador falha com lacuna inexistente ou ID que não é D do lote.

## Prazos, datas e números: filtro rigoroso para PRF e demais concursos

Transformar em Cloze os prazos, datas e números importantes que passarem em TODOS os critérios abaixo, registrados no relatório. Não converter automaticamente dados numéricos do material.

1. Relevância demonstrável: o número ou prazo está no programa do concurso-alvo e é o núcleo de um conceito do material (2.40); questão real que o cobra ou erro real do aluno reforçam, mas não são exigidos. Para PRF, não presumir que todo número de norma de trânsito é prioritário. Sem edital, declarar a limitação e usar o escopo informado; não inventar incidência ou cobrança da banca.
2. Necessidade de memória: o valor exato precisa ser necessário para distinguir regras, resolver questões ou reconhecer marco importante. Número acessório, curiosidade, estatística passageira ou dado de exemplo de cálculo não justifica Cloze. Se o alvo é calcular o resultado com dados fornecidos, usar aplicação.
3. Benefício de recuperação: a lacuna deve exigir lembrar o dado importante, com resposta determinada, sem pistas nem duplicata. Explicar qual confusão ou esquecimento se pretende evitar. Isso é justificativa editorial, não garantia de memorização ou desempenho; avaliar benefício real com uso posterior quando houver dados.
4. Precisão e verificação: conservar sujeito, hipótese, condições, exceções e unidades. Em prazos, explicitar termo inicial e modo de contagem quando necessários; em percentuais/limites, base e abrangência; em datas, evento e relevância do marco exato. Regras jurídicas exigem fonte primária atual e data de verificação. Valor não confirmado não é aprovado.
5. Carga proporcional: selecionar só dados prioritários e comparar redundância. Não converter uma tabela inteira em dezenas de cartões sem avaliar a necessidade de cada recuperação.

Se qualquer critério falhar, não criar o Cloze; registrar descarte, pendência de verificação ou formato melhor. Datas de publicação, anos de apostilas, números de artigos, estatísticas e números de exemplos não devem ser memorizados por padrão. Só passam se houver necessidade demonstrável de lembrar exatamente esses dados na preparação.

Omitir valor e unidade juntos se a unidade também for alvo ou houver risco de confusão. Manter unidade visível se ela for contexto e o alvo for apenas o valor. Intervalos podem ser recuperados como uma faixa coerente quando ambos os limites forem necessários.

Regressões editoriais: prazo normativo central com hipótese e termo inicial confirmados pode passar; data histórica só passa se o marco exato importar no programa; ano de publicação de apostila falha; velocidade inventada para exercício de cálculo falha; número de artigo sem necessidade de memória demonstrada falha; tabela de limites exige seleção item a item.

## Construção e inspeção por vista

Usar `{{c1::resposta}}` ou `{{c1::resposta::categoria útil}}`. Dica opcional não pode entregar a resposta. Frente autossuficiente, sem depender do PDF ou Extra; preservar condições, unidades e alcance.

Para notas novas, `--new` exige índice c1 e aceita mais de uma marcação somente em mnemônico no formato de `references/tags.md`, sempre contando um cartão por nota. A leitura de notas antigas conta os índices distintos. Conferir editorialmente a coerência do conjunto, a determinação das respostas, o Extra e a cobertura substantiva pelos desafiadores.

Extra obrigatório e específico para a omissão (em mnemônico, para cada termo), montado conforme `protocolo_visual_html_anki.md` e terminando no bloco `💡 Memorize` com o resumo da explicação. Conferir significado, distinção e exemplos, quando necessários, sem slogan obrigatório. Comparar redundância pelo alvo e operação.

## Coleção existente

Avaliar se as lacunas conjuntas formam um alvo coerente. Recomendar divisão quando exigirem recuperações independentes. Não apagar índices ou dividir notas existentes silenciosamente: pedir autorização para a migração quando ainda não fornecida, preservando o original e declarando limitações de histórico. Separar ADEQUADO, REFORMULAR LACUNA, MUDAR FORMATO e REDUNDANTE no relatório, com ID e motivo. Não converter todo Cloze antigo em C/E. Alterar modelo ou índices pode afetar identidade/histórico: propor migração separadamente e só executar em fluxo autorizado que a suporte e verifique. O atual revisar_colpkg.py altera apenas campos e preserva modelos/índices; não forçar migração por ele nem prometer histórico preservado. Melhorar o plugin não autoriza editar a coleção.

## Casos editoriais sintéticos de regressão

1. APROVAR: “A passagem do estado sólido diretamente ao gasoso é {{c1::sublimação}}.” Conceito delimitado e termo completo.
13. APROVAR (2.40): conceito-chave do material sem questão real localizada, com resposta determinada e Extra que o explica. Sem `refs` nem `cobra`, o Cloze sai normalmente.
14. APROVAR como conceito-chave (2.40): prazo que uma questão real troca por outro; citar a questão em `refs` e a troca em `cobra`.
15. PREFERIR MNEMÔNICO: lista ou sequência que precisa ser lembrada; antes de três notas soltas, procurar ou criar um mnemônico (sem limite de palavras).
16. REJEITAR (2.40): palavra secundária ou de ligação omitida só porque não há questão para o termo central; escolher o núcleo do conceito ou outro formato.
2. REFORMULAR: “Os três estados físicos clássicos da matéria são {{c1::sólido, líquido e gasoso}}.” Criar três notas com uma propriedade distintiva e um Extra específico para cada estado.
11. REFORMULAR: “POP3 → {{c1::110}}; IMAP → {{c1::143}}.” Par sem mnemônico: criar duas notas, uma por porta.
12. APROVAR como mnemônico: assunto visível, título `Mnemônico SIGLA:`, letras visíveis como pistas e o resto de cada termo em c1, Extra que explica cada termo e bloco 📚 Origem do mnemônico (autoral ou link).
3. REFORMULAR: “Sólido, líquido e {{c1::gasoso}} são estados físicos clássicos.” Evitar eliminação pela lista; contextualizar a propriedade distintiva do estado gasoso e explicar esse estado no Extra.
4. REJEITAR como Cloze: “As etapas são lembradas pela sigla {{c1::ABCDE}}.” Recupera o auxílio, não as etapas; delimitar e recuperar as etapas relevantes.
5. REFORMULAR: “A letra T do mnemônico significa {{c1::tempo}}.” Identificar o assunto e mostrar a relação dos termos para que a letra oriente a recuperação de um conteúdo determinado.
6. REFORMULAR: “Cobre, ferro e {{c1::alumínio}} são metais.” Muitas respostas possíveis.
7. MUDAR FORMATO: narrativa de colisão com massas e velocidades + “A velocidade final é {{c1::2 m/s}}.” Alvo é aplicar conservação/cálculo.
8. REJEITAR: “A conclusão é {{c1::que vários fatores precisam ser considerados antes de decidir}}.” Omissão genérica, extensa e indeterminada.
9. REJEITAR: “A unidade newton recebe o nome de {{c1::newton}}.” Resposta exposta.
10. NÃO FORÇAR C: lote sem alvo de memória distinto adequado; manter R/D pertinentes e zero Cloze, sem duplicar para preencher mistura.

Critérios editoriais, não prova experimental. Scripts verificam sintaxe e sinais; aprovação técnica não certifica adequação semântica nem superioridade universal de Cloze.

Regressões obrigatórias: Cloze só de mnemônico ou conceito-chave, sem exigir questão real (2.40; `refs` + `cobra` quando houver); alvos independentes em notas distintas; expressão de várias palavras permitida; múltiplas lacunas c1 só em mnemônico no formato de `references/tags.md`, sem limite de palavras; "Dica autoral" com a lista inteira numa lacuna reprovado; cada lacuna explicada no Extra; `cob` opcional, mas só com lacunas existentes e D do lote; c1/c2 reprovado em nota nova; coleção antiga contada por índices distintos.
