---
name: perfil-carreiras-policiais
description: "Seleciona e encaminha conteúdos Anki por disciplina para PRF e Agente da Polícia Federal, conferindo edital, utilidade e nível; PRF prioritária e Inglês como língua estrangeira."
---

# Perfil de carreiras policiais — PRF e Agente PF

## Escopo e escolha do alvo

Aplicar antes de selecionar, criar, reformular ou auditar cartões para PRF ou PF. O foco desta configuração é **Policial Rodoviário Federal e Agente de Polícia Federal**. PRF é a prioridade na ausência de alvo mais específico; pedido atual explícito prevalece. Nesta configuração, PF sem outro cargo significa **Agente**, não Delegado, Escrivão, Papiloscopista ou Perito. Outros cargos exigem programa próprio, sem reaproveitar automaticamente esta matriz. Não estender o perfil a carreiras fiscais por implicação.

A língua estrangeira configurada para PRF é **Inglês**. Não selecionar Espanhol nem criar cartões dessa língua nesta configuração. A opção histórica do edital não muda a preferência do usuário. Nova escolha explícita pode mudar a configuração, sem tratar este perfil como proibição geral.

Aproveitar cargo/edital fornecidos no contexto. Não perguntar de novo o que já está resolvido. Se o usuário disser somente “PRF e PF”, usar PRF como principal e Agente PF como secundário, avaliando a pertinência de cada alvo em ambos. Se disser “para Agente PF”, avaliar pelo programa de Agente; não impor prioridade PRF ao lote. Se só faltar um detalhe que não impeça trabalhar, declarar a hipótese e avançar.

## Edital e fontes

Ler [registro de disciplinas e cargos](references/disciplinas.json) para localizar as skills e [fontes e atualização](references/fontes-editais.md) para os documentos de referência. A matriz é um mapa editorial inicial, **não prova de que todo tema de uma disciplina consta do edital**. Abrir o programa oficial do cargo, localizar o item/subitem e conferir retificações antes de aprovar alvos. Edital histórico sustenta preparação pré-edital com essa identificação; não chamá-lo de novo edital, vigente por presunção ou previsão de futura prova. Material e edital novos substituem o recorte antigo após verificação.

Distinguir três evidências: (1) pertinência ao programa; (2) verdade do conteúdo, com atualização normativa/técnica quando aplicável; (3) questão real usada como referência de raciocínio. Uma não comprova as outras. Não inventar pesos por disciplina, recorrência, número de questões ou probabilidade de cobrança. Se calcular incidência, declarar corpus, anos, denominador e método; peso de bloco não é peso de cada disciplina.

## Seleção e encaminhamento

1. Ler o núcleo em `../gerar-revisao-anki/references/nucleo-pedagogico.md`. Preservar intenção: seleção apenas, geração, melhoria, caderno de erros, auditoria ou orientação.
2. Resolver cargo principal/secundário, edital/ano, banca e Inglês; registrar essas escolhas de forma breve no relatório, sem obrigar o usuário a preencher formulário.
3. No registro JSON, filtrar disciplinas por cargo; ler o `skill_path` **relativo a esta pasta** de cada disciplina pertinente ao material. São instruções para o agente carregar, não chamadas de API nem subagentes. Não carregar todas as disciplinas por padrão. Penal e Processo Penal são duas especializações de um cabeçalho conjunto em Agente PF.
4. Para Direito, ler também `../direito-cebraspe-qualidade/SKILL.md`; para RLM, Lógica e Estatística, ler o protocolo quantitativo indicado pela especialização. Reusar as skills já existentes de Português e Direito, sem clonar regras.
5. Por alvo, comparar regra/conceito e operação com cartões acessíveis. Classificar A (dentro do recorte e valioso para recuperar/aplicar), B (condicional, complementar ou precisa de evidência) ou C (fora do recorte, trivial, redundante ou revisão cara sem utilidade demonstrada). B sem prova de pertinência fica PENDENTE, não aprovado por conveniência.
6. Priorizar conceitos centrais, condições decisivas, distinções e lacunas demonstradas. Situação policial só entra quando melhora o raciocínio da disciplina. Não transformar toda frase do material em cartão nem exigir três formatos por tópico.
7. Aplicar a rota de trabalho solicitada: `../selecionar-conteudos-pdf-anki/SKILL.md`, `../gerar-revisao-anki/SKILL.md`, `../caderno-erros-anki/SKILL.md`, `../melhorar-cartoes-anki/SKILL.md` ou `../auditar-cartoes-anki/SKILL.md`. **Não reiniciar este perfil** quando a rota voltar a referenciá-lo: resolver perfil e especializações uma vez por tarefa, atualizando apenas se mudar cargo/conteúdo.

## Nível, formatos e transferência

R mantém um alvo central fácil e direto. D exige aplicação, inferência ou distinção com dados suficientes e verso que ensine a decisão. C memoriza um conceito importante omitindo a palavra, expressão ou frase curta central, conforme o protocolo Cloze. Não aumentar complexidade com jargão, enunciado comprido ou matérias de outro cargo. O nível “Noções” de Agente delimita profundidade, sem eliminar conteúdo expresso no programa.

Cebraspe é a referência inicial destes recortes, não uma restrição permanente do núcleo. Outro concurso/banca pedido exige verificar formato e programa e adaptar a referência sem atribuir item autoral a banca real. Manter regras do fluxo vigente; se o novo formato exigir mudar tags ou exportador, não fingir compatibilidade já implementada. Para D Cebraspe, preservar pesquisa/calibração existentes e a distinção `inspiracao_geral`.

Conhecimento transferível a outros concursos pode ser mantido com justificativa, mas não entra como obrigatório fora do cargo atual. Contabilidade para Agente PF não ativa preparação fiscal, nem suas disciplinas extras. Evitar duplicar uma mesma nota só por servir a PRF e PF; registrar dupla pertinência quando comprovada.

## Evidência de execução

No relatório de seleção ou por ID quando houver cartões: cargo(s), edital/ano e item, disciplina e skill lida, alvo/operação, evidência com URL/data, A/B/C/pendência, decisão e motivo, eventual transferência. Um vínculo de fonte pode cobrir vários IDs se a relação ficar explícita. Não acrescentar campos ou tags obrigatórios incompatíveis com os exportadores existentes. Não afirmar atualização de configuração persistente, execução de skill, teste independente ou importação no Anki sem evidência.
