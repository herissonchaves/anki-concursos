#!/usr/bin/env python3
"""Gera os TSVs de ATUALIZAÇÃO dos 47 cartões de Matemática da coleção (backup de 20/11/2026).

Não cria notas novas: cada linha leva o GUID da nota existente, e o Anki (2.1.54+) atualiza
a nota no lugar, mantendo baralho, agendamento e histórico. Fonte dos dados antigos:
base_colecao.json (instantâneo somente leitura do backup). Rode na raiz do repositório:

    python -X utf8 lotes/PRF/Revisao_Matematica_Colecao_2026_11_20/fonte/gerar_atualizacao.py
"""
from __future__ import annotations

import html as _html
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[3]
sys.path.insert(0, str(RAIZ / 'skills' / 'gerar-revisao-anki' / 'scripts'))
from html_anki import (caso, certo, erro, esquema, extra_cloze, fluxo, problemas_html,  # noqa: E402
                       regra, tabela, verso_ce)

LOTE = AQUI.parent / 'lote'

# ------------------------------------------------------------------ frentes corrigidas
FRENTES = {
    # "qualquer x > 0" deixa explícito que a afirmação é universal (3 lapsos seguidos).
    'F_R04': 'Para a &gt; 0 e a ≠ 1, log<sub>a</sub>(x) é positivo para todo x &gt; 0.',
    # Sem "quaisquer", a igualdade é verdadeira para u = v = 2: frente ambígua.
    'F_R07': 'Para quaisquer u, v &gt; 0, log<sub>2</sub>(u + v) = log<sub>2</sub>(u) + log<sub>2</sub>(v).',
    # Alvo antigo (+25% duas vezes ≠ +50%) repetia P_D04 e P_R08; novo alvo: crescimento
    # exponencial gera acréscimos absolutos crescentes (linear × exponencial).
    'F_D02': 'Uma assinatura de R$ 80 sofre dois reajustes sucessivos de 25%, cada um sobre o preço vigente. Em reais, o segundo reajuste é igual ao primeiro.',
    # A versão antiga se resolvia só substituindo x = 2; agora é preciso resolver a equação.
    'F_D04': 'A única solução real da equação 8<sup>x + 1</sup> = 4<sup>2x − 1</sup> é um número menor que 4.',
    # Redação mais clara do modelo ("o excesso da vazão sobre 12" confundia).
    'F_D10': 'A vazão de uma bomba começa em 28 L/min e vai se aproximando de 12 L/min: a cada hora, a diferença entre a vazão e 12 L/min cai pela metade. Pelo modelo, ao fim de quatro horas a vazão será de 12 L/min.',
}
# Correção do HTML duplamente escapado (aparecia "&gt;" literal na tela).
SUBSTITUICOES = {'P_C01': ('&amp;gt;', '&gt;')}

S = lambda t: f'<sup>{t}</sup>'  # noqa: E731
L = lambda b, x: f'log<sub>{b}</sub>({x})'  # noqa: E731

