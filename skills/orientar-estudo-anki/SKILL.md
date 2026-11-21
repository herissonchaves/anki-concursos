---
name: orientar-estudo-anki
description: Orienta rotina Anki, recuperação ativa, botões de resposta, FSRS, carga diária e cartões com erros recorrentes, sem alterar coleção ou prometer desempenho.
---

# Estudo e manutenção no Anki

Leia `../gerar-revisao-anki/references/nucleo-pedagogico.md`. Antes de orientar, meça na coleção viva (somente leitura): `../automacao-anki-python/scripts/colecao_anki.py desempenho` (vencidos, acerto, segundos por revisão por disciplina), `dificeis` (lapsos e leeches) e `lacunas --alvo PRF` (prioridades Alta/Média do banco `referencias/` com poucas notas ou muitos lapsos). Responda "o que revisar ou estudar agora" com esses números, priorizando acerto baixo, lapsos concentrados e lacunas Alta. Utilize também dados já fornecidos; pergunte tempo disponível e clientes/versões apenas se necessários para uma recomendação específica. Para configurações, confira o manual oficial atual, pois nomes e recursos variam entre versões.

1. Estudar a explicação antes de memorizar; tentar recuperar antes de mostrar resposta. Em C/E, recuperar motivo ou correção da proposição; acertar por chute não satisfaz esse critério. Não escrever uma dissertação em cada revisão.
2. Usar Novamente/Again para esquecimento ou erro; Difícil/Hard para lembrança correta com esforço; Bom/Good para lembrança correta normal; Fácil/Easy para lembrança imediata. Não ensinar a marcar Difícil quando esqueceu. O critério de correção deve corresponder ao alvo do cartão; exigir literalidade só quando necessária.
3. Priorizar revisões pendentes. Se a carga excede o tempo disponível, reduzir temporariamente novos cartões, inclusive a zero, em vez de esconder o atraso por limite baixo de revisões. Não prescrever número universal de novos por dia nem prever carga sem dados. Ajustar com tempo e desempenho observados.
4. FSRS: verificar compatibilidade de todos os clientes; explicar retenção desejada versus carga. Não copiar parâmetros de outra pessoa, recomendar 100% ou alterar agendamento em massa. O valor padrão documentado pode servir de ponto de partida, não de promessa de desempenho. Conferir opções atuais de otimização e passos no manual antes de orientar cliques.
5. Cartões irmãos Cloze podem revelar respostas entre si; explicar enterramento de irmãos quando pertinente. Não confundir enterramento temporário com suspensão. Intercalar temas relacionados depois de compreender fundamentos, sem impor embaralhamento que destrua pré-requisitos.
6. Erros recorrentes/leeches: inspecionar cartão e pré-requisito, procurar interferência entre conceitos, melhorar contexto ou dividir alvos independentes; sugerir pausa para reaprender quando útil. Lapsos não provam desatenção. Preservar IDs e histórico ao editar a mesma nota; mudança de frente em pacote pode gerar nova nota.
7. Reavaliar com tempo real, atrasos, esquecimentos e questões inéditas. Sem métricas, oferecer plano provisório explícito. Não transformar toda questão errada em vários cartões. Não operar a coleção sem autorização para a ação.

Fontes: [botões e revisão](https://docs.ankiweb.net/manual/studying), [opções e FSRS](https://docs.ankiweb.net/manual/deck-options), [importação e atualização](https://docs.ankiweb.net/manual/importing/text-files). Consulta de referência: 01/11/2026; rever antes de aconselhar configurações futuras.
