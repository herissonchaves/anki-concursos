---
name: selecionar-conteudos-pdf-anki
description: Seleciona conteúdos de PDF úteis para memorização e aplicação em concursos, com triagem A/B/C e estimativa de cartões, sem gerar quando não solicitado.
---

# selecionar-conteudos-pdf-anki

Leia `../gerar-revisao-anki/references/nucleo-pedagogico.md` primeiro.

Leia páginas realmente acessíveis e registre limites de OCR. Classifique alvo, página, prioridade A/B/C, operação, possível duplicidade e custo. Não prometer incidência sem evidência. Escolha R/D/C pelo alvo, não por proporções. Compare com backup acessível somente em leitura. Para Português leia `../portugues-cebraspe-qualidade/SKILL.md`. Não converter teoria incompreendida ou conteúdo periférico automaticamente. Liste também as questões de concursos que o PDF contiver (página, banca, ano, assunto), extraídas com `referencias.py importar`; salve no banco `referencias/` todas elas conforme `../referencias-questoes/SKILL.md` (`origem: anexo_usuario`) e indique as do banco já existentes para os alvos selecionados. Entregue seleção e estimativa de cartões efetivos; só prossiga à geração se o pedido a incluir. A seleção apenas prioriza: se o pedido for de cards de revisão do PDF, a geração cobre todo o conteúdo do PDF e de suas questões (`../gerar-revisao-anki/references/cobertura-pdf.md`), e a estimativa deve contar ao menos um card por unidade.

## Regras comuns

- **Perfil e especializações:** quando o alvo for PRF ou PF (inclusive o foco padrão PRF), aplicar a seção “Perfil de carreira” do núcleo e `../perfil-carreiras-policiais/SKILL.md`, uma vez por tarefa, carregando só as disciplinas pertinentes. Outro cargo ou concurso explícito prevalece.

## Relevância para o concurso

Na triagem, aplique a comparação de alvos da seção “Recuperação e formatos”
do núcleo e use o registro existente para justificar a seleção e os descartes.

Antes de selecionar ou aprovar cartões, aplicar a seção “Relevância para PRF e outros concursos” do núcleo pedagógico. Pesquisar editais, retificações, provas e gabaritos oficiais; vincular cada alvo ao concurso/cargo e registrar evidência, utilidade esperada e decisão. Exatidão do conteúdo não basta. Busca por tema pode cobrir vários IDs com vínculo explícito; não presumir recorrência, utilidade universal ou ganho de desempenho. Evidência insuficiente fica pendente.

## Avaliação de candidatos Cloze

Ler `../gerar-revisao-anki/references/protocolo_cloze_cientifico.md` antes de avaliar a escolha de formatos, inclusive uma conclusão de zero Cloze. Conferir candidatos conceituais, relações e condições, além dos numéricos; comparar alvo, operação e direção de recuperação com as frentes existentes. Menção apenas no verso ou coincidência de tema não comprova duplicidade. Exigir motivos concretos de seleção/descarte, sem impor cotas e sem gerar ou alterar cartões fora do pedido. Usar `../gerar-revisao-anki/references/avaliacao-cloze.md` quando auditar essa política.
