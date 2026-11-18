---
name: direito-cebraspe-qualidade
description: "Protocolo transversal obrigatório para selecionar, criar, melhorar e auditar cartões Anki de Direito para concursos PRF e Agente PF/Cebraspe. Aciona as especializações Constitucional, Administrativo, Penal, Processual Penal, Direitos Humanos, legislação especial e trânsito; aplica fontes oficiais, vigência, casos práticos e linguagem didática."
---

# Direito no Anki — protocolo transversal 1.0

## Ativação e hierarquia

Aplicar quando o conteúdo for jurídico, mesmo que o pedido só mencione o tema (crime, prisão, poder de polícia, licitação, mandado de segurança, CTB, direitos humanos, lei de drogas etc.). Aplica-se a **seleção de PDF, geração, explicação, melhoria, caderno de erros e auditoria**. Em mistos, aplicar apenas aos alvos jurídicos. Classificar o ramo e **ler também a skill específica** indicada em `references/roteamento-juridico.md`. Caso caiba em duas, aplicar ambas sem duplicar cartões; se não encaixar, seguir esta skill e protocolo geral. Não tratar a mera menção de um termo jurídico num problema de Português como pedido para decorar o Direito.

**Ordem de autoridade:** solicitação atual → `../gerar-revisao-anki/references/nucleo-pedagogico.md` → `matriz_tipos_quantidades.md` → esta skill e ramo → `../gerar-revisao-anki/references/radar-juridico-atualizacao.md` → protocolos de C/E, Cloze e validação. Não criar regras novas de quantidade. Preservar equidade exata **50% Certo e 50% Errado separadamente** em lotes novos de R e D, conforme matriz; não falsear leis para fechar paridade. Cloze fora da contagem. Reformulações de cartões existentes não exigem alterar seu gabarito para reequilibrar um lote antigo.

## Perfil pedagógico

O estudante não tem formação inicial em Direito; isso orienta a explicação, não reduz a exigência de prova. Manter o termo técnico exigível e **explicá-lo em palavras comuns no verso**. Evitar juridiquês desnecessário, latinismos não explicados, frases artificiais e linguagem infantilizada. O cartão precisa ser compreensível isoladamente, sem depender de PDF ou de outro cartão. Não colocar no cartão o perfil pessoal do estudante.

## Dupla triagem antes de escrever

1. **Pertinência de concurso:** identificar cargo, edital/ano e programa. Priorizar PRF se for o alvo conhecido, mas não presumir que um novo edital já cobre o mesmo tema. Verificar edital, retificações, provas e gabaritos oficiais; classificar A (relevante e de recuperação útil), B (condicional) ou C (fora de foco, trivial ou redundante), com justificativa. Não inventar recorrência.
2. **Correção temporal da regra:** abrir legislação oficial consolidada (Planalto, Congresso/Senado, diário oficial), conferir artigo, redação, exceções, vigência e eventuais transições; para jurisprudência ler tese/acórdão oficial do STF/STJ, verificar status, ratio, abrangência, modulação e possíveis divergências. Aplicar `../gerar-revisao-anki/references/radar-juridico-atualizacao.md`. Lei nova promulgada pode não estar em vigor; proposta/PL não é lei; afetação de recurso não é julgamento definitivo. O que uma prova antiga cobrava não substitui direito vigente. Se não houver verificação suficiente, **marcar PENDENTE e não aprovar como validado**.
3. **Comparação Cebraspe para D:** ler questões **reais** CESPE/Cebraspe no formato C/E dos temas, com enunciado completo e gabarito definitivo quando acessível, antes da redação; registrar concurso, ano, item, operação de raciocínio, URL e data. A questão inspira a **operação cognitiva**, não o texto. Se não houver fonte de forma encontrada após busca, indicar `inspiracao_geral` conforme protocolo sem inventar equivalência.

## Formatos orientados à recuperação

- **R, rápido:** memorizar um conceito jurídico central, condição ou distinção direta. Fácil e curto, sem pegadinha nem caso longo. O verso explica brevemente por que a assertiva está certa/errada; nunca produzir R só para decorar número periférico.
- **D, desafiador:** um *caso novo curto e resolúvel*, contendo fato decisivo que permita aplicar regra, distinguir instituto, identificar requisito/exceção ou decidir consequência. Raciocínio verdadeiro, não definição adornada. Regra → fato → consequência deve ser recuperável sem consultar material; cenário pode ser mínimo. **Não confundir dois regimes jurídicos** nem omitir elemento que decide a tipificação/atribuição. Caso com mais de uma resposta plausível: reformular ou rejeitar.
- **C, Cloze:** priorizar termos, condições, consequências e prazos úteis. Em notas Cloze novas, aplicar o protocolo Cloze: usar uma única marcação `{{c1::…}}` por nota; mais de uma omissão somente em nota de mnemônico, com a tag `Mnemonico`; separar alvos independentes em notas próprias e explicar a omissão no Extra. Para mnemônicos, deixar visíveis o tema e as letras ou pistas do próprio mnemônico. Associar a cada novo Cloze desafiadores C/E do mesmo lote que cubram todas as lacunas. Preservar os índices e o histórico de notas existentes. Nunca ocultar o próprio artigo como substituto de compreender a regra.

## Procedimento do cartão D

Para cada ID registrar: (1) alvo jurídico; (2) fonte vigente/dispositivo e marco temporal; (3) fato decisivo e condições; (4) pergunta de julgamento; (5) raciocínio esperado; (6) confusão plausível; (7) fonte formal Cebraspe ou `inspiracao_geral`; (8) verificação da resposta. **No verso**, iniciar com gabarito, explicar regra em linguagem simples, associar a regra ao fato e corrigir a inferência errada, quando houver. Evitar citar artigo sem explicar seu efeito. Conferir contraexemplo, exceção e todas as partes de conclusões compostas. Se a regra depender de corrente doutrinária, indicar corrente adotada ou criar caso incontroverso; não inventar consenso.

## Controle de qualidade e carga

- Política geral exige auditoria **individual** de exatidão, determinação, operação D, autoria, linguagem, feedback, utilidade, fonte e data. Scripts de tags/TSV não verificam conteúdo jurídico.
- Não gerar 3 cartões para cada parágrafo nem repetir a mesma norma nos três formatos por padrão. Selecionar operação distinta ou fundir. Se a mesma dificuldade persistir, explicar o fundamento primeiro e reformular a nota existente quando mantiver seu alvo/ID; não apagar histórico sem autorização.
- Separar **acerto por recuperação do fundamento** de acerto por palpite. Recomendar questões inéditas como teste de transferência, sem alegar ganho de aprovação garantido.
- No relatório por ID usar `ramo`, `regra/fonte/data`, `fato decisivo`, `operação`, `gabarito/justificativa`, `comparação de forma`, `prioridade/decisão`. Não fabricar pesquisa, benchmark, alteração da coleção ou resultados de teste.

Leia `references/roteamento-juridico.md` para seleção disciplinar e `references/casos-regressao-juridicos.md` ao validar ou revisar o próprio módulo. As skills jurídicas **não substituem** as demais (Português, Matemática) em conteúdo misto.
