---
name: gerar-revisao-anki
description: Cria cartões Anki C/E e Cloze com recuperação ativa, feedback corretivo, seleção econômica e validação de exportação, nos fluxos revisão por PDF e caderno de erros, com rápidos, desafiadores e Cloze.
---

# Geração Anki — 2.15

## Visual em HTML, Memorize e Cloze de omissão única — 2.15

- **Visual:** todo cartão novo usa HTML compatível com o Anki, montado com `scripts/html_anki.py` conforme `references/protocolo_visual_html_anki.md`: blocos coloridos (📌 Regra, 🔎 No caso, ⚠️ Onde está o erro, ✔️ Por que está certo), esquemas visuais (tabela comparativa, fluxo) quando mostrarem melhor a relação, estilos inline, fundos translúcidos legíveis no modo noturno e nada de script, CSS externo ou mídia remota. O visual organiza o texto; não troca precisão por enfeite.
- **Verso:** o antigo rótulo “Correção:” foi substituído pelo bloco final obrigatório **💡 Memorize**, com o resumo da explicação do verso em uma ou duas frases. No Errado, o Memorize traz a formulação correta; no Certo, a ideia central. O mesmo vale para o Extra do Cloze.
- **Cloze:** uma única omissão `{{c1::…}}` por nota. Mais de uma omissão somente em nota de mnemônico, com a tag `Mnemonico`; pares, listas e etapas viram notas separadas. `validar_anki.py --new` reprova o descumprimento.

Ao criar Cloze, aplicar `references/protocolo_cloze_cientifico.md` antes da escolha dos formatos. Em notas Cloze novas, aplicar o protocolo Cloze: usar uma única marcação `{{c1::…}}` por nota; mais de uma omissão somente em nota de mnemônico, com a tag `Mnemonico`; separar alvos independentes em notas próprias e explicar a omissão no Extra. Para mnemônicos, deixar visíveis o tema e as letras ou pistas do próprio mnemônico. Associar a cada novo Cloze desafiadores C/E do mesmo lote que cubram todas as lacunas. Preservar os índices e o histórico de notas existentes.

## Perfil policial e especializações — 2.12

Quando o alvo for PRF ou PF, inclusive o foco padrão PRF deste usuário, ler `../perfil-carreiras-policiais/SKILL.md` antes de selecionar, escrever ou aprovar conteúdo e carregar as disciplinas pertinentes indicadas em seu registro. PF tem foco em **Agente**; PRF usa **Inglês**, sem Espanhol. Resolver essa rota uma vez por tarefa; se o perfil já foi lido, aproveitar o resultado e não reiniciar o ciclo. Outro cargo/concurso explícito prevalece e exige programa próprio. Preservar o escopo do pedido (seleção, geração, melhoria ou auditoria), as regras do núcleo e os validadores existentes.

Cartões rápidos devem ser fáceis e voltados à memorização de conceitos importantes: um alvo direto, linguagem simples, sem pegadinhas ou raciocínio complexo. Não impor teto fixo nem limitar rápidos pela quantidade de desafiadores. Aplicar a matriz para relevância, equilíbrio de gabaritos e eventual teto solicitado pelo usuário.

Cartões desafiadores devem ser didáticos, contextualizados e fáceis de entender, preservando o raciocínio de aplicação, inferência ou distinção do estilo Cebraspe. A dificuldade deve estar na decisão conceitual, não no juridiquês. Aplicar a seção de linguagem didática do protocolo estratégico e conferir clareza e raciocínio separadamente na rubrica.

Leia primeiro `references/nucleo-pedagogico.md`, política comum de todos os fluxos. Não carregar todos os documentos do plugin para cada tarefa.

Aplique `references/revisao-integral-e-linguagem.md` para os critérios de linguagem
simples, lacunas determinadas, siglas e contexto doutrinário, inclusive em geração.

Na seleção e composição, aplique “Recuperação e formatos” do núcleo. Na
segunda conferência, aplique os testes de R, D e C da seção “Feedback econômico”
e registre a evidência nos relatórios já previstos por ID.

