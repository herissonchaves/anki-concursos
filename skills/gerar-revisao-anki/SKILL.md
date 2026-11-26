---
name: gerar-revisao-anki
description: Cria cartões Anki C/E e Cloze com recuperação ativa, feedback corretivo, seleção econômica e validação de exportação, nos fluxos revisão por PDF e caderno de erros, com rápidos, desafiadores e Cloze.
---

# Geração Anki

**Lote exportado a partir de PDF: siga só `references/roteiro-lote-pdf.md`.** Ele resume as regras
obrigatórias e os comandos (texto limpo do PDF, coleção viva, banco, modelo do gerador,
`finalizar_lote.py`) e substitui a leitura integral das referências nos casos comuns. Abra um
documento completo só em dúvida, caso especial (Português, imagens, caderno de erros) ou ao alterar
o projeto. Os passos abaixo valem para pedidos inline, tema avulso e os demais fluxos.

Política comum: `references/nucleo-pedagogico.md` (leia uma vez por tarefa, sem carregar todos os
documentos). PRF ou PF: aplique a seção "Perfil de carreira" do núcleo e
`../perfil-carreiras-policiais/SKILL.md`; PF = **Agente**; PRF usa **Inglês**; outro cargo ou
concurso explícito prevalece e exige programa próprio.

## Tipos de cartão

- **R (rápido, modo rápido):** memorização de conceito, fácil de responder. Frente C/E afirmativa de 8 a
  15 palavras com um fato só, sem caso, personagem, exceção, negação ou pegadinha; o Errado troca um
  único elemento (prazo, número, sujeito, consequência, termo) por uma confusão real; verso com a
  regra em uma frase e o 💡 Memorize; lista longa vira um R por item. Sem teto fixo e sem limite pela
  quantidade de D. Com material anexado, todo conceito dele ganha ao menos um R ou outro card (2.39,
  `references/cobertura-pdf.md`).
- **D (desafiador Cebraspe):** caso curto, didático, com dado decisivo e uma decisão real (aplicar,
  inferir, distinguir); a dificuldade está na decisão, não no juridiquês. Definição disfarçada vira R.
- **Cloze (modo Cloze, 2.40):** memorização de conceitos e mnemônicos por omissão de palavras, sem
  exigir questão real nem D. Dois tipos: **mnemônico** de lista ou sequência (frente `Mnemônico SIGLA:`,
  letras visíveis e o resto de cada termo em c1, origem só no verso, `references/tags.md`; sem limite de
  palavras) ou **conceito-chave** (uma omissão `{{c1::…}}` no núcleo do conceito, frase curta, Extra com
  a regra em uma frase + Memorize). Questão (`refs` + `cobra`) e D que aplica a lacuna (`cob`) só quando
  houver. Antes de escolher formatos, inclusive para concluir zero Cloze, leia
  `references/protocolo_cloze_cientifico.md`.
- 50% Certo e 50% Errado nos R e, separadamente, nos D (total ímpar: diferença de 1); composição e teto em
  `references/matriz_tipos_quantidades.md`. Não repetir o mesmo fato nos três formatos.

## Passos (fora do roteiro de PDF)

1. Identifique pedido, material, disciplina, concurso e teto; pergunte só o que impedir a tarefa.
2. **Coleção e banco primeiro.** Busque na coleção viva os termos centrais
   (`../automacao-anki-python/scripts/colecao_anki.py buscar`, somente leitura; `.colpkg` só fora
   deste PC) e compare operações cognitivas, não só palavras. Siga `../referencias-questoes/SKILL.md`:
   prioridade e edital salvos, conteúdos verificados (até 90 dias, com checagem rápida), notícias
   e questões; importe e salve as questões do arquivo enviado. Vincule cada alvo ao programa do
   concurso (seção "Relevância para PRF e outros concursos" do núcleo); exatidão não basta, e
   recorrência não se presume sem contagem.
