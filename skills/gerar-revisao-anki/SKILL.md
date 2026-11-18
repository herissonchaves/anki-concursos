---
name: gerar-revisao-anki
description: Cria cartões Anki C/E e Cloze com recuperação ativa, feedback corretivo, seleção econômica e validação de exportação, nos fluxos revisão por PDF e caderno de erros, com rápidos, desafiadores e Cloze.
---

# Geração Anki — 2.16

Leia primeiro `references/nucleo-pedagogico.md`, política comum de todos os fluxos, e não carregue todos os documentos do plugin em cada tarefa. Quando o alvo for PRF ou PF (inclusive o foco padrão PRF), aplique a seção “Perfil de carreira” do núcleo e `../perfil-carreiras-policiais/SKILL.md` uma vez por tarefa: PF significa **Agente**; PRF usa **Inglês**, sem Espanhol; outro cargo ou concurso explícito prevalece e exige programa próprio.

## Fluxo

Cartões rápidos devem ser fáceis e voltados à memorização de conceitos importantes: um alvo direto, linguagem simples, sem pegadinhas ou raciocínio complexo. Não impor teto fixo nem limitar rápidos pela quantidade de desafiadores. Aplicar a matriz para relevância, equilíbrio de gabaritos e eventual teto solicitado pelo usuário.

Cartões desafiadores devem ser didáticos, contextualizados e fáceis de entender, preservando o raciocínio de aplicação, inferência ou distinção do estilo Cebraspe. A dificuldade deve estar na decisão conceitual, não no juridiquês. Aplicar a seção de linguagem didática do protocolo estratégico e conferir clareza e raciocínio separadamente na rubrica.

Aplique `references/revisao-integral-e-linguagem.md` para os critérios de linguagem
simples, lacunas determinadas, siglas e contexto doutrinário, inclusive em geração.

Na seleção e composição, aplique “Recuperação e formatos” do núcleo. Na
segunda conferência, aplique os testes de R, D e C da seção “Feedback econômico”
e registre a evidência nos relatórios já previstos por ID.

