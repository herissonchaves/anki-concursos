"""MODELO de fonte/gerar_lote.py — copie para output/<CONCURSO>_<Tema>/fonte/ e preencha.

Uso, depois de copiado (na raiz do repositório):
  uv run --no-project python -I -X utf8 output/<CONCURSO>_<Tema>/fonte/gerar_lote.py

Este arquivo guarda só o conteúdo. `montar_lote.py` grava TSVs, calibracao_cebraspe.json,
revisao_recuperacao.json e os relatórios gerados (sem prévia, ZIP ou APKG desde a 2.30), resolve as referências do banco pelos `refs` dos
cartões (com ou sem prova oficial) e registra o uso no banco. Sinais do lint pendentes são
impressos com detalhes: corrija o cartão ou justifique em fonte/sinais_resolvidos.json
({"ID|SINAL": "motivo específico"}). Regras: references/roteiro-lote-pdf.md.
"""
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parents[1]
RAIZ = PASTA.parents[1]
if PASTA.parent.name != 'output':
    sys.exit('Copie este modelo para output/<CONCURSO>_<Tema>/fonte/gerar_lote.py antes de rodar.')
sys.path.insert(0, str(RAIZ / 'skills' / 'gerar-revisao-anki' / 'scripts'))
from html_anki import regra, caso, erro, certo, esquema, tabela, fluxo  # noqa: E402,F401
from montar_lote import Lote, rubrica as rub  # noqa: E402

HOJE = 'AAAA-MM-DD'
# Tags (2.33, references/tags.md): ASSUNTO::<tags do card> = Disciplina::Assunto::Topico; PDF só nos cards
# com Pagina_NN; o tipo (Rapida/Desafiadora/Cloze) e as questões dos D entram sozinhos. Nada de concurso,
# Estilo_Cebraspe, Revisao_PDF, Mnemonico ou outra tag genérica: o montador falha.
ASSUNTO = 'Disciplina::Assunto'  # ex.: 'Direito_Administrativo::Atos_Administrativos'
PDF = 'Missao_NN'                # nome curto do PDF; None em lote sem PDF (prints, caderno de erros)

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
  alvo='O que deve ser lembrado.', fx=('lei',), sol='Certo: fundamento conferido na fonte.'),
  # Opcionais (2.24), só quando houver algo real a registrar: alt='leitura concorrente encontrada',
  # rec='por que a frente exige o alvo', fb='confusão que o verso corrige'.
]

CZ = [  # uma omissão {{c1::...}} por nota (várias só em mnemônico, com mn=); cada lacuna coberta por um D
 dict(k='C01', tags='Topico',
  t='Contexto suficiente e o termo central {{c1::omitido}}.',
  b=[regra('Extra: explica o termo omitido.')], m='Memorize do Extra.',
  alvo='Termo a recuperar.', fx=('lei',), cob={'1': ['D01']}),
  # sol é tirada das lacunas; escreva sol= só para equivalentes aceitos. alt/rec/fb: opcionais.
  # Mnemônico (2.33): título "Mnemônico SIGLA:", letras visíveis e o resto de cada termo em c1; a origem
  # (autoral ou link da fonte) vai só no verso, pelo mn=. Exemplo:
  # dict(k='C02', tags='Delegacao',
  #  t='<b>Mnemônico CE-NO-RE:</b><br>Pela Lei 9.784/1999 (art. 13), não podem ser delegados:<br>'
  #    'a matéria de C{{c1::ompetência}} E{{c1::xclusiva}},<br>a edição de atos NO{{c1::rmativos}}<br>'
  #    'e a decisão de RE{{c1::cursos administrativos}}.',
  #  mn=dict(sigla='CE-NO-RE', origem='autoral'),  # ou origem=('encontrado'|'adaptado', 'https://...', 'Nome da fonte')
  #  b=[regra('Explica cada termo da sigla.')], m='CE-NO-RE: o que não se delega.', alvo='...', fx=('lei',),
  #  cob={'*': ['D01']}),  # '*' = a mesma lista para cada lacuna c1 (2.36); ou {'1': [...], '2': [...], ...}
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
  #   (a='disciplina/assunto' opcional: o montador avisa itens Cebraspe C/E do banco desse assunto;
  #    sa=['subassunto'] restringe o aviso ao subtema. Banco suficiente — item Cebraspe C/E oficial do mesmo
  #    subassunto já no banco — dispensa a busca na internet: cite-o em refs com fid='comparada')
  # sem questão de outra banca em refs: obp=OBP
  # Rubrica curta (2.24): os 4 primeiros critérios e linguagem_didatica com evidência; autoria,
  # feedback e utilidade só com observação (autoria='...').
  rb=rub('correção: fonte conferida', 'determinação: condições explícitas', 'operação D: o que exige além de lembrar',
         'comparação: questão e operação (ou PENDENTE: ...)', linguagem_didatica='termos explicados, frente clara')),
]

# Cobertura do PDF por prioridade para o concurso-alvo (obrigatória em revisão de PDF): inventário de
# todo o PDF e de suas questões. Alta/Média: card do lote ou nota da coleção (colecao=[IDs]);
# Baixa: sem card, com motivo. O montador falha se faltar card e põe as tags Pagina_NN nos cards.
# Questões do PDF citadas em `refs` (2.29): viram unidade sozinhas, com os cards que as citam e a prioridade
# herdada do conteúdo. Questão Baixa ou coberta só pela coleção fica declarada em COBERTURA.
QUESTOES_PDF = {'Q02': ('17', Q_OUTRA)}

# Valores comuns aos D (2.29), usados só quando o D não traz a chave; sem `regra`, vale o trecho da 1ª fonte.
PADRAO_D = dict(orig='Caso autoral.')

# Cabeçalho da triagem gerada (2.29); os relatórios triagem/auditoria/economia/fontes saem sozinhos.
RELATORIO = dict(material='Código — título do PDF, N páginas', leitura='extrair_pdf.py, texto limpo, sem OCR',
                 alvo='PRF (prioridade do assunto no banco: ...)', edital='PRF 2021, item ...',
                 colecao='baralho "..." consultado em cópia somente leitura')

COBERTURA = [
 dict(u='U01', pag='5', p='alta', conteudo='Regra X do art. Y', cartoes=['R01', 'C01']),
 dict(u='U02', pag='6-7', p='media', conteudo='Exceção Z', cartoes=['D01']),
 dict(u='U03', pag='8', p='media', conteudo='Definição W', colecao=['1792883029812']),
 dict(u='U04', pag='9', p='baixa', conteudo='Detalhe administrativo V', motivo='Periférico para o cargo; sem questão localizada'),
 dict(u='Q01', pag='17', p='alta', questao=Q_CEB, conteudo='Questão 01 do PDF', cartoes=['D01']),
 dict(u='N01', pag='1-3', conteudo='Capa, apresentação e sumário', excluir='nao_conteudo: capa e sumário'),
]

if __name__ == '__main__':
    Lote(PASTA, '', F, HOJE, [], R, D, CZ, semente=2026, cobertura=COBERTURA, assunto=ASSUNTO, pdf=PDF,
         questoes_pdf=QUESTOES_PDF, padrao_d=PADRAO_D, relatorio=RELATORIO,
         revisor='Claude (assistente de IA) — mesmo agente que redigiu os cartões').gerar()
