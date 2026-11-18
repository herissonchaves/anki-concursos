---
name: melhorar-cartoes-anki
description: Explica e reformula cartões Anki difíceis de entender, ambíguos, redundantes ou caros de revisar, preservando o alvo e o histórico quando possível.
---

# melhorar-cartoes-anki

Leia `../gerar-revisao-anki/references/nucleo-pedagogico.md` primeiro.

Leia também `../gerar-revisao-anki/references/revisao-integral-e-linguagem.md`.
Quando a melhoria for solicitada, execute as reescritas necessárias em cópia e
conclua o escopo; não encerre apenas com sugestões. Preserve cartões adequados.

Diagnostique o problema antes de reescrever: compreensão, contexto, pista, ambiguidade, inferência artificial, feedback ou redundância. Explique a regra se o usuário não a compreendeu. Defina um alvo e resposta correta; entregue versão revisada e motivo breve. Para Português leia `../portugues-cebraspe-qualidade/SKILL.md`; Direito exige fonte primária atual. Cloze usa `../gerar-revisao-anki/references/protocolo_cloze_cientifico.md`; imagens somente com protocolo visual. Confira de novo a solução após editar. Sugira editar a nota existente quando conservar o mesmo alvo; gerar novo APKG não garante preservar histórico se a frente mudar. Não remova índices Cloze de uma nota existente sem avaliar cartões e histórico envolvidos. Exportações seguem `../automacao-anki-python/SKILL.md`.

## Regras comuns

- **Perfil e especializações:** quando o alvo for PRF ou PF (inclusive o foco padrão PRF), aplicar a seção “Perfil de carreira” do núcleo e `../perfil-carreiras-policiais/SKILL.md`, uma vez por tarefa, carregando só as disciplinas pertinentes. Outro cargo ou concurso explícito prevalece.
- **Cloze:** antes de criar, reformular, aprovar ou avaliar omissões (inclusive uma conclusão de zero Cloze), ler `../gerar-revisao-anki/references/protocolo_cloze_cientifico.md`. Nota nova tem uma única omissão `{{c1::…}}` (várias só com a tag `Mnemonico`), e cada lacuna é coberta por D do mesmo lote. Preservar índices e histórico de notas existentes.
- **Pesquisa:** cartões criados ou reescritos substantivamente seguem a seção “Pesquisa na internet obrigatória” do núcleo. Todo D novo segue também a pesquisa de questões anteriores (Cebraspe C/E primeiro; depois outras bancas) de `../gerar-revisao-anki/references/protocolo-modo-estrategico.md`.
- **Visual 2.15:** cartões novos ou reformulados são montados com `../gerar-revisao-anki/scripts/html_anki.py`, conforme `../gerar-revisao-anki/references/protocolo_visual_html_anki.md`, com o bloco final 💡 Memorize.

## Reformulação estratégica

Para D, seguir `../gerar-revisao-anki/references/protocolo-modo-estrategico.md`, atlas e rubrica. Em reescrita substantiva de D, cumprir a pesquisa obrigatória de questões anteriores (Cebraspe C/E primeiro; depois outras bancas) da seção “Pesquisa e comparação por família” do protocolo. Diagnosticar operação, elemento decisivo, plausibilidade do erro e originalidade. Preservar explicações e enunciados bons; não alongar uma frase para fingir desafio. Toda alteração substantiva requer nova solução/conferência. Atualizar o registro e hash em novas exportações; coleções existentes seguem o fluxo de preservação de identidade e histórico.