1. Identifique pedido, material acessível, disciplina, prioridade e teto. Aproveite contexto disponível. Pergunte apenas se faltar informação que impeça a tarefa; na revisão por PDF o backup é opcional; no caderno de erros, usar prints e comparar backup quando disponível; sua ausência não impede concluir os cartões. Estatísticas são opcionais.
2. Leia fontes e selecione alvos A/B/C antes de redigir. Leia obrigatoriamente `references/protocolo_cloze_cientifico.md` nesta etapa, antes de escolher formatos, inclusive quando a conclusão puder ser zero Cloze. Para PDF, carregue `references/triagem_previa_pdf.md`; para backup, use `../analisar-colecao-anki/SKILL.md` em leitura somente. Compare operações cognitivas, não só palavras.
3. Para qualquer D (modo estratégico), faça antes a pesquisa de questões anteriores (seção própria abaixo), leia `references/protocolo-modo-estrategico.md` e a seção disciplinar de `references/atlas-multidisciplinar-cebraspe.md`; siga a rubrica de `references/avaliacao-modo-estrategico.md`. Carregue especializações somente quando aplicáveis: Português → `../portugues-cebraspe-qualidade/SKILL.md`; Direito → `references/radar-juridico-atualizacao.md` e fontes primárias atuais; imagens úteis → `references/protocolo_imagens_reais_anki.md`.
4. Leia obrigatoriamente `references/matriz_tipos_quantidades.md`; para PDF, também `references/cobertura-pdf.md`. Escolha perfil misto ou focado conforme a matriz, respeite o equilíbrio separado dos rápidos e dos desafiadores e registre exceções concretas; inclua Cloze somente quando adequado. Defina resposta e fundamento antes da frente. Em lote grande, faça piloto interno proporcional. Aplique os critérios individuais do núcleo, reformule e confira de novo cada solução/vista.
5. Entregue inline quando forem poucos cartões e não houver pedido de arquivo. Monte frentes, versos e Extras com `scripts/html_anki.py` (protocolo visual 2.15). Em lote exportado, o `fonte/gerar_lote.py` guarda só fontes, referências, esquemas e cartões e chama `scripts/montar_lote.py` (`Lote(...).gerar()`), que grava TSVs, `calibracao_cebraspe.json` (schema 2), `revisao_recuperacao.json` e a prévia; veja a convenção de chaves na docstring do módulo e o exemplo em `lotes/PRF/Missao_08_Correio_Eletronico/fonte/gerar_lote.py`. Para exportar, leia `../automacao-anki-python/SKILL.md`. TSVs UTF-8 sem BOM, sem cabeçalho, exatamente três campos: Frente/Verso/Tags ou Texto/Extra/Tags. Tags de C/E: exatamente uma entre `Tipo_Revisao_Rapida` e `Tipo_Desafiadora_Cebraspe`; D também recebe `Estilo_Cebraspe`. Cloze não recebe essas tags.
6. Em exportações com D novos, preencher `relatorios/calibracao_cebraspe.json` conforme `references/registro-calibracao-cebraspe.md` e executar `scripts/validar_calibracao_cebraspe.py` no diretório e no ZIP final. Não entregar como final com falha documental ou revisão semântica pendente. O exportador bloqueia D novos sem registro e exige linguagem_didatica aprovada com evidência específica; o resultado do script continua sem certificar a verdade do gabarito. Rode `scripts/validar_anki.py --new PACOTE.zip` com os mesmos parâmetros de perfil e teto aplicados na exportação, conforme a [matriz de quantidades](references/matriz_tipos_quantidades.md). `scripts/validar_gabaritos_rapidos.py PACOTE.zip` detalha contagens e `scripts/auditar_clareza.py PACOTE.zip` sinaliza riscos para revisão semântica. Conte também em entregas inline. Use os validadores TSV no diretório ou ZIP do lote.
7. Relate notas/cartões efetivos, fontes, principais decisões e verificações feitas. Arquivos de exportação incluem seleção/fontes, economia e auditoria por ID. Não apresentar a própria revisão como avaliação independente. A conferência semântica pelo agente deve ser declarada como tal. Não alegar importação no Anki sem realizá-la.

Para orientação de rotina, FSRS, botões de resposta ou excesso de revisões, use `../orientar-estudo-anki/SKILL.md`. Para casos de referência adicionais, consulte `references/protocolo_clareza_pedagogica.md` e `references/testes_regressao_pedagogicos.md` sob demanda.

## Formato visual, Memorize e Cloze

- **Visual:** todo cartão novo usa HTML compatível com o Anki, montado com `scripts/html_anki.py` conforme `references/protocolo_visual_html_anki.md`: blocos coloridos (📌 Regra, 🔎 No caso, ⚠️ Onde está o erro, ✔️ Por que está certo), esquemas visuais (tabela comparativa, fluxo) quando mostrarem melhor a relação, estilos inline, fundos translúcidos legíveis no modo noturno e nada de script, CSS externo ou mídia remota. O visual organiza o texto; não troca precisão por enfeite.
- **Verso:** o antigo rótulo “Correção:” foi substituído pelo bloco final obrigatório **💡 Memorize**, com o resumo da explicação do verso em uma ou duas frases. No Errado, o Memorize traz a formulação correta; no Certo, a ideia central. O mesmo vale para o Extra do Cloze. `validar_anki.py --new` reprova verso ou Extra sem o bloco final preenchido.
- **Cloze:** uma única omissão `{{c1::…}}` por nota. Mais de uma omissão somente em nota de mnemônico, com a tag `Mnemonico`; pares, listas e etapas viram notas separadas. `validar_anki.py --new` reprova o descumprimento.

## Cloze e desafiadores associados

Antes de selecionar formatos, criar, reformular ou aprovar omissões, ou justificar zero Cloze, ler `references/protocolo_cloze_cientifico.md`. Avaliar primeiro se o alvo merece Cloze; clareza da frase sozinha não basta. Conceitos e listas importantes são candidatos, sem obrigação de transformar todo conteúdo em lacuna. Registrar inadequação de formato separadamente de ambiguidade.

