> Política comum: [nucleo-pedagogico.md](nucleo-pedagogico.md). Distribuição, equilíbrio e exceções: [matriz_tipos_quantidades.md](matriz_tipos_quantidades.md). Este documento complementa essas regras.

# Protocolo de clareza, dificuldade genuína e economia

**Norma eliminatória**, aplicável à geração por PDF/resumo, caderno de erros, melhoria e auditoria de lotes de qualquer tamanho. Complementa o núcleo, sem alterar a matriz de distribuição ou suas exceções. Ser juridicamente correto e estruturalmente válido é NECESSÁRIO, mas NÃO SUFICIENTE. Nenhuma etiqueta de dificuldade garante qualidade.

## 1. Teste de inteligibilidade antes de qualquer aprovação

Para cada cartão candidato, simular um aluno que **já estudou o tema**, mas ainda pode não lembrar a solução. O aluno precisa compreender a tarefa sem recorrer à apostila, ao chat, ao verso nem a vocabulário obscuro desnecessário. A pergunta é "Consigo entender precisamente o que devo julgar, ainda que erre a resposta?". Se NÃO: `REFORMULAR`, nunca `APROVAR`.

- Português natural, sujeito e ação concretos; preferir termos técnicos jurídicos padronizados e necessários, explicando-os pelo contexto quando não forem o alvo testado.
- Frente com **uma proposição julgável**, fato relevante e condição decisiva. Evitar premissa decorativa, concatenação de teses, abstração empilhada, duplas negativas, encadeamento de subordinadas e referente ambíguo.
- Priorizar frente rápida de ~8–25 palavras e frente desafiadora normalmente de ~20–50 palavras. **Não são limites duros**: extensão justificável por cenário relevante é permitida; não reduzir até eliminar condição jurídica indispensável. Se mais de 50 palavras, justificar necessidade e tentar condensar. Rejeitar complexidade verbal que não agregue raciocínio.
- Não criar "duas perguntas em uma"; dividir apenas se ambas forem importantes e não redundantes, lembrando o custo de revisão.
- Na frente de C/E, evitar repetições de absolutos (`sempre`, `nunca`, `jamais`, `automaticamente`, `necessariamente`, `qualquer`, `apenas`, `somente`, `em todos os casos`) que forneçam pistas para Errado. Podem ser essenciais à tese jurídica: avaliar sem proibir indiscriminadamente. **Equilibrar verdade/erro não autoriza fabricar falsidades.**

## 2. Dificuldade verdadeira — obrigatória para `Desafiadora`

Antes de redigir registrar, fora do cartão:
`alvo juridico | regra aplicada | dado decisivo | inferencia exigida | erro plausivel | fonte`.
A inferência deve depender da aplicação de uma condição, exceção, comparação, consequência ou distinção real. Se basta reconhecer uma definição literal, reclassificar como **rápida** (se relevante) ou usar Cloze/descartar; **não** chamar definição longa de desafiadora. Dificuldade não vem de trocar personagens, usar linguagem rebuscada, enganar por advérbio ou inserir detalhes supérfluos.

## 3. Verso que ENSINA e continua rápido

- Abrir com `✅ Certo` ou `❌ Errado` para C/E. Em 1–3 frases curtas: explicar **qual fato do caso ativa a regra, qual regra e por que a conclusão decorre dela**. Para rápido conceitual, basta regra/contraste; para aplicação, mencionar fato decisivo expressamente.
- Incluir artigo/norma verificável quando relevante, sem referência genérica a "material", "PDF", "aula", "doutrina indicada". Em Direito, conferir fonte primária atual; dizer quando uma hipótese depende de circunstâncias, não fazer generalizações absolutas erradas.
- Pode acrescentar dica mnemônica útil, sem obrigação, com distinção ou lembrança recuperável, nunca repetição vazia ou slogan enigmático. Se uma explicação curta não resolve dúvida, reformular a frente e/ou a seleção.
- Não fazer do verso uma aula longa: cartões de revisão pressupõem estudo prévio. Conteúdo muito complexo pode exigir estudo/questões antes de Anki.

