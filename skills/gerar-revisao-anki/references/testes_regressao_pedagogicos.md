> Política comum: [nucleo-pedagogico.md](nucleo-pedagogico.md). Distribuição, equilíbrio e exceções: [matriz_tipos_quantidades.md](matriz_tipos_quantidades.md). Este documento complementa essas regras.

# Casos de regressão pedagógica

Rodar como inspeção de linguagem e de operação mental por responsável pelo lote. **Não confundir com testes automatizados executáveis**; a validade jurídica deve ser checada em fonte primária vigente.

1. **Crime omissivo:** frente abstrata "espectador casual com dever geral... automaticamente idêntico..." deve ser REFORMULADA para dois atores (pai vs desconhecido), fato decisivo de posição de garantidor e verso com condições da imputação. Não afirmar homicídio automático do pai.
2. **Pena por contravenção:** preferir "Juiz aplica reclusão por perturbação do sossego; a pena é compatível com contravenção" a texto sobre "qualquer pena privativa de liberdade". Verso distingue prisão simples/multa, com norma de apoio.
3. **Peculato e particular:** exigir ciência da função e concurso doloso; frente não deve sugerir que simples proximidade ou presença do particular é suficiente; verso explica comunicação da elementar (art. 30 CP).
4. **Ameaça oral/transeunte:** explicitar ausência de vestígio; verso diferencia possibilidade de provar por testemunhas da obrigatoriedade do exame de corpo de delito quando há vestígio. Não dizer que toda ameaça é transeunte.
5. **Teoria quadripartida:** "punibilidade como quarto elemento" isolado NÃO é inferência Cebraspe; reclassificar rápida ou excluir se duplicado por Cloze. Não adicionar parágrafo sem fato decisivo para fingir D.
6. **Cloze + C/E repetidos:** a mesma definição com `{{c1::...}}` e como julgar C/E somente pode coexistir se testar operações distintas úteis, documentadas. Similaridade textual sozinha não é base de rejeição.
7. **Pistas absolutas:** se muitos Errados usam "sempre", "jamais" e "automaticamente", reescrever para erro substantivo sem sinal de gabarito óbvio. Não proibir uso legalmente necessário de termos absolutos.
8. **Verso tautológico:** se o verso só cita conceito, exige resposta à pergunta "qual fato do caso ativa essa regra?"; se não há fato concreto no cartão rápido, oferecer contraste factual útil.
9. **Direito atualizado:** validar artigo, exceções e jurisprudência conforme o tema e data. Sem acesso à norma, declarar pendência em vez de afirmar validação.
10. **Lote grande:** piloto interno 8–12, mapa de alvos, 100% de crítica individual com segunda conferência da solução, exclusão de candidatos ruins sem repor com trivia; lint + validações; relatório real.

Critérios de aceite: 100% das frentes compreensíveis sem gabarito, todos D com inferência registrada, todos versos explicativos, nenhum candidato redundante sem justificativa, nem relatórios de testes fictícios. Essa verificação é humana; o script `auditar_clareza.py` apenas sinaliza riscos.

## Regressões do modo estratégico

Aplicar também `avaliacao-modo-estrategico.md` (E01–E12). Para checagens de código, usar `../tests/test_calibracao_cebraspe.py`. Os testes documentais devem preservar o limite conhecido: definição rotulada D ou solução falsa com registro completo podem passar. A rubrica semântica deve reclassificar/rejeitar esses casos; não anunciar que o script resolve o problema conceitual.