1. Identifique pedido, material acessível, disciplina, prioridade e teto. Aproveite contexto disponível. Pergunte apenas se faltar informação que impeça a tarefa; na revisão por PDF o backup é opcional; no caderno de erros, usar prints e comparar backup quando disponível; sua ausência não impede concluir os cartões. Estatísticas são opcionais.
2. Leia fontes e selecione alvos A/B/C antes de redigir. Leia obrigatoriamente `references/protocolo_cloze_cientifico.md` nesta etapa, antes de escolher formatos, inclusive quando a conclusão puder ser zero Cloze. Para PDF, carregue `references/triagem_previa_pdf.md`; para backup, use `../analisar-colecao-anki/SKILL.md` em leitura somente. Compare operações cognitivas, não só palavras.
3. Para qualquer D (modo estratégico), leia `references/protocolo-modo-estrategico.md` e a seção disciplinar de `references/atlas-multidisciplinar-cebraspe.md`; siga a rubrica de `references/avaliacao-modo-estrategico.md`. Carregue especializações somente quando aplicáveis: Português → `../portugues-cebraspe-qualidade/SKILL.md`; Direito → `references/radar-juridico-atualizacao.md` e fontes primárias atuais; imagens úteis → `references/protocolo_imagens_reais_anki.md`.
4. Leia obrigatoriamente `references/matriz_tipos_quantidades.md`; para PDF, também `references/cobertura-pdf.md`. Escolha perfil misto ou focado conforme a matriz, respeite o equilíbrio separado dos rápidos e dos desafiadores e registre exceções concretas; inclua Cloze somente quando adequado. Defina resposta e fundamento antes da frente. Em lote grande, faça piloto interno proporcional. Aplique os critérios individuais do núcleo, reformule e confira de novo cada solução/vista.
5. Entregue inline quando forem poucos cartões e não houver pedido de arquivo. Monte frentes, versos e Extras com `scripts/html_anki.py` (protocolo visual 2.15). Para exportar, leia `../automacao-anki-python/SKILL.md`. TSVs UTF-8 sem BOM, sem cabeçalho, exatamente três campos: Frente/Verso/Tags ou Texto/Extra/Tags. Tags de C/E: exatamente uma entre `Tipo_Revisao_Rapida` e `Tipo_Desafiadora_Cebraspe`; D também recebe `Estilo_Cebraspe`. Cloze não recebe essas tags.
6. Em exportações com D novos, preencher `relatorios/calibracao_cebraspe.json` conforme `references/registro-calibracao-cebraspe.md` e executar `scripts/validar_calibracao_cebraspe.py` no diretório e no ZIP final. Não entregar como final com falha documental ou revisão semântica pendente. O exportador bloqueia D novos sem registro e exige linguagem_didatica aprovada com evidência específica; o resultado do script continua sem certificar a verdade do gabarito. Rode `scripts/validar_anki.py --new PACOTE.zip` com os mesmos parâmetros de perfil e teto aplicados na exportação, conforme a [matriz de quantidades](references/matriz_tipos_quantidades.md). `scripts/validar_gabaritos_rapidos.py PACOTE.zip` detalha contagens e `scripts/auditar_clareza.py PACOTE.zip` sinaliza riscos para revisão semântica. Conte também em entregas inline. Use os validadores TSV no diretório ou ZIP do lote.
7. Relate notas/cartões efetivos, fontes, principais decisões e verificações feitas. Arquivos de exportação incluem seleção/fontes, economia e auditoria por ID. Não apresentar a própria revisão como avaliação independente. A conferência semântica pelo agente deve ser declarada como tal. Não alegar importação no Anki sem realizá-la.

Para orientação de rotina, FSRS, botões de resposta ou excesso de revisões, use `../orientar-estudo-anki/SKILL.md`. Para casos de referência adicionais, consulte `references/protocolo_clareza_pedagogica.md` e `references/testes_regressao_pedagogicos.md` sob demanda.

## Escolha de Cloze — 2.4

