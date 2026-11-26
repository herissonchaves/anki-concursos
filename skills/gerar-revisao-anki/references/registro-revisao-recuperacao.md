# Revisão de recuperação e resolução de alertas

Aplicar a exportações de notas NOVAS R/D/C. Não exigir registros retroativos para ler ou auditar uma coleção existente. Poucos cartões inline recebem a mesma revisão semântica com síntese proporcional; não criar ZIP/JSON apenas para formalizar uma resposta no chat.

## Antes de aprovar

Resolver a frente novamente, confrontar o trecho realmente lido da fonte, procurar alternativa concorrente e verificar se a recuperação tem utilidade. R: julgar e recuperar o fundamento, sem confundir palpite com domínio. C: ocultar o núcleo de um conceito importante, determinado pelo contexto e sem resposta exposta; aceitar equivalentes legítimos. Conferir se o verso/Extra ensina o alvo. Aplicar `auditoria-conteudo-gabaritos.md`, a triagem de pertinência e os protocolos dos formatos.

Em exportações, usar `relatorios/revisao_recuperacao.json` para guardar evidências de R/C e resolver sinais do lote inteiro. D continua usando `calibracao_cebraspe.json`; não duplicar sua rubrica neste arquivo. O registro não substitui seleção/fontes e a auditoria por ID já existentes: reutilizar seus IDs e evidências, sem relatórios paralelos repetitivos. O `id` técnico abaixo é o arquivo TSV canônico e a linha física; relacioná-lo ao ID editorial no relatório existente.

## Estrutura do arquivo

Objeto JSON UTF-8, `schema_version: 2` (2.37; `1` só em lote legado, sem os campos de evidência), `sha256_lote`, `revisor`, `tipo_revisao` (`autorevisao` ou `independente`), `cartoes` e `sinais` como listas, inclusive quando vazias.

Cada R e C tem exatamente um objeto em `cartoes`:

- `id`: `anki_certo_errado.tsv:N` ou `anki_cloze.tsv:N`, N começando em 1.
- `sha256`: SHA-256 UTF-8 de frente + TAB + verso + TAB + tags, sem quebra final, conforme `fingerprint()` do script.
- `alvo`: conhecimento útil que deve ser recuperado.
- `solucao`: resposta conferida e fundamento concreto, incluindo correção do Errado ou equivalentes da lacuna quando pertinentes.
- `fontes`: lista não vazia de objetos com `url`, `consulta` (AAAA-MM-DD) e `trecho` (trecho breve ou seção/dispositivo/localizador efetivamente lido). Identificar versão/data decisivas. URL bem formada não comprova leitura nem confiabilidade.
- `evidencia_cobranca` (versão 2): `{"questoes": [IDs do banco]}` com as questões reais que cobram o conteúdo, ou `{"nucleo_cargo": "motivo"}` para regra central da atuação do cargo sem questão localizada, ou (2.39) `{"conceito_material": [unidades Baixa]}`; no Cloze (2.40) o campo é opcional e omitido quando não há nenhuma dessas evidências para conceito do material anexado sem questão localizada (`cobertura-pdf.md`). Gerado pelo `montar_lote.py` a partir de `refs`/`nucleo`/`COBERTURA`.
- `cobranca_do_termo` (versão 2, só C, opcional desde a 2.40): como as questões cobram o termo omitido (no mnemônico, a lista ou sequência), a partir de `cobra`.
- `alternativa_concorrente`: alternativa, contraexemplo ou condição testada e por que não muda a solução. Não usar “nenhuma” como aprovação genérica sem análise.
- `recuperacao`: por que a frente exige o alvo útil sem entregá-lo; em Cloze, justificar a parte omitida e sua determinação.
- `desafiadores_por_lacuna` (só C, opcional desde a 2.40): objeto com uma chave para cada lacuna que um D do lote aplica, numerada a partir de `1` pela ordem no campo Texto; o Cloze de memorização sem D associado omite o campo. Cada valor é uma lista não vazia de IDs de desafiadores do mesmo lote, por exemplo `{"1":["anki_certo_errado.tsv:2"],"2":["anki_certo_errado.tsv:2","anki_certo_errado.tsv:4"]}`. Confirmar na revisão que os itens de cada lista realmente testam a lacuna. Um D pode cobrir várias lacunas quando elas sustentam o mesmo julgamento.
- `feedback`: o que o verso/Extra explica e qual confusão corrige.
- `segunda_conferencia: true` e `decisao: "APROVAR"` somente após revisão real. Pendência ou erro exige corrigir, conferir de novo ou retirar o candidato do lote final, registrando a decisão no relatório.