## 4. Deduplicação COGNITIVA, inclusive C/E↔Cloze

Criar mapa por alvo: `conceito | regra ou exceção | operação mental | decisão: manter/fundir/excluir | origem`.
Comparar candidatos do lote uns contra os outros **e** com backup `.colpkg` acessível, independentemente de tags, modelos ou redação. Pergunta obrigatória: "Se eu acertar o cartão A, o B ainda exige conhecimento ou operação adicional relevante?" Se não, em geração nova manter o melhor; em coleção existente registrar a redundância e sugerir fusão, sem excluir, suspender ou fundir sem autorização específica. Cloze e C/E do mesmo fato só coexistem quando testam **operações diferentes e úteis**. Sem backup, informar que deduplicação externa não foi possível, sem fingir análise.

## 6. Auditoria adversarial por cartão — registro observável

Preencher `ID | prioridade | tipo real | alvo | regra | fato decisivo | operacao | clareza SIM/NÃO | duplicação SIM/NÃO | verso explica SIM/NÃO | fonte | decisão`.
Reprovação imediata de qualquer um:
1. Pergunta não compreensível sem ler o verso ou a fonte.
2. Desafiadora sem inferência genuína.
3. Duplicação cognitiva sem benefício adicional justificável.
4. Gabarito ambíguo, interpretação concorrente razoável ou erro de Direito vigente.
5. Verso que só repete o gabarito, não explica a decisão, ou depende de documento externo.
6. Pista lexical previsível, por exemplo vários "sempre/jamais" falsos, quando suprime o teste do conceito.

Reformular e executar **segunda conferência da solução** sem mostrar gabarito; reprovar de novo -> `REJEITAR`. Cloze: testar cada `cN` visível separadamente. A classificação `APROVAR` deve ser justificada, não fornecida automaticamente por script. Em geração nova, não exportar cartão duvidoso. Em coleção existente, preservar o cartão, explicitar a pendência e não alterar seu histórico ou excluí-lo sem autorização específica.

## 7. Lint de sinais de risco (apoio, nunca prova de qualidade)

Se houver lote TSV/ZIP, rodar **depois dos validadores estruturais**:
`python3 skills/gerar-revisao-anki/scripts/auditar_clareza.py PACOTE.zip --report relatorios/sinais_clareza.tsv`
Também aceita `.tsv`. Sinaliza frentes extensas, absolutos, metarreferências e pares lexicais potencialmente parecidos. **Não equivale a auditoria semântica**, não define sozinho Certo/Errado, nem autoriza rejeitar termos jurídicos relevantes. Os avisos devem ser revisados e a decisão documentada. Se a validação não pôde ser executada, informar explicitamente.

## 8. Exemplos comparativos (autorais, didáticos)

**RUIM:** "Um espectador casual presencia perigo à criança, mas não tem dever especial de garantia. Sua situação é automaticamente idêntica à do pai responsável, para fins de homicídio por omissão."

**MELHOR:** "Pai e desconhecido veem criança se afogando e podem salvá-la sem risco. Se nada fazem e ela morre, ambos respondem necessariamente por homicídio omissivo." → Errado. O pai, como garantidor, *pode* responder por homicídio omissivo; o desconhecido, sem dever especial de impedir o resultado, pode incorrer em omissão de socorro. Dependem dos demais requisitos do tipo e responsabilidade.

**RUIM:** "Uma contravenção admite reclusão por se tratar de infração penal." **MELHOR:** "Um juiz aplica reclusão por perturbação do sossego, contravenção penal. A espécie de pena está correta." → Errado. Contravenção prevê prisão simples e/ou multa, não reclusão; distinguir a lei de cada infração.

**RUIM:** "Na teoria quadripartida, a punibilidade figura como quarto elemento do crime, diferentemente da tripartida." (definição disfarçada de desafiadora). **AÇÃO:** reclassificar como revisão rápida ou excluir se já recuperada por outra nota, sem inventar dificuldade.