# ------------------------------------------------------------------ versos C/E
VERSOS = {
    # ---------------- Funções exponenciais e logarítmicas
    'F_R03': ('C', [
        regra(f'<b>Imagem</b> é o conjunto das saídas que a função realmente produz. Com base a &gt; 0 e a ≠ 1, a potência a{S("x")} é sempre positiva e nunca chega a zero.'),
        certo(f'Toda saída y &gt; 0 é atingida: basta tomar x = {L("a", "y")}. Já o zero e os negativos nunca aparecem.'),
        esquema(tabela(['x', f'2{S("x")}'], [['−2', '1/4'], ['0', '1'], ['3', '8']])),
    ], 'Exponencial: domínio ℝ e imagem (0, +∞). O gráfico fica sempre acima do eixo x.'),
    'F_D06': ('E', [
        regra('Em equação com logaritmo, fixe primeiro o <b>domínio</b>: todo argumento precisa ser positivo.'),
        caso(f'x − 1 &gt; 0 e x − 4 &gt; 0 ⇒ x &gt; 4. Juntando os logs: (x − 1)(x − 4) = 2{S("2")} = 4 ⇒ x{S("2")} − 5x = 0 ⇒ x = 0 ou x = 5.'),
        erro(f'x = 0 resolve a equação do 2º grau, mas não a original: {L("2", "−1")} não existe. Só x = 5 serve, então há <b>uma</b> solução.'),
        esquema(fluxo(['domínio: x &gt; 4', '(x − 1)(x − 4) = 4', 'x = 0 ou x = 5', 'só 5 serve'], destaque={3})),
    ], 'Em equação logarítmica, ache o domínio antes e descarte as raízes que ficam fora dele.'),
    'F_R02': ('C', [
        regra('Na exponencial, somar 1 ao x multiplica a saída pela base a.'),
        certo(f'Se 0 &lt; a &lt; 1, cada passo multiplica por um número menor que 1 e a saída encolhe: a função é decrescente. Ex.: (1/2){S("x")} vale 1, 1/2, 1/4 para x = 0, 1, 2.'),
        esquema(tabela(['Base', 'Comportamento'], [['a &gt; 1', 'crescente'], ['0 &lt; a &lt; 1', 'decrescente']])),
    ], 'Base maior que 1: a exponencial sobe. Base entre 0 e 1: desce.'),
    'F_D01': ('C', [
        regra(f'Em f(x) = A · b{S("x")}, dividir saídas de x vizinhos dá a base b, e A é o valor em x = 0, onde o gráfico corta o eixo y.'),
        caso(f'b = f(3)/f(2) = 135/45 = 3. Daí A · 3{S("2")} = 45 ⇒ A = 5. Logo f(0) = 5 · 3{S("0")} = <b>5</b>.'),
        certo('Conferência pelo caminho inverso: 5 → 15 → 45 → 135 para x = 0, 1, 2, 3.'),
    ], f'Em A · b{S("x")}: divida saídas vizinhas para achar b; o corte no eixo y é A.'),
    'F_D02': ('E', [
        regra('Reajuste sucessivo incide sobre o preço já reajustado. Por isso o crescimento é <b>exponencial</b> (multiplica por 1,25 a cada etapa), e não linear (somar sempre o mesmo valor).'),
        caso('1º reajuste: 25% de 80 = R$ 20 → R$ 100. 2º reajuste: 25% de 100 = R$ 25 → R$ 125.'),
        erro('O segundo reajuste é de <b>R$ 25</b>, maior que o primeiro (R$ 20): a mesma taxa age sobre uma base maior.'),
        esquema(tabela(['Etapa', 'Base', 'Reajuste', 'Preço'], [['1º', '80', '20', '100'], ['2º', '100', '25', '125']])),
    ], 'Taxa percentual constante gera acréscimos em reais cada vez maiores: é crescimento exponencial, não linear.'),
    'F_R05': ('E', [
        regra('Logaritmo de base entre 0 e 1 é decrescente; de base maior que 1, crescente.'),
        erro(f'Com base 1/3, o gráfico <b>desce</b> da esquerda para a direita: {L("1/3", "1/3")} = 1 e {L("1/3", "1")} = 0. O x aumentou e a saída diminuiu.'),
        esquema(tabela(['Base', f'a{S("x")}', f'{L("a", "x")}'], [['a &gt; 1', 'sobe', 'sobe'], ['0 &lt; a &lt; 1', 'desce', 'desce']])),
    ], 'Exponencial e logaritmo de mesma base têm o mesmo sentido: base maior que 1 sobe; base entre 0 e 1 desce.'),
    'F_R04': ('E', [
        regra('A condição x &gt; 0 vale para o <b>argumento</b> (domínio). A saída do logaritmo pode ser negativa, zero ou positiva: a imagem é ℝ.'),
        erro(f'Com a = 2: {L("2", "1/2")} = −1, {L("2", "1")} = 0 e {L("2", "8")} = 3. Basta um x entre 0 e 1 para a saída ser negativa.'),
        esquema(tabela(['x (base a &gt; 1)', f'sinal de {L("a", "x")}'], [['0 &lt; x &lt; 1', 'negativo'], ['x = 1', 'zero'], ['x &gt; 1', 'positivo']]) + 'Com base entre 0 e 1, os sinais se invertem.'),
    ], 'Positivo tem de ser o argumento, não o resultado: o logaritmo pode dar qualquer número real.'),
    'F_D05': ('C', [
        regra(f'Em {L("b", "x − 3")}, o argumento x − 3 manda: a assíntota vertical fica onde ele vale 0, e o corte no eixo x onde ele vale 1, porque o log de 1 é 0 em qualquer base.'),
        caso('x − 3 = 0 ⇒ assíntota em x = 3. x − 3 = 1 ⇒ corte em x = 4. Distância: 4 − 3 = <b>1 unidade</b>.'),
        certo('A base 1/2 só decide se a curva sobe ou desce; não muda a posição da assíntota nem do corte.'),
        esquema(tabela(['Argumento x − 3', 'x', 'No gráfico'], [['0', '3', 'assíntota vertical'], ['1', '4', 'corta o eixo x']])),
    ], 'Logaritmo: argumento 0 dá a assíntota; argumento 1 dá o corte no eixo x. A base não muda esses pontos.'),
    'F_R08': ('C', [
        regra(f'{L("a", "b")} é o expoente que leva a base a até b.'),
        certo(f'Como a{S("1")} = a, o expoente é 1. Ex.: {L("5", "5")} = 1 e {L("10", "10")} = 1.'),
        esquema(tabela(['Valor', 'Por quê'], [[f'{L("a", "1")} = 0', f'a{S("0")} = 1'], [f'{L("a", "a")} = 1', f'a{S("1")} = a']])),
    ], 'Log da própria base vale 1; log de 1 vale 0.'),
    'F_D03': ('C', [
        regra('Para tirar t do expoente, deixe primeiro a exponencial sozinha; depois aplique ln dos dois lados, pois ln desfaz e.'),
        caso(f'40 = 20 + 60 · e{S("−t/3")} ⇒ e{S("−t/3")} = 20/60 = 1/3 ⇒ −t/3 = ln(1/3) = −ln 3 ⇒ t = <b>3 · ln 3</b> (cerca de 3,3 s).'),
        certo(f'Conferência: e{S("−ln 3")} = 1/3, e 20 + 60 · (1/3) = 40.'),
        esquema(fluxo([f'isolar e{S("−t/3")} = 1/3', 'aplicar ln', '−t/3 = −ln 3', 't = 3 · ln 3'], destaque={3})),
    ], 'Modelo com e: isole a exponencial, aplique ln e use ln(1/k) = −ln k.'),
    'F_D07': ('C', [
        regra(f'Passar de logaritmo para potência: {L("b", "N")} = k significa N = b{S("k")}. Expoente negativo indica fração.'),
        caso(f'U/V = 3{S("−2")} = 1/9 ⇒ <b>V = 9U</b>.'),
        certo(f'Log negativo ⇒ razão U/V menor que 1 ⇒ U é a medida menor. Ex.: U = 2 e V = 18 dão U/V = 1/9 e {L("3", "1/9")} = −2.'),
    ], f'{L("b", "N")} = k significa N = b{S("k")}; log negativo indica que N é uma fração menor que 1.'),
    'F_R01': ('E', [
        regra('Base da exponencial: a &gt; 0 e a ≠ 1.'),
        erro(f'Com a = 1, 1{S("x")} = 1 para todo x: o gráfico é uma reta horizontal, sem crescer nem decrescer. Isso é função constante, não exponencial.'),
        esquema(tabela(['Base', 'Problema'], [['a = 1', 'função constante'], ['a ≤ 0', f'potências indefinidas, como (−2){S("1/2")} ou 0{S("−1")}']])),
    ], 'Exponencial exige base positiva e diferente de 1.'),
    'F_R06': ('C', [
        regra('Com base válida e argumentos positivos, o logaritmo é <b>injetor</b>: saídas iguais só vêm de entradas iguais.'),
        certo(f'Se {L("a", "u")} = {L("a", "v")} = k, então u = a{S("k")} e v = a{S("k")}, logo u = v. É isso que permite cortar o log em {L("2", "x")} = {L("2", "7")} ⇒ x = 7.'),
    ], 'Mesma base e logs iguais ⇒ argumentos iguais, desde que positivos.'),
    'F_D04': ('E', [
        regra('Para comparar potências de bases diferentes, escreva tudo na mesma base e iguale os expoentes.'),
        caso(f'8 = 2{S("3")} e 4 = 2{S("2")} ⇒ 2{S("3x + 3")} = 2{S("4x − 2")} ⇒ 3x + 3 = 4x − 2 ⇒ x = <b>5</b>.'),
        erro(f'A solução é 5, que não é menor que 4. Conferência: 8{S("6")} = 2{S("18")} e 4{S("9")} = 2{S("18")}.'),
        esquema(fluxo([f'8 = 2{S("3")}, 4 = 2{S("2")}', '3(x + 1) = 2(2x − 1)', 'x = 5'], destaque={2})),
    ], 'Exponencial com bases diferentes: reduza à mesma base e iguale os expoentes.'),
    'F_D10': ('E', [
        regra('Quando a diferença até um nível cai pela metade a cada etapa, ela diminui sem nunca zerar: o nível é só um limite de aproximação (assíntota).'),
        caso(f'Diferença: 16 → 8 → 4 → 2 → 1 L/min. Após 4 h, a vazão é 12 + 1 = <b>13 L/min</b>. Fórmula: V(t) = 12 + 16 · (1/2){S("t")}.'),
        erro('Ao fim de quatro horas a vazão é 13 L/min, não 12. Nenhum número finito de horas leva a diferença a zero.'),
        esquema(fluxo(['28', '20', '16', '14', '13'], destaque={4}) + 'Vazão (L/min) no início e ao fim de cada hora.'),
    ], 'Cair pela metade nunca chega a zero: o valor se aproxima do nível-limite sem alcançá-lo.'),
    'F_R09': ('E', [
        regra(f'Expoente negativo significa inverter: a{S("−n")} = 1/a{S("n")}.'),
        erro(f'Com base positiva, a potência é sempre positiva. O sinal do expoente só decide se ela fica acima ou abaixo de 1 (com base maior que 1). Ex.: 3{S("−2")} = 1/9 &gt; 0.'),
    ], f'Expoente negativo inverte, não troca o sinal: 3{S("−2")} = 1/9.'),
    'F_D08': ('E', [
        regra(f'A inversa troca entrada e saída: (p, q) no gráfico de f vira (q, p) no gráfico da inversa. A inversa de 2{S("x")} é {L("2", "x")}, na mesma base.'),
        caso(f'(3, 8) está em 2{S("x")}, pois 2{S("3")} = 8. Trocado: (8, 3). Para estar em {L("4", "x")}, seria preciso 4{S("3")} = 8.'),
        erro(f'4{S("3")} = 64, e {L("4", "8")} = 1,5 (pois 4{S("1,5")} = 8). O ponto (8, 3) está em <b>{L("2", "x")}</b>, não em {L("4", "x")}.'),
    ], f'A inversa de a{S("x")} é {L("a", "x")}, com a mesma base; trocar coordenadas só funciona entre funções inversas.'),
    'F_R10': ('C', [
        regra('Ponto do eixo y tem x = 0.'),
        certo(f'a{S("0")} = 1 para qualquer base válida, então toda exponencial a{S("x")} passa por (0, 1).'),
        esquema(tabela(['Função', 'Ponto fixo'], [[f'a{S("x")}', '(0, 1): corta o eixo y'], [L('a', 'x'), '(1, 0): corta o eixo x']])),
    ], f'Exponencial a{S("x")} corta o eixo y em (0, 1); {L("a", "x")} corta o eixo x em (1, 0).'),
    'F_D09': ('C', [
        regra(f'Diferença de logs de mesma base vira log do quociente: {L("a", "u")} − {L("a", "v")} = {L("a", "u/v")}.'),
        caso(f'{L("2", "12x/3")} = {L("2", "4x")} = 5 ⇒ 4x = 2{S("5")} = 32 ⇒ x = <b>8</b>.'),
        certo(f'x = 8 está no domínio (x &gt; 0). Conferência: {L("2", "96")} − {L("2", "3")} = {L("2", "32")} = 5.'),
    ], 'Subtração de logs vira log da divisão; depois passe para a forma de potência.'),
    'F_R07': ('E', [
        regra('Soma de logaritmos corresponde ao log do <b>produto</b>: log u + log v = log(u · v). Não existe regra que abra o log de uma soma.'),
        erro(f'Contraexemplo: u = v = 1 ⇒ {L("2", "2")} = 1, mas {L("2", "1")} + {L("2", "1")} = 0. A igualdade só acontece em casos especiais (quando u + v = u · v, como u = v = 2), não para quaisquer valores.'),
        esquema(tabela(['Expressão', 'Pode expandir?'], [['log(u · v)', 'sim: log u + log v'], ['log(u/v)', 'sim: log u − log v'], ['log(u + v)', 'não']])),
    ], 'Log transforma produto em soma; log(u + v) não se abre em log u + log v.'),
    # ---------------- Porcentagem
    'P_R03': ('C', [
        regra('Porcentagem de uma parte = parte ÷ total × 100.'),
        certo('Ex.: 45 de 180 ⇒ 45/180 = 0,25 = 25%. A divisão dá a taxa decimal; o × 100 só a escreve em %.'),
    ], 'Parte sobre total, vezes 100.'),
    'P_R08': ('E', [
        regra('Em variações sucessivas, cada taxa age sobre o valor já atualizado; por isso os fatores (1 + i para aumento, 1 − i para redução) se <b>multiplicam</b>.'),
        erro('Somar as taxas ignora que a base muda. Ex.: +10% e +10% ⇒ 1,1 × 1,1 = 1,21 ⇒ +21%, não +20%.'),
        esquema(fluxo(['1,10 × 1,10', '= 1,21', '− 1', '+21%'], destaque={3})),
    ], 'Taxa acumulada = produto dos fatores − 1; taxas sucessivas não se somam.'),
    'P_R07': ('C', [
        regra('O total vale 100%. Gastar uma parte deixa o complemento.'),
        certo('100% − 35% = 65%. Ex.: de R$ 200, gasta R$ 70 e restam R$ 130, que são 65% de 200.'),
    ], 'Resto = 100% − parte gasta, quando as duas se referem ao mesmo total.'),
    'P_R06': ('C', [
        regra('Taxa de variação = (final − inicial)/inicial. O sinal indica o sentido; o valor absoluto, o tamanho.'),
        certo('−0,08 = −8%: o valor caiu 8% do inicial. Ex.: 250 → 230 dá −20/250 = −0,08.'),
    ], 'Taxa negativa é redução: −0,08 significa queda de 8% sobre o valor inicial.'),
    'P_D06': ('E', [
        regra('Descontos sucessivos se multiplicam: o segundo incide sobre o preço já reduzido.'),
        caso('A: 1.000 × 0,80 × 0,90 = R$ 720 (desconto total de 28%). B: 1.000 × 0,70 = R$ 700.'),
        erro('Os preços são diferentes: a loja B sai <b>R$ 20 mais barata</b>. Descontos de 20% e 10% equivalem a 28%, não a 30%.'),
        esquema(tabela(['Loja', 'Fator', 'Preço'], [['A', '0,80 × 0,90 = 0,72', 'R$ 720'], ['B', '0,70', 'R$ 700']])),
    ], 'Descontos sucessivos dão menos que a soma das taxas: 20% e 10% sucessivos equivalem a 28%.'),
    'P_D12': ('C', [
        regra('Taxas sobre a <b>mesma base</b> podem ser somadas. Só não se somam quando a segunda incide sobre o valor já alterado.'),
        caso('As duas taxas usam R$ 2.000: 20% = R$ 400 e 15% = R$ 300. Gastos: R$ 700. Saldo: R$ 1.300.'),
        certo('O texto diz “da quantia inicial”. Se os 15% fossem sobre o que restou (R$ 1.600), o gasto seria R$ 240 e o saldo, R$ 1.360.'),
    ], 'Antes de somar porcentagens, confira a base: com a mesma base, pode somar.'),
    'P_D01': ('C', [
        regra('Porcentagem de porcentagem: a segunda taxa incide só sobre o subgrupo, e as taxas se multiplicam.'),
        caso('600 × 0,20 = 120 caminhões; 120 × 0,15 = <b>18</b>.'),
        certo('Em relação a todos os veículos: 0,20 × 0,15 = 0,03 = 3%, e 3% de 600 = 18.'),
        esquema(fluxo(['600 veículos', '20% ⇒ 120 caminhões', '15% ⇒ 18 irregulares'], destaque={2})),
    ], '“x% dos caminhões” usa os caminhões como base: multiplique as taxas.'),
    'P_D09': ('C', [
        regra(f'Reajustes sucessivos de 10% multiplicam o preço por 1,10 a cada vez: P(n) = 1.000 × 1,10{S("n")}.'),
        caso('2º reajuste: R$ 1.210, ainda dentro do limite. 3º reajuste: <b>R$ 1.331</b>, acima de R$ 1.300.'),
        certo('Quem soma as taxas (3 × 10% = 30% ⇒ R$ 1.300) acha que o 3º reajuste apenas atinge o limite. O produto dos fatores mostra que ele ultrapassa.'),
        esquema(tabela(['Reajuste', 'Preço'], [['1º', 'R$ 1.100'], ['2º', 'R$ 1.210'], ['3º', 'R$ 1.331']])),
    ], 'Três reajustes sucessivos de 10% somam 33,1%, não 30%.'),
    'P_D10': ('E', [
        regra('Para juntar grupos de tamanhos diferentes, some as quantidades e divida pelo total (média ponderada). A média simples das taxas só vale com grupos iguais.'),
        caso('20 + 120 = 140 caminhões em 400 veículos ⇒ 140/400 = <b>35%</b>.'),
        erro('O conjunto tem 35% de caminhões, não 30%: o 2º turno, com 300 veículos, pesa mais.'),
        esquema(tabela(['Turno', 'Veículos', 'Caminhões'], [['1º', '100', '20 (20%)'], ['2º', '300', '120 (40%)'], ['Total', '400', '140 (35%)']])),
    ], 'Taxa do conjunto = total da parte ÷ total geral; não tire média simples de taxas de grupos desiguais.'),
    'P_R04': ('E', [
        regra('Porcentagem compara com uma referência. Passar de 100% significa ser maior que a referência.'),
        erro('300 é 150% de 200 (300/200 = 1,5). O limite de 100% só vale para uma parte de um todo.'),
    ], 'Uma quantidade pode valer mais de 100% de outra; o teto de 100% vale só para parte de um todo.'),
    'P_D08': ('E', [
        regra('Trabalhe com fatores sobre o custo C: aumento de 30% ⇒ × 1,30; desconto de 20% ⇒ × 0,80.'),
        caso('Preço final = 1,30 × 0,80 × C = 1,04C. Lucro = 1,04C − C = 0,04C. Com custo 100: 100 → 130 → 104.'),
        erro('O lucro é de <b>4% do custo</b>, não 10%. O desconto de 20% incide sobre o preço já aumentado, maior que o custo.'),
        esquema(fluxo(['C', '× 1,30 ⇒ 1,30C', '× 0,80 ⇒ 1,04C'], destaque={2})),
    ], '+30% seguido de −20% dá fator 1,04: lucro de 4%, não de 10%.'),
    'P_D02': ('E', [
        regra('Taxa é parte ÷ total. Comparar taxas não diz nada sobre quantidades se os totais forem diferentes.'),
        caso('Exemplo compatível com a frente: A aborda 100 ⇒ 30 irregulares; B aborda 200 ⇒ 40 irregulares.'),
        erro('A conclusão não segue: sem os totais, não se sabe qual posto teve mais veículos irregulares. B pode ter mais, mesmo com taxa menor.'),
    ], 'Taxa maior não significa quantidade maior quando as bases são diferentes.'),
    'P_D04': ('E', [
        regra('Aumentos sucessivos: multiplique os fatores. O segundo aumento incide também sobre o primeiro acréscimo.'),
        caso('400 × 1,20 = 480; 480 × 1,10 = <b>R$ 528</b> (fator 1,32 = +32%). Com aumento único de 30%: 400 × 1,30 = R$ 520.'),
        erro('Os preços diferem em R$ 8: os aumentos sucessivos equivalem a 32%, não a 30%.'),
    ], '20% e 10% sucessivos: 1,2 × 1,1 = 1,32, ou seja, +32%, mais que 30%.'),
    'P_R05': ('E', [
        regra('Variação percentual = (final − inicial)/inicial: a base é sempre o valor de partida.'),
        erro('Dividir pelo final mede outra coisa. Ex.: 80 → 100 dá (100 − 80)/80 = 25% de aumento; dividir por 100 daria 20%, que é a queda de 100 para 80.'),
    ], 'Variação percentual: diferença dividida pelo valor inicial.'),
    'P_R02': ('E', [
        regra('Para passar de % para decimal, divida por 100 (vírgula duas casas para a esquerda).'),
        erro('0,5% = 0,5/100 = <b>0,005</b>. O decimal 0,05 equivale a 5%.'),
        esquema(tabela(['%', 'Decimal'], [['50%', '0,5'], ['5%', '0,05'], ['0,5%', '0,005']])),
    ], '0,5% = 0,005; 5% = 0,05.'),
    'P_D07': ('C', [
        regra('Para recompor um valor depois de uma perda, a base do percentual é o que restou, não o valor original.'),
        caso('Restam 800 × 0,80 = 640 L. Faltam 160 L. 160/640 = 0,25 = <b>25%</b>.'),
        certo('Perder 20% exige ganhar 25% para voltar, porque a base da recuperação é menor. Conferência: 640 × 1,25 = 800.'),
    ], 'Recuperar uma perda de 20% exige alta de 25%, porque a base ficou menor.'),
    'P_D05': ('C', [
        regra('Variações sucessivas: multiplique os fatores (0,88 para −12%; 1,25 para +25%).'),
        caso('0,88 × 1,25 = <b>1,10</b> ⇒ +10% sobre o valor anterior à redução. Com base 100: 100 → 88 → 110.'),
        certo('Somar as taxas daria +13%, o que estaria errado; vale o produto dos fatores.'),
    ], 'Fator total = produto dos fatores: 0,88 × 1,25 = 1,10, ou seja, +10%.'),
    'P_D11': ('E', [
        regra('A mudança de uma taxa pode ser medida de dois jeitos: diferença simples, em <b>pontos percentuais</b> (p.p.), ou variação relativa, em %.'),
        caso('25% − 20% = 5 p.p. Variação relativa: 5/20 = 0,25 = 25%.'),
        erro('O aumento relativo foi de <b>25%</b>; o número 5 é a diferença em pontos percentuais.'),
        esquema(tabela(['Medida', 'Cálculo', 'Resultado'], [['Diferença', '25 − 20', '5 p.p.'], ['Variação relativa', '5 ÷ 20', '25%']])),
    ], 'De 20% para 25%: +5 pontos percentuais, que é um aumento relativo de 25%.'),
}

