---
name: automacao-anki-python
description: Extrai PDFs, consulta a coleção viva do Anki e backups em leitura e exporta TSV ZIP APKG com validação estrutural, mídia e diagnóstico de clareza.
---

# automacao-anki-python

Leia `../gerar-revisao-anki/references/nucleo-pedagogico.md` primeiro.

Para melhorar e devolver uma coleção existente, siga
`../gerar-revisao-anki/references/revisao-integral-e-linguagem.md` e use
`scripts/revisar_colpkg.py` com plano integral previamente auditado. Ele opera
em cópia temporária pela biblioteca oficial do Anki, preserva cartões/histórico
e exporta `.colpkg`; não use o exportador de notas novas para substituir coleção.

**Destino dos arquivos:** o lote inteiro (gerador, TSVs, relatórios, ZIP, APKG, `.colpkg`, TSVs
de atualização) fica em `output/<CONCURSO>_<Tema>/` na raiz do repositório, fora do Git; o
usuário apaga a pasta após importar. Regra completa em [GIT_E_ARQUIVOS.md](../../GIT_E_ARQUIVOS.md).

Leia `references/uso_scripts.md` e use scripts existentes. Extração não equivale a OCR nem leitura visual; análise de backup não mede aprendizagem por si só. Similaridade textual não autoriza remoção. Gere apenas arquivos a partir de cartões semanticamente auditados conforme `../gerar-revisao-anki/references/auditoria-conteudo-gabaritos.md`; uma saída aprovada dos scripts não certifica gabarito. Não fabrique relatórios.

**Coleção viva:** `scripts/colecao_anki.py` (`buscar`, `duplicatas`, `dificeis`, `desempenho`, `lacunas`) lê o perfil `concursos` deste computador em cópia temporária, sem alterar nada; detalhes em `references/uso_scripts.md`.

**Atalhos de baixo custo:** `scripts/extrair_pdf.py PDF -o TMP.json --texto TMP.txt [--ruido PALAVRA]` grava também o texto limpo (sem marcas-d'água, CPF e rodapés), bem menor que o JSON; leia o TXT. Para um lote pronto, `scripts/finalizar_lote.py LOTE --baralho NOME` (com `uv run --no-project --with genanki python -I -X utf8`) exporta ZIP e APKG para `output/<CONCURSO>_<Tema>/` sem sobrescrever, revalida o ZIP final (estrutura, calibração, revisão de recuperação e, em lote de PDF, cobertura por prioridade com `../gerar-revisao-anki/scripts/validar_cobertura_pdf.py`) e imprime só o resumo; aceita `--profile`, `--exception-reason` e `--max-cards`.

Para exportação textual, use `scripts/exportar_anki.py`. Os campos chegam em HTML montado por `../gerar-revisao-anki/scripts/html_anki.py` (protocolo visual); o validador central reprova HTML inseguro e, em notas novas, tags desbalanceadas e Cloze com várias omissões sem a tag `Mnemonico`. Com imagens locais autênticas e manifesto, siga o protocolo visual e use `scripts/exportar_anki_visual.py`. Ambos executam o validador central com `--new`. A [matriz de quantidades](../gerar-revisao-anki/references/matriz_tipos_quantidades.md) define composição, paridade e parâmetros de perfil, justificativa e teto. Use os mesmos parâmetros no exportador e na revalidação. Rode o lint de clareza e revise os avisos semanticamente. Forneça um TSV vazio para cada modalidade ausente. Use caminhos completos dos scripts e inclua evidências nos relatórios.

APKG depende de genanki. Os tipos de nota do pacote levam o CSS padrão de `../gerar-revisao-anki/scripts/estilo_anki.py` (Arial 20 px, igual ao Basic/Cloze da coleção); não criar outro tipo nem mudar esse CSS por lote. Inspecionar integridade ZIP, banco e mídia; declarar importação e renderização no aplicativo como não testadas se não executadas. TSV deve ser importado separadamente no modelo Básico (sem inverso) para C/E e Cloze para lacunas; mapear terceira coluna como Tags e habilitar HTML. Não importar os TSVs e o APKG do mesmo lote. Exportação não altera a coleção. Mudanças na frente podem gerar nova identidade; não prometer atualização segura de notas existentes sem conferir IDs.

## Calibração documental de D novos

Antes de exportar lote com D, seguir `../gerar-revisao-anki/references/protocolo-modo-estrategico.md` e `../gerar-revisao-anki/references/registro-calibracao-cebraspe.md`. Incluir `calibracao_cebraspe.json` no diretório de relatórios. Rodar `../gerar-revisao-anki/scripts/validar_calibracao_cebraspe.py DIRETORIO_DO_LOTE` e novamente sobre o ZIP final; qualquer falha impede apresentar a entrega como final. Os exportadores textual e visual bloqueiam D novos sem esse JSON e verificam o registro no diretório e no ZIP final. A rubrica exige também linguagem_didatica com resultado PASSA e evidência específica. Para analisar coleções antigas, usar os fluxos de leitura/revisão; não fabricar registros retroativos nem usar o exportador de notas novas para contornar essa distinção. O validador central antigo não substitui a checagem adicional. Não produzir um pacote apenas para revisar poucos cartões inline. Esta checagem é documental, não semântica.

## Desenvolvimento e regressões

Quando a tarefa for testar ou atualizar o plugin, ler `references/testes-desenvolvimento.md`. Isso não acrescenta etapas à criação de poucos cartões inline.

## Barreira de recuperação e resolução do lint

Para exportar notas novas, ler `../gerar-revisao-anki/references/registro-revisao-recuperacao.md`. Além da calibração dos D, incluir `revisao_recuperacao.json` nos relatórios: evidências por R/C, hash do lote e decisões específicas para todos os sinais atuais de clareza, também nos D. Os exportadores textual e visual executam `validar_revisao_pedagogica.py` no diretório e no ZIP final. Ausência, cobertura incompleta, revisão obsoleta ou sinal pendente bloqueia a entrega. Não inferir aprovação automaticamente a partir do esquema ou do lint, nem usar fixtures como relatórios reais. Coleções existentes e respostas pequenas inline preservam os fluxos proporcionais; nenhum registro retroativo é fabricado.
