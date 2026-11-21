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

- **R (rápido):** fácil, um alvo direto, linguagem simples, sem pegadinha nem raciocínio complexo.
  Sem teto fixo e sem limite pela quantidade de D.
- **D (desafiador Cebraspe):** caso curto, didático, com dado decisivo e uma decisão real (aplicar,
  inferir, distinguir); a dificuldade está na decisão, não no juridiquês. Definição disfarçada vira R.
- **Cloze:** uma omissão `{{c1::…}}` por nota (várias só em nota de mnemônico, tag `Mnemonico`);
  cada lacuna coberta por um D do mesmo lote. Antes de escolher formatos, inclusive para concluir
  zero Cloze, leia `references/protocolo_cloze_cientifico.md`.
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
   Questões anteriores: obrigatórias para todo D, antes de escrevê-lo, salvo banco suficiente (item
   Cebraspe C/E oficial do mesmo subassunto já no banco) — primeiro Cebraspe C/E
   (modelo de forma), depois outras bancas (o que se cobra, pegadinhas); use-as como inspiração
   para itens autorais, nunca como cópia. Para R/Cloze, questões só quando o banco não mostrar o que
   se cobra; no Cloze, pesquise mnemônicos e confira cada pista na fonte. Sem Cebraspe acessível:
   `inspiracao_geral` + limitação; sem outra banca: `outras_bancas_pendencia`. Sem pesquisa
   disponível, a entrega não é final verificada.
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
- TSVs UTF-8 sem BOM, sem cabeçalho, três campos. C/E: exatamente uma entre `Tipo_Revisao_Rapida` e
  `Tipo_Desafiadora_Cebraspe` (D também `Estilo_Cebraspe`); Cloze sem essas tags. Sem tags de
  prioridade. Cada D leva ainda uma tag por questão de concurso citada em `refs`, igual ao nome do
  arquivo da questão em `referencias/questoes/` (ex.: `cebraspe-2021-prf-080`); o `montar_lote.py`
  põe essas tags e o validador da calibração bloqueia D sem elas.

## Barreiras de exportação

O exportador e o `finalizar_lote.py` bloqueiam: D sem `calibracao_cebraspe.json`
(`references/registro-calibracao-cebraspe.md`), R/Cloze sem `revisao_recuperacao.json`
(`references/registro-revisao-recuperacao.md`), hashes divergentes, sinais do lint pendentes
(corrija ou justifique em `fonte/sinais_resolvidos.json`), paridade 50/50 e, em PDF, cobertura
Alta/Média incompleta (`references/cobertura-pdf.md`). As barreiras checam documentos, não a verdade
do gabarito nem a aprendizagem. Não use helpers de teste para preencher auditoria. Casos de
referência sob demanda: `references/protocolo_clareza_pedagogica.md` e
`references/testes_regressao_pedagogicos.md`. Rotina, FSRS e carga: `../orientar-estudo-anki/SKILL.md`.