# ------------------------------------------------------------------ extras Cloze
EXTRAS = {
    'F_C04': ([
        regra(f'No eixo x a saída vale 0. {L("a", "x")} = 0 exige a{S("0")} = x, isto é, x = 1, em qualquer base válida.'),
        esquema(tabela(['Função', 'Ponto fixo'], [[f'a{S("x")}', '(0, 1)'], [L('a', 'x'), '(1, 0)']])),
    ], f'{L("a", "1")} = 0: todo logaritmo corta o eixo x em (1, 0).'),
    'F_C05': ([
        regra(f'Logaritmo é expoente. Multiplicar potências de mesma base soma os expoentes: a{S("m")} · a{S("n")} = a{S("m + n")}. Por isso o log do produto é a soma dos logs.'),
        caso(f'{L("2", "8 · 4")} = {L("2", "32")} = 5 = 3 + 2.', '🔎 Exemplo'),
    ], 'Log do produto = soma dos logs.'),
    'F_C06': ([
        regra(f'Dividir potências de mesma base subtrai os expoentes: a{S("m")}/a{S("n")} = a{S("m − n")}. A ordem segue a fração: numerador menos denominador.'),
        caso(f'{L("3", "81/9")} = {L("3", "9")} = 2 = 4 − 2.', '🔎 Exemplo'),
    ], 'Log do quociente = log do numerador − log do denominador.'),
    'F_C07': ([
        regra(f'Se u = a{S("m")}, então u{S("k")} = a{S("mk")}: o expoente k desce e multiplica o logaritmo.'),
        caso(f'{L("2", "8" + S("4"))} = 4 · {L("2", "8")} = 4 · 3 = 12 (de fato, 8{S("4")} = 4096 = 2{S("12")}).', '🔎 Exemplo'),
    ], f'Expoente dentro do log sai multiplicando: log(u{S("k")}) = k · log u.'),
    'F_C08': ([
        regra(f'ln é o logaritmo natural, de base e (número de Euler, cerca de 2,718): ln(x) = {L("e", "x")}. Log sem base escrita costuma indicar base 10.'),
        caso(f'ln(e) = 1, ln(1) = 0 e ln(e{S("t")}) = t para qualquer t real.', '🔎 Exemplo'),
    ], f'ln é o log na base e; ln desfaz e{S("x")}.'),
    'P_C01': ([
        regra('A variação é comparada à base inicial: diferença dividida pelo valor de partida. Forma equivalente: Vf/Vi − 1.'),
        caso('80 → 100: i = 20/80 = 0,25 = 25%. 100 → 80: i = −20/100 = −0,20 = −20%.', '🔎 Exemplo'),
    ], 'i = (Vf − Vi)/Vi: diferença sobre o valor inicial.'),
    'P_C02': ([
        regra('Fator de aumento = 1 (o valor inteiro) + i (o acréscimo).'),
        caso('+12% ⇒ 1,12; +5% ⇒ 1,05; +150% ⇒ 2,5.', '🔎 Exemplo'),
    ], 'Aumento de i: multiplique por 1 + i.'),
    'P_C03': ([
        regra('Fator de desconto = 1 (o inteiro) − i (a parte retirada).'),
        caso('−12% ⇒ 0,88 (permanecem 88%); −35% ⇒ 0,65.', '🔎 Exemplo'),
    ], 'Desconto de i: multiplique por 1 − i.'),
    'P_C04': ([
        regra('Subtrair duas taxas dá a diferença em pontos percentuais (p.p.). A variação relativa divide essa diferença pela taxa inicial. Aceite a abreviação p.p.'),
        caso('8% → 11%: +3 p.p.; variação relativa 3/8 = 37,5%.', '🔎 Exemplo'),
    ], 'Diferença entre taxas: pontos percentuais (p.p.); variação relativa: em %.'),
}

