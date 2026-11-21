"""MODELO de fonte/gerar_lote.py — copie para lotes/<CONCURSO>/<Missao_NN_Tema>/fonte/ e preencha.

Uso, depois de copiado (na raiz do repositório):
  uv run --no-project python -I -X utf8 lotes/<CONCURSO>/<Missao_NN_Tema>/fonte/gerar_lote.py

Este arquivo guarda só o conteúdo. `montar_lote.py` grava TSVs, calibracao_cebraspe.json,
revisao_recuperacao.json e a prévia, resolve as referências do banco pelos `refs` dos
cartões (com ou sem prova oficial) e registra o uso no banco. Sinais do lint pendentes são
impressos com detalhes: corrija o cartão ou justifique em fonte/sinais_resolvidos.json
({"ID|SINAL": "motivo específico"}). Regras: references/roteiro-lote-pdf.md.
"""
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parents[1]
RAIZ = PASTA.parents[2]
if 'lotes' not in PASTA.parts:
    sys.exit('Copie este modelo para lotes/<CONCURSO>/<Missao_NN_Tema>/fonte/gerar_lote.py antes de rodar.')
sys.path.insert(0, str(RAIZ / 'skills' / 'gerar-revisao-anki' / 'scripts'))
from html_anki import regra, caso, erro, certo, esquema, tabela, fluxo  # noqa: E402,F401
from montar_lote import Lote, rubrica as rub  # noqa: E402

HOJE = 'AAAA-MM-DD'
BASE = 'PRF Disciplina Missao_NN'  # tags comuns, sem espaços dentro de cada tag

# IDs do banco referencias/ (referencias.py buscar/mostrar). Basta citá-los em `refs`.
Q_CEB = 'cebraspe-AAAA-orgao-NNN'  # Cebraspe C/E com prova oficial: sustenta fidelidade comparada
Q_OUTRA = 'banca-AAAA-orgao-NNN'   # outra banca (com ou sem prova): inspiração

# Fontes de conteúdo lidas nesta tarefa: chave -> (url, trecho/dispositivo verificado).
F = {
 'lei': ('https://www.planalto.gov.br/...', 'Lei X, art. Y (redação vigente conferida em AAAA-MM-DD)'),
}

# Busca de outras bancas sem sucesso (use em `obp` dos D sem questão de outra banca vinculada).
OBP = 'Buscas em AAAA-MM-DD por ... (bancas, termos, sites): nenhuma questão de outra banca lida por inteiro.'

R = [  # rápidos: um alvo, frase curta; 50% C / 50% E
 dict(k='R01', tags='Topico', g='C', refs=[Q_OUTRA],
  f='Frente: uma afirmação direta, sem pista do gabarito.',
  b=[regra('Regra em linguagem simples, com o termo técnico explicado.')],
  m='Memorize: a ideia central em uma frase.',
  alvo='O que deve ser lembrado.', fx=('lei',),
  sol='Certo: fundamento conferido na fonte.', alt='Leitura concorrente testada e por que não muda o gabarito.',
  rec='Por que a frente exige o alvo sem entregá-lo.', fb='O que o verso explica e qual confusão corrige.'),
]

CZ = [  # uma omissão {{c1::...}} por nota (várias só com a tag Mnemonico); cada lacuna coberta por um D
 dict(k='C01', tags='Topico',
  t='Contexto suficiente e o termo central {{c1::omitido}}.',
  b=[regra('Extra: explica o termo omitido.')], m='Memorize do Extra.',
  alvo='Termo a recuperar.', fx=('lei',), sol='Lacuna: omitido (equivalentes aceitos).',
  alt='Termo concorrente testado.', rec='O contexto determina a resposta sem revelá-la.', fb='O que o Extra ensina.',
  cob={'1': ['D01']}),
]

D = [  # desafiadores: caso curto com dado decisivo; 50% C / 50% E
 dict(k='D01', g='E', tags='Topico', refs=[Q_CEB, Q_OUTRA],
  f='Situação curta com o dado decisivo. Conclusão a julgar.',
  b=[regra('Regra.'), caso('Como o dado decisivo leva à conclusão.'), erro('Onde está o erro.')],
  m='Memorize: a formulação correta.',
  alvo='Alvo.', op='Operação exigida (aplicar, distinguir, inferir).', regra='Dispositivo/regra.',
  dado='Dado decisivo.', solucao='Cadeia de solução; logo Errado.', erro='Erro plausível.',
  conc='Leitura concorrente e como a frente a fecha.', orig='O que foi reconstruído em relação às questões.',
  fx=('lei',), fid='comparada', cmp='Vínculo com a operação da questão Cebraspe.',
  # sem Cebraspe C/E com prova: fid='inspiracao_geral', lim='Buscas feitas e o que faltou.'
  # sem questão de outra banca em refs: obp=OBP
  rb=rub('correção: fonte conferida', 'determinação: condições explícitas', 'operação D: o que exige além de lembrar',
         'comparação: questão e operação (ou PENDENTE: ...)', 'autoria: o que foi reconstruído',
         'feedback: regra, aplicação e erro', 'linguagem: termos explicados, frente clara', 'utilidade: alvo e cobertura')),
]

# Cobertura do PDF por prioridade para o concurso-alvo (obrigatória em revisão de PDF): inventário de
# todo o PDF e de suas questões. Alta/Média: card do lote ou nota da coleção (colecao=[IDs]);
# Baixa: sem card, com motivo. O montador falha se faltar card e põe as tags Pagina_NN nos cards.
COBERTURA = [
 dict(u='U01', pag='5', p='alta', conteudo='Regra X do art. Y', cartoes=['R01', 'C01']),
 dict(u='U02', pag='6-7', p='media', conteudo='Exceção Z', cartoes=['D01']),
 dict(u='U03', pag='8', p='media', conteudo='Definição W', colecao=['1792883029812']),
 dict(u='U04', pag='9', p='baixa', conteudo='Detalhe administrativo V', motivo='Periférico para o cargo; sem questão localizada'),
 dict(u='Q01', pag='17', p='alta', questao=Q_CEB, conteudo='Questão 01 do PDF', cartoes=['D01']),
 dict(u='N01', pag='1-3', conteudo='Capa, apresentação e sumário', excluir='nao_conteudo: capa e sumário'),
]

if __name__ == '__main__':
    Lote(PASTA, BASE, F, HOJE, [], R, D, CZ, semente=2026, cobertura=COBERTURA,
         revisor='Claude (assistente de IA) — mesmo agente que redigiu os cartões',
         titulo_previa='Prévia dos cards — Tema').gerar()
