---
name: portugues-cebraspe-qualidade
description: Protocolo especializado obrigatório de Língua Portuguesa para geração, melhoria e auditoria de cartões Anki, especialmente C/E autorais inspirados no Cebraspe.
---

Leia primeiro `../gerar-revisao-anki/references/nucleo-pedagogico.md`. Seus critérios comuns valem também para Português.


# Engenharia especializada de Português

Aplicar o núcleo comum; para geração usar `../gerar-revisao-anki/SKILL.md`. Ler `../gerar-revisao-anki/references/protocolo_cloze_cientifico.md` antes de selecionar formatos, inclusive quando a conclusão puder ser zero Cloze.

## Especialização obrigatória

Antes de selecionar, gerar, melhorar, fazer caderno de erros ou auditar Português, ler exatamente as três referências:
1. `references/atlas_operacoes_cebraspe_portugues.md`
2. `references/roteiro_auditoria_e_modelos.md`
3. `references/evidencias_e_limitacoes.md`

Não alegar leitura não realizada. Diferenciar textos de teoria, comentários e itens oficiais; não copiar, não parafrasear superficialmente questões originais. Origem e página aparecem apenas nos relatórios.

## Seleção e coleção

1. Mapear `tema | construção/texto | competência | risco de erro | operação | interpretação concorrente | elemento decisivo | página/fonte no relatório`.
2. Na coleção viva (`../automacao-anki-python/scripts/colecao_anki.py buscar`, `dificeis`, `desempenho`, somente leitura; fora deste PC, `.colpkg`) analisar notas e desempenho QUANDO LEGÍVEIS; verificar redundância cognitiva, não presumir histórico.
3. Triagem A/B/C por incidência verificada, transferibilidade, importância e economia. Rápida legítima pode recuperar conceito linguístico relevante sem cenário artificial; não decorar lista periférica.

## Itens C/E desafiadores

- Exigir operações reais: substituição/reescrita e efeitos sobre gramaticalidade, sentido e coesão (G/S/C); regência, concordância, crase, vírgula, colocação, referência, escopo, ambiguidade, conectivos.
- Quando a reescrita exigir preservação simultânea, testar **G**ramaticalidade, **S**entido e **C**oesão/referência separadamente. Para certo, TODAS as dimensões exigidas devem preservar-se; para errado, mostrar a dimensão decisiva.
- Para `que`, `se`, `lhe`, relativos, pontuação e coesão, contexto completo sem «linha 8». Um julgamento nuclear com possível combinação de operações relacionadas.
- Considerar análises gramaticais concorrentes: se legitimamente controversas sem solução inequívoca, qualificar ou rejeitar. Sem absoluto óbvio, frase monstruosa ou cenário inventado sem função. Registrar leitura concorrente plausível.

## C/E rápidos e Cloze

- **Rápido:** reconhecer regra linguística central de modo preciso e quase imediato (p. ex. função sintática ou contraste entre estruturas), sem transformar em pegadinha difícil por artifício.
- **Cloze:** selecionar conceitos linguísticos importantes e manter o contexto que determina a resposta. Em notas Cloze novas, aplicar o protocolo Cloze: usar uma única marcação `{{c1::…}}` por nota; mais de uma omissão somente em nota de mnemônico, no formato de `skills/gerar-revisao-anki/references/tags.md` (título `Mnemônico SIGLA:`, letras visíveis, resto de cada termo em c1, origem só no verso); separar alvos independentes em notas próprias e explicar a omissão no Extra. Para mnemônicos, deixar visíveis o tema e as letras ou pistas do próprio mnemônico. Associar a cada novo Cloze desafiadores C/E do mesmo lote que cubram todas as lacunas. Preservar os índices e o histórico de notas existentes. Rejeitar ambiguidades, respostas visíveis, omissões secundárias e duplicatas cognitivas.

## Formato, qualidade e entrega

Frente sem resposta ou metarreferência ao PDF; C/E com verso `✅ Certo<br><br>fundamento` ou `❌ Errado<br><br>fundamento e correção`; dica mnemônica opcional. Tags conforme `skills/gerar-revisao-anki/references/tags.md` (`Lingua_Portuguesa::Assunto::Topico`, PDF e página só em card feito sobre o PDF, uma de tipo: `Rapida`, `Desafiadora` ou `Cloze`; nos D, a questão de origem). Cloze com Extra útil. Sem imagens.

## Integração do modo estratégico

Para D, aplicar também `../gerar-revisao-anki/references/protocolo-modo-estrategico.md` e sua rubrica. O atlas de Português e G/S/C permanecem obrigatórios. Avaliar dificuldade editorial sem confundi-la com estilo da banca; modelos internos não demonstram nível psicométrico. Uma conclusão e sua justificativa podem integrar um julgamento nuclear quando relacionadas. Exportações de D novos incluem o registro de calibração, sem expor metadados na frente.