GAB_RE = re.compile(r'^(✅ Certo|❌ Errado)<br><br>')
CABECALHO = '#separator:tab\n#html:true\n#guid column:1\n#tags column:4\n#notetype:{nt}\n#deck:Matemática\n'


def _campo(texto: str) -> str:
    if '\t' in texto or '\n' in texto:
        raise ValueError('TAB/quebra de linha no campo')
    if texto.startswith('"'):
        raise ValueError('campo começa com aspas: o leitor CSV do Anki o trataria como citado')
    return texto


def gerar() -> list[dict]:
    base = json.loads((AQUI / 'base_colecao.json').read_text(encoding='utf-8'))
    linhas = {'Basic': [], 'Cloze': []}
    registro = []
    for nota in base:
        nid, nt = nota['id'], nota['notetype']
        campo1 = FRENTES.get(nid, nota['campo1'])
        if nid in SUBSTITUICOES:
            velho, novo = SUBSTITUICOES[nid]
            assert velho in campo1, nid
            campo1 = campo1.replace(velho, novo)
        if nt == 'Basic':
            gab, blocos, resumo = VERSOS[nid]
            antigo = GAB_RE.match(nota['campo2_antigo']).group(1)
            assert (gab == 'C') == antigo.startswith('✅'), f'{nid}: gabarito trocado'
            campo2 = verso_ce(gab, blocos, resumo)
        else:
            assert len(re.findall(r'\{\{c\d+::', campo1)) == 1 and '{{c1::' in campo1, nid
            blocos, resumo = EXTRAS[nid]
            campo2 = extra_cloze(blocos, resumo)
        for c in (campo1, campo2):
            p = problemas_html(c)
            if p:
                raise ValueError(f'{nid}: {p}')
        if nota['guid'].startswith('#'):
            raise ValueError(f'{nid}: GUID iniciado por # seria lido como cabeçalho')
        linhas[nt].append('\t'.join(_campo(x) for x in (nota['guid'], campo1, campo2, nota['tags'])))
        registro.append(dict(id=nid, frente_alterada=campo1 != nota['campo1'], frente=campo1, verso=campo2))
    assert set(VERSOS) | set(EXTRAS) == {n['id'] for n in base}
    nomes = {'Basic': 'atualizar_certo_errado.tsv', 'Cloze': 'atualizar_cloze.tsv'}
    for nt, ls in linhas.items():
        (LOTE / nomes[nt]).write_text(CABECALHO.format(nt=nt) + '\n'.join(ls) + '\n', encoding='utf-8', newline='\n')
    return registro