Antes de selecionar formatos, criar, reformular ou aprovar omissões, ou justificar zero Cloze, ler `references/protocolo_cloze_cientifico.md`. Avaliar primeiro se o alvo merece Cloze; clareza da frase sozinha não basta. Conceitos e listas importantes são candidatos, sem obrigação de transformar todo conteúdo em lacuna. Registrar inadequação de formato separadamente de ambiguidade.

## Pesquisa obrigatória — 2.4.1

Sempre pesquisar na internet antes de finalizar cartões criados ou reescritos substantivamente, inclusive com material fornecido. Seguir a seção de pesquisa obrigatória do núcleo pedagógico: consultar fontes pertinentes, verificar conteúdo e registrar links/data e alvos apoiados. Sem pesquisa disponível, explicitar pendência e não apresentar lote como final verificado.

## Relevância para o concurso — 2.4.2

Antes de selecionar ou aprovar cartões, aplicar a seção “Relevância para PRF e outros concursos” do núcleo pedagógico. Pesquisar editais, retificações, provas e gabaritos oficiais; vincular cada alvo ao concurso/cargo e registrar evidência, utilidade esperada e decisão. Exatidão do conteúdo não basta. Busca por tema pode cobrir vários IDs com vínculo explícito; não presumir recorrência, utilidade universal ou ganho de desempenho. Evidência insuficiente fica pendente.

## Lacunas e desafiadores associados

Em notas Cloze novas, aplicar o protocolo Cloze: usar uma única marcação `{{c1::…}}` por nota; mais de uma omissão somente em nota de mnemônico, com a tag `Mnemonico`; separar alvos independentes em notas próprias e explicar a omissão no Extra. Para mnemônicos, deixar visíveis o tema e as letras ou pistas do próprio mnemônico. Associar a cada novo Cloze desafiadores C/E do mesmo lote que cubram todas as lacunas. Preservar os índices e o histórico de notas existentes.

## Pesquisa de questões reais e cobertura autoral — 2.9.3

Após analisar os conteúdos e antes de escrever qualquer D, pesquisar na internet questões anteriores CESPE/Cebraspe C/E desses conteúdos, ler os itens completos e utilizá-los como inspiração e referências para criação autoral. Seguir a seção de pesquisa de `references/protocolo-modo-estrategico.md`, vinculando os cartões às questões consultadas. Não substituir essa etapa por exemplos memorizados, apenas consulta ao atlas, questões de outras bancas ou simulados de cursos. Sem referência acessível para um alvo após buscas pertinentes e tentativa de fontes alternativas, informar a pendência de referência e criar D autorais para cobrir esse conteúdo, identificados no relatório como `inspiracao_geral`, sem comparação específica verificada. A falta de questão acessível não impede aprovação ou exportação se conteúdo, pertinência e gabarito estiverem verificados; ela não dispensa as demais verificações nem autoriza inventar fontes. Preservar pesquisa de conteúdo, clareza, originalidade e demais verificações existentes.

## Revisão de recuperação e alertas — 2.14

Antes de aprovar R/C, aplicar a conferência de conteúdo e a revisão de alvo, resposta concorrente, recuperação sem pistas e feedback. Em exportações de notas novas, ler `references/registro-revisao-recuperacao.md` e preencher `relatorios/revisao_recuperacao.json` com evidências reais por R/C; D mantém sua calibração. Resolver todos os sinais atuais do lint do lote: corrigir problemas ou justificar especificamente construções legítimas, sem aprovação automática. Os exportadores bloqueiam registro ausente/incompleto, hashes divergentes e sinais pendentes, no diretório e no ZIP final. Executar também `scripts/validar_revisao_pedagogica.py DIRETORIO_OU_ZIP`; o central `validar_anki.py` continua sendo estrutural e não o substitui. Edição, corte ou reordenação exige conferir novamente e atualizar registros. Não importar helpers de testes para preencher auditoria. Poucos cartões inline recebem síntese proporcional, sem JSON/ZIP obrigatório. A barreira checa documentos, não verdade ou aprendizagem. Preservar as regras de pesquisa, pertinência e 50/50 em R/D.
