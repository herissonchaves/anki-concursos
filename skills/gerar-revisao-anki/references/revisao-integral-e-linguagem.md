# Revisão integral e linguagem pedagógica

## Escopo e cobertura verificável

Uma solicitação de melhorar toda a coleção autoriza revisar todas as notas e
reescrever as que precisarem, em uma cópia. Não autoriza importar no perfil ativo,
sincronizar, excluir, suspender ou zerar histórico. Entregar todos os cartões
quando o usuário pedir todos; redundância é registrada, não removida silenciosamente.

Inventariar primeiro o banco real, modelos, campos, notas, cartões, vistas Cloze,
histórico e mídia. Em backup moderno, jamais analisar o SQLite de compatibilidade
como se fosse a coleção. Usar o leitor com Zstandard, não pedir outro backup antes
de tentar a capacidade disponível. Python 3.14 tem `compression.zstd`; nas versões
anteriores, usar `zstandard`. Banco desconhecido ou corrompido: falhar claramente.

Manter um registro por ID com conteúdo anterior, decisão, motivo, conteúdo final
e fonte quando pertinente. Cobrir cada nota e cada vista real. Só chamar a revisão
de integral quando todos os itens tiverem sido examinados semanticamente; a
presença de linhas no relatório ou um script sem erros não prova essa leitura.
Trabalhar em blocos, mas concluir o escopo autorizado. Evitar truncar saídas de
leitura: quando isso ocorrer, reler o trecho perdido antes de decidir.

## Linguagem que ensina sem mudar a regra

- Começar pela ação ou relação concreta. Se o termo técnico não é o alvo,
  traduzi-lo em palavras comuns e apresentar o nome técnico depois.
- Conservar condições, exceções, sujeitos, unidades e marco temporal. Linguagem
  simples não autoriza transformar uma regra condicionada em regra absoluta.
- O verso deve mostrar a ligação entre fato e regra, e explicar a correção do
  erro. Citar apenas número de artigo ou repetir o enunciado não ensina.
- Usar um exemplo curto quando resolver a dúvida, sem exigir exemplo em todo
  cartão. Não converter cada verso em aula nem duplicar a explicação numa dica.
- Não inserir comentários sobre a revisão no cartão ("a redação anterior era
  ruim", "mantido por preservar histórico"). Esses comentários vão no relatório.
- Preservar redação boa. Padronizar emojis ou HTML não conta como reescrita
  pedagógica. Não alterar todos os cartões para aumentar a contagem de melhorias.
- Não afirmar que o aluno acertou antes de ele responder. Verso C/E mostra o
  gabarito, não uma mensagem de desempenho presumido.

## Lacunas, siglas e hipóteses concorrentes

Para cada vista, ocultar a resposta e perguntar quais outras respostas corretas
caberiam. Se couberem várias de conceitos distintos, acrescentar contexto ou
reformular. Aceitar equivalentes semânticos legítimos; não exigir uma palavra
exata quando não for o alvo. Evitar pistas por palavra repetida, pedaço visível
de expressão ou sigla que entregue a lacuna.

Quando o alvo é recuperar os termos de um mnemônico, manter visíveis suas letras
ou pistas e explicar cada associação no Extra. Nos demais Clozes, usar a sigla
como apoio no verso quando útil. Se uma reformulação alterar o alvo, registrar a
mudança para que o histórico de revisão seja interpretado no contexto do alvo anterior.

Classificações doutrinárias variam entre autores. Indicar a corrente quando ela
decide o gabarito. Não chamar duas categorias diferentes de "opostas" se não forem
opostos. Em Direito, conferir o alcance da norma/precedente, não extrapolar uma
decisão específica para todo o sistema. Em fontes inacessíveis, tentar outra
fonte primária e declarar limites concretos; não inventar verificação.

## Mídia herdada e identificação visual

Inspecionar mídia já fornecida pelo usuário e preservar seus bytes no backup,
inclusive arquivos não usados. Não atribuir origem, licença ou autoria não
comprovada. Não incluir qualquer mídia privada nos arquivos do plugin.

Uma fotografia isolada não prova propriedades que dependem de contexto ausente,
como a classificação jurídica de uma rua inteira. Quando a imagem não determina
a resposta, tornar os critérios explícitos em texto ou substituir a pergunta por
uma textual. Imagem remota não é mídia incorporada. Não prometer uso offline
enquanto existirem dependências remotas; corrigir ou declarar cada uma.

## Exportação conservadora

Para coleção existente, preferir a biblioteca oficial do Anki em diretório
temporário. Não reconstruir as notas pelo texto da frente com genanki: isso pode
criar novas identidades e perder histórico. `revisar_colpkg.py` aceita um plano
integral já auditado e aplica apenas mudanças de campos, bloqueando diferenças
em IDs, modelo, tags, índices Cloze, cartões e revlog. Não fornece autorização
automática de qualidade pedagógica.

Conferir banco e ZIP, correspondência de conteúdo, notas/cartões, históricos,
agendamento, mídia e hash do original. Renderizar cada cartão pelo mecanismo do
Anki e inspecionar visualmente um conjunto representativo; reportar separadamente
renderização técnica, inspeção visual e teste na interface desktop. Nunca alegar
que abrir pelo backend equivale a testar a interface gráfica.

Um `.colpkg` restaura/substitui a coleção do perfil: avisar isso na entrega e
orientar teste em perfil separado. Não importar nem sincronizar sem pedido.

## Casos de regressão editorial (sintéticos)

1. "Legalidade, igualdade e {{c1::X}} são princípios": lacuna indeterminada;
   reformular para a função específica do princípio alvo.
2. "A letra P de uma sigla significa {{c1::prazo}}": preferir recuperar prazo,
   termo inicial ou consequência relevante, e deixar a sigla como apoio.
3. "O ato admite convalidação. Verso: art. 55": explicar que convalidar é corrigir
   defeito sanável e indicar as condições de preservação do ato.
4. Foto de avenida sem contexto + "qual tipo legal?": insuficiente; descrever os
   acessos, cruzamentos e função, sem inferir a categoria pela aparência.
5. Coleção com c1 e c2: reescrever sem remover nenhum índice; exportação deve
   impedir desaparecimento de cartão ou mudança de histórico.
6. Doutrina divergente: delimitar autor/corrente ou substituir por proposição
   verificável, sem apresentar consenso fictício.