Em notas Cloze novas, aplicar o protocolo Cloze: usar uma única marcação `{{c1::…}}` por nota; mais de uma omissão somente em nota de mnemônico, com a tag `Mnemonico`; separar alvos independentes em notas próprias e explicar a omissão no Extra. Para mnemônicos, deixar visíveis o tema e as letras ou pistas do próprio mnemônico. Associar a cada novo Cloze desafiadores C/E do mesmo lote que cubram todas as lacunas. Preservar os índices e o histórico de notas existentes.

## Pesquisa e relevância

Sempre pesquisar na internet antes de finalizar cartões criados ou reescritos substantivamente, inclusive com material fornecido. Seguir a seção de pesquisa obrigatória do núcleo pedagógico: consultar fontes pertinentes, verificar conteúdo e registrar links/data e alvos apoiados. Sem pesquisa disponível, explicitar pendência e não apresentar lote como final verificado.

Antes de selecionar ou aprovar cartões, aplicar a seção “Relevância para PRF e outros concursos” do núcleo pedagógico. Pesquisar editais, retificações, provas e gabaritos oficiais; vincular cada alvo ao concurso/cargo e registrar evidência, utilidade esperada e decisão. Exatidão do conteúdo não basta. Busca por tema pode cobrir vários IDs com vínculo explícito; não presumir recorrência, utilidade universal ou ganho de desempenho. Evidência insuficiente fica pendente.

## Pesquisa de questões anteriores para desafiadores

Regra obrigatória para todo D. Após analisar os conteúdos e antes de escrever qualquer D, pesquisar na internet e ler os itens completos de: (1) **questões anteriores CESPE/Cebraspe Certo/Errado** desses conteúdos, primeiro e com prioridade, como modelo de forma; e (2) **questões de outras bancas** (FGV, FCC, Vunesp, Cesgranrio, IBFC, Quadrix etc.) do mesmo conteúdo, para ver o que se cobra, os detalhes decisivos e as pegadinhas. Usar as duas como inspiração para cards autorais sempre em C/E estilo Cebraspe e vincular cada D às questões consultadas. Seguir a seção “Pesquisa e comparação por família” de `references/protocolo-modo-estrategico.md` e registrar `banca` e `formato` de cada referência no `calibracao_cebraspe.json` versão 2 (`references/registro-calibracao-cebraspe.md`). Não substituir essa etapa por exemplos memorizados, atlas ou simulados de cursos.

Sem questão Cebraspe acessível para um alvo após buscas pertinentes, informar a pendência e criar o D autoral como `inspiracao_geral`. Sem questão de outra banca acessível, registrar `outras_bancas_pendencia`. Nenhuma das duas faltas impede a exportação se conteúdo, pertinência e gabarito estiverem verificados; elas não dispensam as demais verificações nem autorizam inventar fontes. R e Cloze não exigem essa pesquisa de questões, mas mantêm a pesquisa de conteúdo e de pertinência.

## Revisão de recuperação e alertas

Antes de aprovar R/C, aplicar a conferência de conteúdo e a revisão de alvo, resposta concorrente, recuperação sem pistas e feedback. Em exportações de notas novas, ler `references/registro-revisao-recuperacao.md` e preencher `relatorios/revisao_recuperacao.json` com evidências reais por R/C; D mantém sua calibração. Resolver todos os sinais atuais do lint do lote: corrigir problemas ou justificar especificamente construções legítimas, sem aprovação automática. Os exportadores bloqueiam registro ausente/incompleto, hashes divergentes e sinais pendentes, no diretório e no ZIP final. Executar também `scripts/validar_revisao_pedagogica.py DIRETORIO_OU_ZIP`; o central `validar_anki.py` continua sendo estrutural e não o substitui. Edição, corte ou reordenação exige conferir novamente e atualizar registros. Não importar helpers de testes para preencher auditoria. Poucos cartões inline recebem síntese proporcional, sem JSON/ZIP obrigatório. A barreira checa documentos, não verdade ou aprendizagem. Preservar as regras de pesquisa, pertinência e 50/50 em R/D.
