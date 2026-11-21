# Avaliação editorial da seleção Cloze

Estes casos sintéticos avaliam decisões de seleção, não comprovam aprendizagem nem substituem validação de conteúdo. Ao modificar esta política, confrontar as instruções com cada cenário e registrar o resultado real; não tratar a mera existência desta tabela como teste executado.

| Cenário | Decisão esperada | Falha a detectar |
| --- | --- | --- |
| Números já cobertos; há conceito prioritário cuja definição permite recuperar um termo determinado | Avaliar esse conceito separadamente para C | Concluir zero apenas pela cobertura numérica |
| R apresenta o nome do conceito e pede julgar sua definição; recuperar o nome sem pista também é relevante | Comparar operações; preferir substituir R novo por C se bastar | Descartar por coincidência de assunto ou acrescentar sempre |
| D exige aplicar regra; C recupera conceito necessário e distinto | Admitir ambos somente com ganho específico e carga justificada | Proibir coexistência ou aprová-la só pelo formato |
| Conceito aparece apenas no Extra de outro cartão | Inspecionar a frente; avaliar necessidade de recuperação direta | Afirmar cobertura ativa pela simples menção |
| Backup já pede a mesma resposta a partir da mesma informação | Não criar duplicata; registrar nota e operação | Produzir C adicional para atingir quantidade |
| Todos os candidatos relevantes estão cobertos ou exigem inferência; demais termos são periféricos | Aceitar zero com evidências específicas | Forçar pelo menos um Cloze |
| Uma frase permite dois conceitos distintos como resposta | Reformular contexto; mudar formato se continuar indeterminada | Aceitar só porque a lacuna é curta |
| Uma lacuna contém quatro conceitos | Reprovar; selecionar e separar alvos úteis em notas independentes | Confundir uma marcação com um conceito |
| Relação conceitual curta, importante, sem número e sem pista | Avaliar como candidato legítimo | Reservar Cloze exclusivamente a valores |
| Texto contém muitos termos técnicos de baixo valor | Descartar os periféricos | Converter automaticamente todos os termos |
| Converter R novo em C deixa os R restantes desequilibrados | Reavaliar seleção e restabelecer 50/50 no modo afetado (diferença máxima de 1 em total ímpar) | Inverter verdade, mudar tags ou acrescentar duplicatas |
| Fonte necessária não pôde ser verificada | Marcar pendência e limite da entrega | Justificar zero como ausência comprovada de alvo |

Casos adicionais:

- Conceito permanece visível e lacuna esconde palavra secundária sem utilidade: REFORMULAR para recuperar o conhecimento central.
- Expressão técnica importante com várias palavras: omitir o termo completo em um único c1.
- Frase curta que exprime uma única relação conceitual importante: admitir se determinada, com contexto e Extra específicos; não ocultar o parágrafo inteiro.

Conferir também: Em notas Cloze novas, aplicar o protocolo Cloze: usar uma única marcação `{{c1::…}}` por nota; mais de uma omissão somente em nota de mnemônico, com a tag `Mnemonico`; separar alvos independentes em notas próprias e explicar a omissão no Extra. Para mnemônicos, deixar visíveis o tema e as letras ou pistas do próprio mnemônico. Associar a cada novo Cloze desafiadores C/E do mesmo lote que cubram todas as lacunas. Preservar os índices e o histórico de notas existentes. A sintaxe e os vínculos declarados podem ser testados por scripts. Adequação, necessidade e redundância exigem revisão semântica.
