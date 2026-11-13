# Avaliação repetível do modo estratégico — 2.7

Usar em todo lote D, proporcionalmente, e em mudanças do plugin. A avaliação é editorial e pode ser feita pelo mesmo agente; identificá-la como autorevisão. Teste automatizado não julga conteúdo.

## Rubrica por cartão

Registrar PASSA / FALHA / PENDENTE e uma evidência concreta para cada dimensão:

1. **Correção:** gabarito, solução e correção da falsidade derivam dos dados e da fonte aplicável.
2. **Determinação:** contexto suficiente, condições explícitas e leitura concorrente resolvida.
3. **Operação D:** há aplicação/inferência/discriminação contextual; o dado decisivo participa da solução.
4. **Comparação:** item real e operação estão identificados; a operação autoral é comparável ou a inspiração geral está declarada.
5. **Autoria:** situação/texto/encadeamento reconstruídos; não é troca superficial de nomes e números.
6. **Feedback:** explica a passagem dos dados à conclusão, enfrenta a confusão plausível e corrige o erro.
7. **Linguagem e didática:** situação e julgamento compreensíveis sem graduação jurídica; jargão dispensável removido, termos necessários explicados sem pistas na frente; verso conecta regra, fato decisivo e conclusão. Registrar separadamente da operação D: texto claro não comprova desafio, e texto difícil não comprova raciocínio.
8. **Revisão útil:** alvo pertinente, carga proporcional, ausência de redundância funcional e de pistas de resposta.

Falha em correção, determinação, autoria ou linguagem/didática impede aprovação até a correção. Falha na operação D exige reformulação ou reclassificação R, sem alterar gabarito para cumprir proporção. Referência indisponível impede declarar fidelidade comparada, mas a inspiração geral pode ser explicitada se conteúdo e pertinência estiverem verificados. Não calcular média que esconda falha essencial.

## Procedimento de avaliação do gerador

Definir temas e fontes antes da geração. Em lote pequeno, avaliar todos; em lote grande, fazer piloto interno proporcional e revisar todos os cartões finais. Para avaliar transferência, reservar itens de comparação que não tenham servido como modelos de redação e registrar essa separação. Não alegar cegamento: o mesmo agente pode lembrar fontes e soluções.

Guardar solicitação/escopo, versão do plugin, IDs, referências de construção e comparação, texto inicial, resultados da rubrica, alterações e resultado final. Contar candidatos, aprovados sem revisão, reformulados, reclassificados e rejeitados com denominadores explícitos. A seleção intencional não permite estimar desempenho em todos os concursos. Não inventar percentuais de fidelidade.

## Casos sintéticos de regressão editorial

Estes são estímulos de teste, não cartões aprovados nem itens oficiais. Não inseri-los automaticamente em lotes do usuário. As soluções dependem das premissas explícitas; não são fontes de Direito, gramática normativa ou software atual.

| Caso | Estímulo | Resultado esperado e fundamento |
|---|---|---|
| E01 | Definição direta de proposição lógica, marcada D | RECLASSIFICAR R se útil; não há aplicação. |
| E02 | `P → Q; Q; logo P`, com verso Certo | REJEITAR o gabarito; P falso/Q verdadeiro é contraexemplo. |
| E03 | `P → Q; ¬Q; logo ¬P`, com verso Certo | Operação e solução compatíveis; aprovação final depende dos demais critérios. |
| E04 | Duas proposições verdadeiras ligadas por uma causalidade não sustentada | Julgar a ligação; verdade das partes não prova o nexo. |
| E05 | Um componente da velocidade zera; conclui-se que o vetor é nulo, havendo outro componente não nulo | Errado. O componente restante decide; pode ser D curto. |
| E06 | Conservação da energia mecânica aplicada atravessando uma etapa explicitamente dissipativa, sem reposição dessa energia | Errado; delimitar etapas e grandezas. Não confundir com conservação de momento ou energia total. |
| E07 | Regra fictícia fornecida: X é autorizado se e somente se A e B. Caso traz A e não B; item conclui que X está autorizado | Errado sob as premissas. A bicondicional explicita a necessidade de B; não apresentar como regra jurídica real. |
| E08 | Recurso hipotético exige permissão P; conta não tem P; item conclui acesso porque houve login | Errado sob as premissas; autenticação não supre a condição fornecida. |
| E09 | Texto autoral relata expectativa condicionada; item afirma realização certa | Errado se a condição continua aberta; não extrapolar compromisso do texto. |
| E10 | Referência oficial transposta apenas com nomes/números diferentes | REFORMULAR por autoria insuficiente mesmo com gabarito correto. |
| E11 | Questão anulada usada como prova inequívoca do conteúdo | PENDENTE; buscar outra fonte e resolver a controvérsia. |
| E12 | JSON completo e scripts aprovados, sem revisão da solução | PENDENTE; completude declarada não comprova análise semântica. |

Em cada nova versão, confrontar esses casos com o protocolo, registrar resultados reais e falhas remanescentes. Testes de código devem demonstrar também seus limites: uma solução falsa com metadados completos pode passar pelo verificador documental. Nunca anunciar que ele passou a detectar erros conceituais em geral.

## Regressão editorial de clareza e desafio — 2.8.3

Aplicar junto à rubrica; estímulos sintéticos, sem alegação de conteúdo jurídico verificado.

| Caso | Estímulo | Decisão esperada |
|---|---|---|
| D01 | Caso exige distinguir duas condições, mas usa latinismos dispensáveis | Reformular em português direto, preservando condições e inferência. |
| D02 | Reescrita clara já informa o enquadramento que o aluno deveria descobrir | Reformular para retirar a pista e manter os fatos suficientes. |
| D03 | Nome e profissão adicionados a uma definição direta, sem efeito na solução | Não aprovar como D; reconstruir aplicação ou reclassificar R se esse for o alvo. |
| D04 | Caso curto, compreensível, exige aplicar exceção; verso liga regra e fato | Passa em clareza e operação; conferir demais critérios antes da aprovação final. |
| D05 | Termo técnico essencial fica preservado e é explicado no verso | Aceitar linguagem se o contexto permite julgar e a precisão é mantida. |
| D06 | Verso cita apenas artigo ou classificação | Reformular com explicação da regra e de sua aplicação ao fato decisivo. |
| D07 | Simplificação remove condição que decide a resposta | Repor a condição e resolver novamente; clareza não autoriza mudar o conteúdo. |

## Avaliação do conjunto — 2.13

Para comparar versões ou avaliar a geração em várias disciplinas e formatos, aplicar `avaliacao-pedagogica-multidisciplinar.md`. Os casos fixos servem à regressão e não substituem material reservado nem resultados de uso.