O `sha256_lote` segue `batch_hash()` do script, calculado sobre os hashes dos dois arquivos TSV canônicos. Use as funções existentes em vez de inventar uma serialização equivalente. O comando de diagnóstico abaixo também fornece o hash do lote e os hashes por cartão, sem criar aprovações.

## Alertas: corrigir ou justificar

Executar:

```text
python -X utf8 skills/gerar-revisao-anki/scripts/validar_revisao_pedagogica.py DIRETORIO --listar-sinais
```

O diagnóstico lista `sinal_id`, cartão, código e detalhes. Cada alerta atual exige decisão editorial. Preferir corrigir problemas reais, especialmente resposta exposta, frente dependente de material ausente, feedback insuficiente e repetição sem ganho. Extensão, palavra absoluta ou semelhança lexical podem ser legítimas: não reescrever cartões bons apenas para silenciar o lint.

Se a redação for mantida, registrar em `sinais` um objeto com `sinal_id`, `decisao: "EXCECAO_JUSTIFICADA"` e `motivo` específico, explicando por que o sinal é falso positivo ou por que a construção é pedagogicamente necessária sem entregar o alvo. “Aprovado”, “é bom”, “teste passou” ou justificativa copiada para tudo não são análise válida, mesmo que um campo não vazio passe pelo esquema.

Um problema corrigido precisa desaparecer dos dados atuais; não declarar `CORRIGIDO` enquanto o mesmo sinal permanece. Refazer revisão e hashes após edição, corte, reordenação ou mudança de tags e remover resoluções obsoletas. A revisão cobre sinais também nos D; a análise semântica desses cartões permanece na calibração. Zero sinais não significa qualidade comprovada.

## Validação e limites

```text
python -X utf8 skills/gerar-revisao-anki/scripts/validar_revisao_pedagogica.py DIRETORIO_OU_ZIP
```

O `finalizar_lote.py` executa a barreira na pasta `lote/` (os exportadores avulsos, no diretório e no ZIP). Falta de registro, cobertura incompleta, hash divergente ou sinal pendente bloqueia a exportação. Não há opção CLI de ignorar a revisão. No ZIP visual final, conferir novamente também a calibração quando presente. O script não consulta a internet, não resolve gabaritos, não autentica revisores e não preenche evidências automaticamente. Um registro falso completo pode passar: isso continua sendo uma falha da revisão semântica, não aprovação de conteúdo pelo script.

Preservar 50% Certo/Errado separadamente em R/D, fontes, triagem, autoria e histórico. Conferir a cobertura de todas as lacunas c1 nos novos Clozes. Nenhuma nova proporção nasce deste registro. Não mudar notas antigas ou importar a coleção por implicação.

## Avaliação do gerador

Ao atualizar o plugin, executar a suíte e um piloto editorial com material real, conforme `avaliacao-pedagogica-multidisciplinar.md`: registrar escopo antes de redigir, fontes consultadas, candidatos iniciais e finais, falhas e correções reais. Identificar modelo/assistente e tipo de revisão, separando controles negativos de cartões aprovados. Não importar helpers de `tests/` para preencher relatórios de produção. Sem segundo revisor, declarar autorevisão; sem dados do aluno, aprendizagem e transferência ficam não medidas. Não anunciar excelência consistente ou ganho de nota apenas porque documentos/testes passaram.
