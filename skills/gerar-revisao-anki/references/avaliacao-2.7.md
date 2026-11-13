# Verificações da versão 2.7.0

Data: 03/11/2026. Revisão pelo próprio agente responsável pela atualização; não é avaliação independente ou experimento com alunos.

## Mudanças verificadas

- Modo estratégico explicitamente mapeado para D.
- Protocolo de referência real → operação → construção autoral → solução → revisão, integrado aos fluxos de geração, auditoria, melhoria e caderno de erros.
- Atlas inicial de Direito/Trânsito, Física, Lógica/Matemática e Informática, preservando a especialização de Português.
- Rubrica de sete dimensões e roteiro de avaliação de saídas com referências reservadas para comparação.
- Registro documental por D com referência, análise, decisão e hash de frente/verso/tags; verificador separado, sem alegação de julgamento semântico.
- Exportador preserva e verifica o registro quando fornecido. Compatibilidade com pacotes anteriores sem JSON mantida; o fluxo de D novos exige sua inclusão e checagem.

## Testes executados

14 testes novos cobrem completude, ausência do registro, cobertura, IDs/linhas duplicados, revisão pendente, hash desatualizado, gabarito declarado divergente, referência desconhecida/anulada, inspiração geral com limitação, rubrica reprovada, dados malformados, exportação/preservação no ZIP e dois limites semânticos conhecidos.

A suíte completa disponível executou 83 testes com sucesso, 27 subtestes e 5 pulados por dependências opcionais. Após a integração final da checagem no exportador, a bateria relevante de calibração e automação executou 36 testes com sucesso e 5 pulados. As tentativas iniciais sem pytest e com codificação Windows inadequada falharam por ambiente; o rerun usou ambiente temporário com pytest e UTF-8. Não se alteraram testes antigos para ocultar falhas.

Casos sintéticos: definição rotulada D e inferência falsa com metadados completos continuam podendo passar pela checagem documental. Esse resultado é esperado e está testado. A solução exige a revisão semântica da rubrica, não um novo selo automático.

## Inspeção editorial E01–E12

Foram conferidos os estímulos pré-definidos de `avaliacao-modo-estrategico.md` e sua compatibilidade com o protocolo. E01 exige reclassificação; E02 rejeição do gabarito; E03 tem inferência válida; E04 exige análise do nexo; E05 distingue componente e vetor; E06 delimita energia mecânica; E07 usa regra fictícia bicondicional; E08 distingue condição de acesso e login; E09 controla extrapolação; E10 exige reconstrução autoral; E11 não aprova referência anulada; E12 não permite substituir revisão por metadados.

Na revisão, E06 foi delimitado a energia mecânica para evitar confusão com outras conservações, e E07 passou a explicitar bicondicional para não transformar condição suficiente em necessária. Isso é inspeção editorial de casos conhecidos, não desempenho medido do gerador sobre novos lotes.

## Limites

Não houve importação em perfil Anki, revisão de coleção do usuário, teste psicométrico, avaliação cega ou medição de ganho de aprendizagem. Não foi demonstrada fidelidade universal do gerador. O protocolo define como avaliar novas saídas; uma versão salva do plugin não prova que toda conversa futura seguirá corretamente as instruções. Referências históricas registradas no atlas precisam de conferência pertinente em cada nova tarefa.
