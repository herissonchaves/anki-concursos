---
name: auditar-cartoes-anki
description: Audita clareza, correção, recuperação, feedback, redundância e integridade dos cartões Anki sem confundir lint com validação pedagógica.
---

# auditar-cartoes-anki

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

## Regras comuns

- **Perfil e especializações:** quando o alvo for PRF ou PF (inclusive o foco padrão PRF), aplicar a seção “Perfil de carreira” do núcleo e `../perfil-carreiras-policiais/SKILL.md`, uma vez por tarefa, carregando só as disciplinas pertinentes. Outro cargo ou concurso explícito prevalece.
- **Cloze:** antes de criar, reformular, aprovar ou avaliar omissões (inclusive uma conclusão de zero Cloze), ler `../gerar-revisao-anki/references/protocolo_cloze_cientifico.md`. Nota nova tem uma única omissão `{{c1::…}}` (várias só em mnemônico, no formato de `skills/gerar-revisao-anki/references/tags.md`: título `Mnemônico SIGLA:`, letras visíveis, resto de cada termo em c1, origem só no verso), e cada lacuna é coberta por D do mesmo lote. Preservar índices e histórico de notas existentes.
- **Visual:** em lotes novos, conferir o HTML do protocolo `../gerar-revisao-anki/references/protocolo_visual_html_anki.md` e o bloco final 💡 Memorize (o validador `--new` reprova a falta, mas não julga o conteúdo do resumo).

## Auditoria do modo estratégico

Para D, ler `../gerar-revisao-anki/references/protocolo-modo-estrategico.md`, a seção pertinente do atlas multidisciplinar e `../gerar-revisao-anki/references/avaliacao-modo-estrategico.md`. Avaliar separadamente correção, determinação, operação, comparação, autoria, feedback e utilidade. Em D novos, conferir se houve a pesquisa de questões Cebraspe C/E e de outras bancas, com referências reais vinculadas ou pendências registradas. Registrar falhas por ID; definição direta pode exigir RECLASSIFICAR R. Não tratar cenário, extensão ou tag como prova de desafio. Em conclusão com fundamento, avaliar a verdade das partes e o nexo.

Sem coleção/lote fornecido, limitar a conclusão às instruções e evidências efetivamente examinadas. Para exportação de D novos, conferir o registro de calibração; sua consistência não substitui auditoria semântica. Não fabricar registros antigos nem editar coleção por implicação.

## Avaliação de candidatos Cloze

Ler `../gerar-revisao-anki/references/protocolo_cloze_cientifico.md` antes de avaliar a escolha de formatos, inclusive uma conclusão de zero Cloze. Conferir candidatos conceituais, relações e condições, além dos numéricos; comparar alvo, operação e direção de recuperação com as frentes existentes. Menção apenas no verso ou coincidência de tema não comprova duplicidade. Exigir motivos concretos de seleção/descarte, sem impor cotas e sem gerar ou alterar cartões fora do pedido. Usar `../gerar-revisao-anki/references/avaliacao-cloze.md` quando auditar essa política.

## Exportações novas e revisão verificável

Ao auditar um pacote novo, ler `../gerar-revisao-anki/references/registro-revisao-recuperacao.md` e executar a barreira de revisão além dos validadores existentes. Conferir semanticamente as evidências R/C e as justificativas de alertas de todo o lote; hash e campos completos não aprovam o conteúdo. Revisão de coleção antiga continua sem exigência retroativa do JSON. Avaliação do plugin exige separar testes técnicos, piloto de saídas com fontes reais e aprendizagem não medida; não chamar autorevisão de revisão independente.
