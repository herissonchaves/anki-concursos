# Revisão dos cartões de Matemática — coleção de 20/11/2026

Backup lido em modo somente leitura: `collection.anki21b` (esquema moderno), 455 notas,
455 cartões e 3.110 revisões no total. O baralho **Matemática** tem 47 notas e 47 cartões:

| Lote de origem | R | D | Cloze | Suspensos |
| --- | --- | --- | --- | --- |
| Funções exponenciais e logarítmicas (`Fonte_Projeto_Missao_MAT010001`) | 10 | 10 | 5 | 8 |
| Porcentagem (`Matematica_Porcentagem`) | 8 | 11 | 4 | 0 |

IDs deste registro: `F_` = lote de funções, `P_` = lote de porcentagem, seguidos da tag
`ID_` da nota. Os 13 cartões de porcentagem com tag de complemento e os 4 Cloze de
porcentagem ainda são novos (sem revisões).

## Diagnóstico geral

1. **Nenhum verso seguia o padrão visual atual** (blocos 📌 Regra / 🔎 No caso / ⚠️ Onde
   está o erro, esquema e 💡 Memorize): os dois lotes são anteriores a ele. Os versos
   eram corretos, mas curtos, sem o resumo final para repetir de memória e, em vários
   Errados, sem apontar o ponto exato do erro. Todos os 47 versos/Extras foram refeitos
   com `html_anki.py`, mantendo o gabarito.
2. **Conteúdo matemático**: todos os gabaritos foram resolvidos de novo a partir da frente;
   nenhum estava errado.
3. **Defeitos de frente** em 6 notas (abaixo).
4. **Sinais de dificuldade**: `F_R04` teve três “Novamente” seguidos e está em
   reaprendizagem; seis cartões de funções levaram um “Novamente” e foram suspensos
   (`F_D05`, `F_D07`, `F_D08`, `F_D10`, `F_R07`, `F_R10`), além de dois Cloze suspensos
   sem revisão (`F_C04`, `F_C05`). Com uma revisão por cartão, não há amostra para
   diagnosticar domínio; a suspensão pode ter sido decisão de organização. A
   atualização **não reativa** cartões suspensos.

## Decisões por nota

| ID | Decisão | Motivo |
| --- | --- | --- |
| F_R04 | REFORMULAR frente + verso | 3 lapsos. A frente passou a dizer “para todo x > 0”, deixando explícito que a afirmação é universal; o verso traz a tabela de sinais (negativo / zero / positivo). |
| F_R07 | REFORMULAR frente + verso | Ambiguidade real: sem “quaisquer”, a igualdade vale para u = v = 2, e o Errado ficava discutível. Verso com tabela do que pode e não pode ser expandido. |
| F_D02 | REFORMULAR (alvo novo) | Repetia o alvo de P_D04 e P_R08 (taxas sucessivas ≠ soma). Agora testa crescimento exponencial × linear: com a mesma taxa, o 2º reajuste em reais é maior (R$ 20 → R$ 25). Gabarito mantido (Errado). O histórico antigo refere-se ao alvo anterior. |
| F_D04 | REFORMULAR frente + verso | A versão antiga se resolvia só substituindo x = 2, sem usar a redução à mesma base. Agora a frente afirma que a única solução é menor que 4: é preciso resolver (x = 5). Gabarito mantido (Errado). |
| F_D10 | REFORMULAR frente + verso | Redação “o excesso da vazão sobre 12 L/min” trocada por “a diferença entre a vazão e 12 L/min cai pela metade”, e o verso mostra a sequência 28 → 20 → 16 → 14 → 13. |
| P_C01 | REFORMULAR texto + Extra | HTML escapado duas vezes: o cartão mostrava “Vi &amp;gt; 0” literalmente. Corrigido para “Vi > 0”. |
| Demais 41 | APROVAR frente; REFORMULAR verso | Frente correta e clara; verso refeito no padrão visual com Memorize. |

### Redundâncias registradas (sem remoção)

