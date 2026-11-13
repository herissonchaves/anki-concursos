---
name: matematica-cebraspe-qualidade
description: "Protocolo especializado para selecionar, criar, melhorar e auditar cartões Anki de Matemática, Raciocínio Lógico-Matemático, Estatística e interpretação quantitativa para concursos, especialmente PRF/Cebraspe. Usar nos modos rápido, desafiador C/E e Cloze, em PDFs, cadernos de erros e coleções."
---

# Matemática para Anki e PRF — protocolo especializado 1.0

## Quando e como ativar

Usar obrigatoriamente quando o conteúdo matemático envolver aritmética, porcentagem, razão, proporção, funções, equações, PA/PG, análise de gráficos/tabelas, matemática financeira, geometria, probabilidade, combinatória, estatística ou lógica matemática quantitativa. Inclui pedidos de criar, selecionar, corrigir, melhorar ou auditar cartões dessas disciplinas, com ou sem a palavra "Matemática". Se o pedido misturar disciplinas, usar esta especialização somente nos alvos matemáticos. Não confundir Matemática com Física: um problema de Física aplica suas próprias condições e requer tratamento físico adicional.

Esta skill complementa, e NÃO substitui, as políticas gerais: `../gerar-revisao-anki/references/nucleo-pedagogico.md`, `matriz_tipos_quantidades.md`, `protocolo_cloze_cientifico.md`, `protocolo-modo-estrategico.md`, `atlas-multidisciplinar-cebraspe.md`, `avaliacao-modo-estrategico.md`; e os fluxos da skill principal (PDF/caderno de erros/backup/exportação). Preservar as tags e validações existentes. Nenhuma proporção fixa R/D/C nasce desta especialização. Novos lotes C/E devem manter EXATAMENTE 50% Certo e 50% Errado SEPARADAMENTE em R e D conforme a matriz, sem fabricar afirmações falsas para fechar paridade. A criação de um único C/E novo segue as regras de incompatibilidade e esclarecimento previstas na matriz; a reformulação de cartão existente preserva a identidade.

## Objetivo de aprendizagem

Um cartão matemático é bom quando recupera uma regra, uma condição de aplicabilidade, um **procedimento transferível** ou um erro conceitual provável. Não transformar cada conta, passagem algébrica ou questão integral em cartão; o Anki reforça a recuperação entre sessões, enquanto exercícios inéditos e simulados verificam transferência. Acertar C/E por palpite ou reconhecimento do texto não comprova que se sabe resolver. Antes de revelar o verso, recuperar mentalmente o *porquê* e os passos-chave; se houve chute, avaliar como não dominado.

## Seleção e pertinência

1. Delimitar cargo, banca, edital/ano, assunto e fonte. Para PRF, consultar o último edital oficial disponível e provas/gabaritos, distinguindo referência histórica de edital futuro. Não inventar conteúdo do próximo edital nem frequência de cobrança. Buscar questões C/E reais da CESPE/Cebraspe **antes** de gerar D, abrir e ler itens completos (incluindo gráfico/texto-base) e registrar a família cognitiva observada e a referência oficial. Caso nenhuma referência específica seja encontrada após tentativas pertinentes, registrar `inspiracao_geral` e não alegar equivalência comprovada; permanece obrigatória a verificação da matemática e pertinência ao concurso.
2. Triar alvos A/B/C. A: conhecimento central, esquecimento/erro real ou procedimento reutilizável; B: importante sob certas condições do programa ou quando reaparece; C: detalhe periférico, procedimento mecânico trivial ou exercício longo melhor para lista. Não inferir dificuldade pessoal sem dados do aluno. Sem backup, deduplicar dentro do material acessível e dizer isso.
3. Identificar o **erro-alvo**: base percentual errada, hipótese oculta, domínio, sinal, unidade, escala de gráfico, amostra, evento complementar, ordem de operações, quantificador, taxa composta ou interpretação da conclusão. Não criar dezenas de variantes numéricas do mesmo erro. Criar R e D do mesmo tema somente quando testar operações cognitivas distintas.

## Escolher o formato pelo alvo

- **Rápido (R):** um conceito, propriedade ou condição essencial, simples e sem contas extensas. Ex.: distinguir aumento percentual de ponto percentual ou reconhecer quando se aplica uma fórmula. Linguagem direta, sem pegadinha artificial. Pode haver mais rápidos que desafiadores quando o material justificar.
- **Cloze (C):** priorizar fórmulas curtas, termos, relações e condições indispensáveis. Preferir recuperar quando aplicar a relação junto do símbolo. Em notas Cloze novas, aplicar o protocolo Cloze: usar uma ou mais marcações `{{c1::…}}` para um alvo de recuperação coerente, separar alvos independentes e explicar cada omissão no Extra. Para mnemônicos, deixar visíveis o tema e as letras ou pistas do próprio mnemônico. Associar a cada novo Cloze desafiadores C/E do mesmo lote que cubram todas as lacunas. Preservar os índices e o histórico de notas existentes.
- **Desafiador (D):** julgar uma conclusão C/E aplicando um dado decisivo, comparando modelos ou identificando inferência incorreta; não basta reconhecer a fórmula. D deve exigir escolher o método, interpretar dados, verificar restrição ou inferir consequência. Preferir cálculo mental/rascunho curto, com **30–90 s como referência editorial experimental, não limite rígido**. Aumentar duração somente se o ganho cognitivo justificar; se exigir algoritmo repetitivo, muitas etapas ou leitura extensa, simplificar para um princípio específico ou deixar a questão na lista/simulado. Um bom D pode ser inteiramente conceitual.

