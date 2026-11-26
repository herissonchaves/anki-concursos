> Política comum: [nucleo-pedagogico.md](nucleo-pedagogico.md). Distribuição, equilíbrio e exceções: [matriz_tipos_quantidades.md](matriz_tipos_quantidades.md). Este documento complementa essas regras.

# Triagem obrigatória antes da escrita — PDF

Nenhuma nota de revisão derivada de PDF nasce antes do inventário e seleção de alvos. Aplicar `../SKILL.md`, `matriz_tipos_quantidades.md`, `filtro-economia-revisao.md`, `cobertura-pdf.md` e `protocolo_cloze_cientifico.md`.

## Portões por unidade de conteúdo

- **Fonte real:** trecho/página de fato lido, conteúdo correto, figuras/tabelas verificadas quando necessárias.
- **Valor:** importância para prova e estrutura conceitual, sem inventar frequência de banca.
- **Alvo autônomo:** regra, definição, termo, condição, exceção ou efeito recuperável sem recorrer a PDF/chat.
- **Distinção:** resposta unívoca; rápido não exige interpretação concorrente, desafiador exige inferência real; Cloze exige recuperação produtiva não entregue pelas pistas.
- **Economia:** redundância com a coleção viva (`colecao_anki.py buscar`; `.colpkg` só fora deste PC), outras modalidades e revisões futuras. Contar índices Cloze como cartões, não notas.
- **Teto:** pedido explícito é máximo TOTAL de CARTÕES; sem pedido estimar `N_ideal` fundamentado.

Classificar a prioridade para o concurso-alvo (`cobertura-pdf.md`): **Alta**, **Média** ou **Baixa** (substitui A/B/C), com motivo. Toda unidade ganha ao menos um card, salvo nota da coleção que já exija a mesma recuperação; Baixa só em R ou Cloze (2.39/2.40). Complementos da internet do mesmo assunto, cobrados em questão real e ausentes do PDF, entram como unidades `X01`…. Toda questão de concurso do PDF também entra no inventário. Antes de escrever, preencher `relatorios/triagem_previa_pdf.txt`: ID, página real, prioridade e motivo, operação, formato, card(s) ou nota da coleção.

Use os campos de alvo, valor e decisão para aplicar a comparação de recuperação
do núcleo. Registre o candidato mantido quando houver duplicidade e o tópico
que ficou descoberto quando a composição do lote impedir uma inclusão útil.

## Escolha pelo alvo cognitivo

| Alvo | Modalidade | Rejeição |
| --- | --- | --- |
| Conceito nuclear para julgar rapidamente | C/E rápido | trivial, ambíguo, repetido |
| Exceção, condição, consequência ou integração de fatos | C/E desafiador | apenas jogo de palavras, sem raciocínio real |
| Conceito importante cujo termo, expressão ou frase curta central precisa ser memorizado | Cloze em qualquer posição; uma única lacuna c1 por nota (várias só em mnemônico, no formato de `references/tags.md`: título `Mnemônico SIGLA:`, letras visíveis, resto de cada termo em c1, origem só no verso), sem exigir questão real nem D (2.40); dados numéricos só após filtro específico | palavra secundária, adivinhação contextual, frase vaga, redundância ou alto custo |

## Relevância para o concurso

Antes de selecionar ou aprovar cartões, aplicar a seção “Relevância para PRF e outros concursos” do núcleo pedagógico. Pesquisar editais, retificações, provas e gabaritos oficiais; vincular cada alvo ao concurso/cargo e registrar evidência, utilidade esperada e decisão. Exatidão do conteúdo não basta. Busca por tema pode cobrir vários IDs com vínculo explícito; não presumir recorrência, utilidade universal ou ganho de desempenho. Evidência insuficiente fica pendente.

## Candidatos Cloze antes de concluir a triagem

Aplicar a seleção ativa e a deduplicação por operação de `protocolo_cloze_cientifico.md`. Examinar conceitos, relações e condições prioritários além de números. Incorporar ao registro de triagem a resposta/equivalentes, operação comparada e motivo da decisão para cada candidato plausível. Se concluir zero Cloze, sustentar essa conclusão com os alvos efetivamente examinados; presença do assunto em versos ou em C/E não prova cobertura da recuperação produtiva.