- `P_D04` (+20% e +10% ≠ +30%) e `P_D06` (−20% e −10% ≠ −30%) testam a mesma ideia em
  sentidos opostos; ficam porque o sentido do erro (32% acima, 28% abaixo) é diferente.
- `F_R10` (exponencial passa por (0, 1)) e `F_C04` (log passa por (1, 0)) se completam;
  os versos agora mostram o contraste lado a lado.
- `P_R07` (100% − 35% = 65%) é muito fácil. Fica, mas é candidato a suspensão se o tempo
  de revisão apertar.

## Verificações executadas

- Gabaritos resolvidos de novo pela frente; nas reformulações: F_D02 (80 → 100 → 125),
  F_D04 (x = 5; 8⁶ = 4⁹ = 2¹⁸), F_D10 (13 L/min), F_R07 (contraexemplo u = v = 1).
- `problemas_html` sem alertas em todos os campos; uma única omissão `{{c1::}}` em cada Cloze.
- **Importação testada com o Anki oficial (biblioteca `anki` 26.9.3) numa cópia
  temporária do backup**: 38 notas Básicas e 9 Cloze atualizadas pelo GUID, 0 notas
  novas, 0 conflitos; cartões (IDs, baralho, agenda, suspensões) e as 3.110 linhas do
  histórico idênticos antes e depois; tags iguais; conteúdo no banco igual ao TSV; os 47
  cartões renderizam pelo mecanismo do Anki. Teste na interface gráfica do desktop **não**
  realizado.

## Pertinência e fontes (consulta em 20/11/2026)

- Programa PRF 2021 (edital publicado no DOU de 19/01/2021): funções afim, quadrática,
  exponencial e logarítmica e porcentagem aparecem no conteúdo de Raciocínio
  Lógico-Matemático, segundo reprodução do edital em
  [Nova Concursos](https://www.novaconcursos.com.br/portal/noticias/concurso-prf-prova/).
  O PDF oficial do edital não foi aberto: pertinência por fonte secundária.
- Prova oficial PRF 2021, caderno
  [578_PRF_001_01](https://cdn.cebraspe.org.br/concursos/PRF_21/arquivos/578_PRF_001_01.PDF),
  itens 27–32: modelagem com produto de percentuais (máximo, duas raízes,
  monotonicidade) e acumulado × incremento em sequência. Salvos no banco como
  `cebraspe-2021-prf-027` a `-032`, com gabarito pela resolução própria
  (`nao_verificado`: o gabarito definitivo não foi localizado). Inspiram o novo alvo de
  F_D02 (crescimento e leitura de incrementos).
- Importação por GUID: [manual do Anki, arquivos de texto](https://docs.ankiweb.net/importing/text-files.html)
  — cabeçalho `#guid column`, atualização no lugar, baralho e agenda preservados.

## Coleção substituta (pedido de 20/11/2026)

A pedido, foi gerado também um `.colpkg` em que as 47 notas antigas de Matemática foram
**removidas** e as versões revisadas entraram como **notas novas** (novos GUIDs, cartões
novos, sem histórico nem suspensão), no mesmo baralho e com as mesmas tags. Script:
`fonte/gerar_colecao.py` (biblioteca oficial `anki` 26.9.3, em cópia temporária; o backup
original não é alterado). O pacote fica fora do Git.

Conferência automática no pacote reimportado: 455 notas e 455 cartões; todas as demais
408 notas e seus cartões idênticos campo a campo (IDs, agenda, suspensões, baralho);
baralhos, opções de baralho, tipos de nota, modelos e configuração iguais (exceto
`nextPos`, a posição do próximo cartão novo); as 15 mídias com o mesmo hash; os 47
cartões novos no baralho Matemática, sem revisões, com o conteúdo igual ao dos TSVs e
renderizando pelo mecanismo do Anki. As 3.110 linhas do histórico continuam no banco: o
Anki não apaga o histórico de cartões removidos, ele só deixa de aparecer em algum cartão.
Teste na interface gráfica do desktop não realizado.