def previa(registro: list[dict]) -> None:
    def esc(t):  # o Anki mostra HTML; na prévia, só tiramos a marcação Cloze
        return re.sub(r'\{\{c1::(.*?)\}\}', r'<span style="background:rgba(30,136,229,.25);padding:0 3px;">[\1]</span>', t)
    cards = ''.join(
        f'<section style="border:1px solid rgba(127,127,127,.4);border-radius:8px;padding:12px;margin:14px 0;">'
        f'<div style="font-size:.8em;opacity:.7;">{_html.escape(r["id"])}{" · frente revista" if r["frente_alterada"] else ""}</div>'
        f'<div style="text-align:center;margin:8px 0 12px;">{esc(r["frente"])}</div><hr>{r["verso"]}</section>'
        for r in registro)
    pagina = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
              '<title>Prévia — Matemática revisada</title></head>'
              '<body style="font-family:Arial,sans-serif;max-width:640px;margin:auto;padding:0 16px;">'
              f'<h1 style="font-size:1.2em;">Matemática — 47 cartões revisados</h1>{cards}</body></html>')
    (AQUI.parent / 'previa_cards.html').write_text(pagina, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    reg = gerar()
    previa(reg)
    print(f'{len(reg)} notas; frentes revistas: {[r["id"] for r in reg if r["frente_alterada"]]}')
