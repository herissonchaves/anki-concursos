---
name: auditar-cartoes-anki
description: Audita clareza, correção, recuperação, feedback, redundância e integridade dos cartões Anki sem confundir lint com validação pedagógica.
---

# auditar-cartoes-anki — 2.1

## Perfil policial e especializações — 2.12

Quando o alvo for PRF ou PF, inclusive o foco padrão PRF deste usuário, ler `../perfil-carreiras-policiais/SKILL.md` antes de selecionar, escrever ou aprovar conteúdo e carregar as disciplinas pertinentes indicadas em seu registro. PF tem foco em **Agente**; PRF usa **Inglês**, sem Espanhol. Resolver essa rota uma vez por tarefa; se o perfil já foi lido, aproveitar o resultado e não reiniciar o ciclo. Outro cargo/concurso explícito prevalece e exige programa próprio. Preservar o escopo do pedido (seleção, geração, melhoria ou auditoria), as regras do núcleo e os validadores existentes.

Leia `../gerar-revisao-anki/references/nucleo-pedagogico.md` primeiro.

Na auditoria de cartões novos, aplique a comparação de recuperação e os
testes de frente e feedback do núcleo. Reconfira a paridade pela
[matriz de quantidades](../gerar-revisao-anki/references/matriz_tipos_quantidades.md) e a cobertura Cloze
depois de reformulações ou descartes e use a auditoria por ID para indicar
qual candidato foi mantido e por quê.

Para coleções ou problemas de linguagem, aplique
`../gerar-revisao-anki/references/revisao-integral-e-linguagem.md`.
Registre cobertura por ID e vista; auditoria estrutural não é revisão integral.

Aplicar também `../gerar-revisao-anki/references/auditoria-conteudo-gabaritos.md`: conferir solução e fonte, não apenas o texto do verso ou declarações de aprovação. Confirme lote e abrangência. Examine cada cartão/vista quanto aos critérios do núcleo; marque APROVAR, REFORMULAR, FUNDIR ou REJEITAR com motivo e evidência. Verifique hipótese adversária em C/E; D exige regra, dado decisivo e inferência. Cloze não pode entregar resposta nem testar frase inteira sem propósito. Compare redundância entre formatos e com backup acessível. Se amostrar, declare tamanho e método, sem chamar auditoria de integral. Para Português leia `../portugues-cebraspe-qualidade/SKILL.md`; Direito exige fonte primária atual. Mídia exige protocolo visual somente quando presente. Ao verificar arquivos use `../automacao-anki-python/SKILL.md`. Relate problemas prioritários e testes executados; não gerar novos cartões ou editar coleção por implicação de uma auditoria.

## Escolha de Cloze — 2.4

Antes de criar, reformular ou aprovar omissões, ler `../gerar-revisao-anki/references/protocolo_cloze_cientifico.md`. Avaliar primeiro se o alvo merece Cloze; clareza da frase sozinha não basta. Conceitos e listas importantes são candidatos, sem obrigação de transformar todo conteúdo em lacuna. Registrar inadequação de formato separadamente de ambiguidade.

## Lacunas e desafiadores associados

Em notas Cloze novas, aplicar o protocolo Cloze: usar uma ou mais marcações `{{c1::…}}` para um alvo de recuperação coerente, separar alvos independentes e explicar cada omissão no Extra. Para mnemônicos, deixar visíveis o tema e as letras ou pistas do próprio mnemônico. Associar a cada novo Cloze desafiadores C/E do mesmo lote que cubram todas as lacunas. Preservar os índices e o histórico de notas existentes.

## Auditoria do modo estratégico — 2.7

Para D, ler `../gerar-revisao-anki/references/protocolo-modo-estrategico.md`, a seção pertinente do atlas multidisciplinar e `../gerar-revisao-anki/references/avaliacao-modo-estrategico.md`. Avaliar separadamente correção, determinação, operação, comparação, autoria, feedback e utilidade. Registrar falhas por ID; definição direta pode exigir RECLASSIFICAR R. Não tratar cenário, extensão ou tag como prova de desafio. Em conclusão com fundamento, avaliar a verdade das partes e o nexo.

Sem coleção/lote fornecido, limitar a conclusão às instruções e evidências efetivamente examinadas. Para exportação de D novos, conferir o registro de calibração; sua consistência não substitui auditoria semântica. Não fabricar registros antigos nem editar coleção por implicação.

## Avaliação de candidatos Cloze — 2.8

Ler `../gerar-revisao-anki/references/protocolo_cloze_cientifico.md` antes de avaliar a escolha de formatos, inclusive uma conclusão de zero Cloze. Conferir candidatos conceituais, relações e condições, além dos numéricos; comparar alvo, operação e direção de recuperação com as frentes existentes. Menção apenas no verso ou coincidência de tema não comprova duplicidade. Exigir motivos concretos de seleção/descarte, sem impor cotas e sem gerar ou alterar cartões fora do pedido. Usar `../gerar-revisao-anki/references/avaliacao-cloze-2.8.md` quando auditar essa política.

## Exportações novas e revisão verificável — 2.14

Ao auditar um pacote novo, ler `../gerar-revisao-anki/references/registro-revisao-recuperacao.md` e executar a barreira de revisão além dos validadores existentes. Conferir semanticamente as evidências R/C e as justificativas de alertas de todo o lote; hash e campos completos não aprovam o conteúdo. Revisão de coleção antiga continua sem exigência retroativa do JSON. Avaliação do plugin exige separar testes técnicos, piloto de saídas com fontes reais e aprendizagem não medida; não chamar autorevisão de revisão independente.