## Construção dos D: seis famílias úteis (não são cotas)

1. **Percentuais e taxas compostas:** identificar base de comparação, fatores multiplicativos, taxas sucessivas e variação líquida; evitar o falso cancelamento +x% seguido de −x%.
2. **Equações/funções e condições:** domínio, soluções extraviadas por operações, parâmetros, sinal, raízes, monotonicidade, interpretação de máximo/mínimo; premissas completas.
3. **Gráficos, tabelas e dados acumulados:** conferir escalas, diferenças entre acumulado e incremento, intervalos, tendência versus valor exato, comparação relativa e leitura de eixos.
4. **Probabilidade/combinatória/estatística:** universo/amostragem, independência, exclusividade, contagem sem duplicação, média ponderada, mediana, dispersão, proporção versus número absoluto.
5. **Sequências, proporcionalidade e modelagem:** taxa por unidade, sequências, crescimento linear/exponencial, alteração de variável relevante, proporcionalidade direta/inversa sob condições.
6. **Raciocínio lógico matemático:** implicação, contrapositiva, recíproca, quantificadores, conjuntos e contraexemplos, sem adicionar hipóteses de mundo real que não constam das premissas.

Antes de escrever, preparar internamente por ID: (a) regra/condição; (b) dado decisivo; (c) operação mental; (d) erro plausível; (e) gabarito e solução resolvida; (f) referência de pertinência e da operação Cebraspe (ou ausência declarada). Criar redação e dados autorais; trocar só números ou personagens da questão da banca não basta. Frente autossuficiente, com unidades e hipóteses relevantes; sem mencionar "PDF/anexo"; no máximo uma conclusão nuclear. Contexto somente se necessário à decisão, sem historinha ornamental ou pista óbvia.

## Verificação matemática antes da aprovação

Resolver novamente usando apenas a frente, ANTES de consultar o verso escrito. Conferir:

- Operações e sinais, arredondamentos, conversões e unidades; simplificação de frações, expoentes, porcentagens, bases diferentes.
- Domínio e hipóteses (denominadores não nulos, radicandos, base de logaritmo, divisibilidade, limites, taxas e intervalos; soluções espúrias após quadratura).
- Dados suficientes e unicidade da conclusão; testar casos-limite e contraexemplo quando a proposição generaliza.
- Gráficos: legendas, escalas, eixos, intervalos, marcações e legibilidade da imagem. Se depender de imagem, fornecer uma imagem legítima, legível e autossuficiente quando o protocolo de mídia permitir; caso contrário, transformar em texto com dados suficientes.
- Em estatística/probabilidade: denominador da amostra, espaço amostral, hipóteses de independência e distinção entre taxa e contagem.
- Sempre que relevante, conferir por segundo caminho: substituição, estimativa, teste numérico ou ferramenta determinística disponível (calculadora/código). Nunca alegar uma verificação por ferramenta não executada. Ferramentas numéricas não demonstram correção de hipótese, lógica ou pertinência.

Para **Errado**, dar correção inequívoca e demonstrar a falha central; para **Certo**, evidenciar que a conclusão segue das premissas. Se gabarito/hipótese persistir ambíguo, REFORMULAR ou REJEITAR — não aprovar para cumprir paridade. Recontar gabaritos após cortes.

## Verso e custo de revisão

Formato preferido em D: `✅ Certo` ou `❌ Errado` + regra curta → substituição/cálculo mínimo → conclusão e, no Errado, correção da afirmação. Mostrar passos suficientes para o estudante reconstruir o método, mas sem resolução longa desnecessária. Valorizar unidades e observação "qual foi a armadilha?" quando acrescentar compreensão. Aceitar solução equivalente; não obrigar método único. Não colocar gabarito da prova original sem conferir origem. Revisão muito lenta ou falhas repetidas sinalizam pré-requisito não aprendido, cartão ambíguo ou excesso de passos: explicar antes de memorizar, dividir apenas *alvos distintos* e manter exercícios longos fora do Anki.

## Auditoria e teste de transferência

Para cada cartão aprovado: exatidão, determinação, operação mental real, pertinência ao concurso, autoria, explicação, custo de revisão, redundância funcional, recuperação sem pistas. D marcado como desafio mas que apenas peça definição deve ser RECLASSIFICADO R ou refeito. Sem material real não inventar resultado de benchmark. Testar cartões de lotes pequenos e registrar decisões; estimar tempo real após uso, não de modo fictício. Orientar o aluno a resolver questões **inéditas**, inclusive com números/representações diferentes, e comparar desempenho ao longo de semanas; retenção no Anki não equivale automaticamente a acerto na prova.

Para revisão de coleção existente, preservar IDs/histórico quando possível; não modificar coleção nem agendamento sem autorização. Para exportação, seguir rigorosamente os validadores e o formato da skill geral. O código de validação estrutural NÃO verifica provas matemáticas nem garante qualidade pedagógica.

Leia `references/casos-regressao-matematica.md` quando estiver fazendo uma avaliação da própria especialização ou corrigindo falhas recorrentes; não converter esses casos de teste automaticamente em cartões da coleção.