3. **Internet.** Conteúdo: pesquisa obrigatória para todo cartão criado ou reescrito (fonte primária
   vigente em Direito, `references/radar-juridico-atualizacao.md`), salvo o reuso válido do banco.
   Questões anteriores (2.37): **R e D** citam em `refs` ao menos uma questão real
   de concurso que cobra o seu conteúdo (qualquer banca ou cargo); busque-as antes de escrever, banco
   primeiro, internet para o que faltar, salvo banco suficiente no D (item Cebraspe C/E oficial do
   mesmo subassunto já no banco) — primeiro Cebraspe C/E (modelo de forma), depois outras bancas (o
   que se cobra, pegadinhas); use-as como inspiração para itens autorais, nunca como cópia. Sem questão
   localizada: nenhum D; R no núcleo do cargo (`nucleo`); o resto é Baixa e, se for conceito do
   material anexado, vira R sem `refs` ou Cloze (2.39/2.40, `references/cobertura-pdf.md`).
   **Complementos (2.39):** compare o material com o item do edital do mesmo assunto e com as questões
   achadas; o tópico cobrado em questão real e ausente do material também vira card (unidade `extra`,
   fonte salva no banco). Cloze (2.40) não exige questão: cite-a em `refs` (+ `cobra`) quando houver;
   pesquise mnemônicos e confira cada pista na fonte. Sem Cebraspe acessível:
   `inspiracao_geral` + limitação; com Cebraspe e sem outra banca: `outras_bancas_pendencia`. Sem
   pesquisa disponível, a entrega não é final verificada.
4. D: o "Resumo operacional" no topo de `references/protocolo-modo-estrategico.md`, só a seção da
   disciplina de `references/atlas-multidisciplinar-cebraspe.md` e só a "Rubrica por cartão" de
   `references/avaliacao-modo-estrategico.md` (o restante, em dúvida ou auditoria). Português: `../portugues-cebraspe-qualidade/SKILL.md`
   (obrigatório). Imagens: `references/protocolo_imagens_reais_anki.md`. Linguagem e lacunas:
   `references/revisao-integral-e-linguagem.md`.
5. Defina resposta e fundamento antes da frente; resolva cada frente de novo sem olhar o verso e
   procure leitura concorrente; corrija e confira outra vez.
6. Poucos cartões sem pedido de arquivo: entregue inline, com síntese proporcional da verificação.
   Lote exportado: modelo `modelos/gerar_lote_modelo.py` + `scripts/montar_lote.py` e
   `../automacao-anki-python/scripts/finalizar_lote.py`, como no roteiro (seções 7 e 8).
7. **Salve no banco tudo o que pesquisou** (edital, conteúdo, notícia, prioridade, questões citadas
   e itens Cebraspe C/E oficiais do tema) e liste os IDs em `selecao_e_fontes.txt`. Relate cartões
   efetivos, fontes e decisões; a conferência do próprio agente é autorevisão (declare). Não alegue
   importação no Anki.

## Formato

- HTML montado com `scripts/html_anki.py` (`references/protocolo_visual_html_anki.md`): blocos
  📌 Regra, 🔎 No caso, ⚠️ Onde está o erro, ✔️ Por que está certo, esquemas quando ajudarem; CSS
  único de `scripts/estilo_anki.py` (Arial 20 px); nada de script, CSS externo ou mídia remota.
- Verso e Extra terminam no bloco **💡 Memorize** (no Errado, a formulação correta).
- TSVs UTF-8 sem BOM, sem cabeçalho, três campos.
- **Tags** (regra única em `references/tags.md`): só `Disciplina::Assunto::Topico`; nome curto do PDF
  (`Missao_07`) e `Pagina_NN` apenas em card feito sobre o PDF; exatamente uma de tipo (`Rapida`,
  `Desafiadora` ou `Cloze`); nos D, uma por questão de `refs`, igual ao nome do arquivo em
  `referencias/questoes/` (ex.: `cebraspe-2021-prf-080`). Proibidas: concurso/cargo (`PRF`, `PF`…),
  `Estilo_Cebraspe`, `Revisao_PDF`, `Mnemonico` e qualquer genérica. O `montar_lote.py` monta as tags e
  falha fora da regra; `validar_anki.py --new` reprova.

## Barreiras de exportação

O exportador e o `finalizar_lote.py` bloqueiam: D sem `calibracao_cebraspe.json`
(`references/registro-calibracao-cebraspe.md`), R/Cloze sem `revisao_recuperacao.json`
(`references/registro-revisao-recuperacao.md`), hashes divergentes, sinais do lint pendentes
(corrija ou justifique em `fonte/sinais_resolvidos.json`), paridade 50/50 e, em PDF, cobertura
incompleta (unidade sem card nem nota da coleção, Baixa com D/Cloze; `references/cobertura-pdf.md`). As barreiras checam documentos, não a verdade
do gabarito nem a aprendizagem. Não use helpers de teste para preencher auditoria. Casos de
referência sob demanda: `references/protocolo_clareza_pedagogica.md` e
`references/testes_regressao_pedagogicos.md`. Rotina, FSRS e carga: `../orientar-estudo-anki/SKILL.md`.
