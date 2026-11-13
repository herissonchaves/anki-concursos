---
name: automacao-anki-python
description: Extrai PDFs, analisa backups Anki em leitura e exporta TSV ZIP APKG com validação estrutural, mídia e diagnóstico de clareza.
---

# automacao-anki-python — 2.1

Leia `../gerar-revisao-anki/references/nucleo-pedagogico.md` primeiro.

Para melhorar e devolver uma coleção existente, siga
`../gerar-revisao-anki/references/revisao-integral-e-linguagem.md` e use
`scripts/revisar_colpkg.py` com plano integral previamente auditado. Ele opera
em cópia temporária pela biblioteca oficial do Anki, preserva cartões/histórico
e exporta `.colpkg`; não use o exportador de notas novas para substituir coleção.

Leia `references/uso_scripts.md` e use scripts existentes. Extração não equivale a OCR nem leitura visual; análise de backup não mede aprendizagem por si só. Similaridade textual não autoriza remoção. Gere apenas arquivos a partir de cartões semanticamente auditados conforme `../gerar-revisao-anki/references/auditoria-conteudo-gabaritos.md`; uma saída aprovada dos scripts não certifica gabarito. Não fabrique relatórios.

Exportação textual: `scripts/exportar_anki.py`; com imagens locais autênticas e manifesto: `scripts/exportar_anki_visual.py` e protocolo visual. Ambos executam o validador central com `--new`. Consultar `../gerar-revisao-anki/references/matriz_tipos_quantidades.md` e passar os mesmos parâmetros de perfil, justificativa, exceção de equilíbrio e teto tanto ao exportador quanto à revalidação. O padrão exige R/D e equilíbrio separado dos rápidos e dos desafiadores; perfil focado exige justificativa e preserva os demais critérios. Rodar lint de clareza e revisar os avisos semanticamente. Sem modalidade, fornecer TSV vazio; não inventar cartões. Usar caminhos completos dos scripts. Os relatórios precisam conter evidências, mesmo quando concisos.

APKG depende de genanki. Inspecionar integridade ZIP, banco e mídia; declarar importação e renderização no aplicativo como não testadas se não executadas. TSV deve ser importado separadamente no modelo Básico (sem inverso) para C/E e Cloze para lacunas; mapear terceira coluna como Tags e habilitar HTML. Não importar os TSVs e o APKG do mesmo lote. Exportação não altera a coleção. Mudanças na frente podem gerar nova identidade; não prometer atualização segura de notas existentes sem conferir IDs.

## Calibração documental de D novos — 2.7

Antes de exportar lote com D, seguir `../gerar-revisao-anki/references/protocolo-modo-estrategico.md` e `../gerar-revisao-anki/references/registro-calibracao-cebraspe.md`. Incluir `calibracao_cebraspe.json` no diretório de relatórios. Rodar `../gerar-revisao-anki/scripts/validar_calibracao_cebraspe.py DIRETORIO_DO_LOTE` e novamente sobre o ZIP final; qualquer falha impede apresentar a entrega como final. Os exportadores textual e visual bloqueiam D novos sem esse JSON e verificam o registro no diretório e no ZIP final. A rubrica exige também linguagem_didatica com resultado PASSA e evidência específica. Para analisar coleções antigas, usar os fluxos de leitura/revisão; não fabricar registros retroativos nem usar o exportador de notas novas para contornar essa distinção. O validador central antigo não substitui a checagem adicional. Não produzir um pacote apenas para revisar poucos cartões inline. Esta checagem é documental, não semântica.

## Desenvolvimento e regressões — 2.13

Quando a tarefa for testar ou atualizar o plugin, ler `references/testes-desenvolvimento.md`. Isso não acrescenta etapas à criação de poucos cartões inline.

## Barreira de recuperação e resolução do lint — 2.14

Para exportar notas novas, ler `../gerar-revisao-anki/references/registro-revisao-recuperacao.md`. Além da calibração dos D, incluir `revisao_recuperacao.json` nos relatórios: evidências por R/C, hash do lote e decisões específicas para todos os sinais atuais de clareza, também nos D. Os exportadores textual e visual executam `validar_revisao_pedagogica.py` no diretório e no ZIP final. Ausência, cobertura incompleta, revisão obsoleta ou sinal pendente bloqueia a entrega. Não inferir aprovação automaticamente a partir do esquema ou do lint, nem usar fixtures como relatórios reais. Coleções existentes e respostas pequenas inline preservam os fluxos proporcionais; nenhum registro retroativo é fabricado.
