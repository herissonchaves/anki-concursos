> Política comum: [núcleo](../../gerar-revisao-anki/references/nucleo-pedagogico.md). Composição e exceções: [matriz](../../gerar-revisao-anki/references/matriz_tipos_quantidades.md).

# Scripts Anki

## Revisar e devolver coleção existente

`analisar_colpkg.py` agora lê bancos `collection.anki21b` sem usar o stub legado.
Requer `zstandard` (Python 3.12/3.13, versões testadas; ver `../requirements-optional.txt`) ou o `compression.zstd` do Python 3.14+. O limite de descompressão é 512 MiB. A
collation usada na inspeção é aproximação somente de leitura; não reconstruir
índices com ela. Para edição, o fluxo abaixo usa o mecanismo oficial do Anki.

Depois da revisão semântica integral, criar JSON com a chave `notes`, contendo
uma entrada por nota: `id`, `old_fields`, `new_fields`, `decision` (`APROVAR` ou
`REFORMULAR`) e `reason`. Notas aprovadas mantêm campos idênticos. Guardar fontes,
motivos específicos, redundâncias e eventuais mudanças de alvo em relatório.
O script confere a cobertura declarada, não certifica que a leitura foi feita.

Executar com `anki==26.9.3` (versão de API testada):

```text
python revisar_colpkg.py original.colpkg plano.json output/PRF_Tema/revisado.colpkg --report verificacao.json
```

O fluxo importa em pasta temporária, aplica somente campos, renderiza cada cartão,
exporta pelo Anki, reimporta para conferir mídia e exige igualdade exata de
cartões e histórico. Preserva IDs, GUIDs, modelos e tags; não altera índices
Cloze. Nunca recebe caminho de perfil ativo. Caminhos de saída devem ser novos.
`verificacao.json` contém textos privados: entregar só ao usuário, nunca embutir
no plugin nem versionar. O `.colpkg` revisado vai para `output/`, fora do Git. Há API interna encapsulada na importação; falhar se versão incompatível.

Explicar que importar `.colpkg` substitui a coleção do perfil. Recomendar perfil
separado para conferir. Distinguir teste do backend e teste da interface desktop.

Python 3.10+; `genanki` somente para `.apkg`; `pymupdf`/`pypdf` e `rapidfuzz` continuam opcionais para as funções anteriores. Scripts não consultam nem baixam imagens da internet: pesquisa e verificação da licença/adequação dependem de ferramentas de navegação e fontes originais. **Não simular busca nem arquivo local.**

Para texto puro, usar `scripts/exportar_anki.py --ce ... --cloze ... --relatorios ... -o saida.zip [--apkg saida.apkg]`. Para cards com imagem na frente, após pesquisa na web, obtenção dos originais licenciados e auditoria visual, organizar `midia/` com arquivos locais e relatório `relatorios/fontes_visuais.tsv`. Exemplo:

```bash
python3 skills/automacao-anki-python/scripts/exportar_anki_visual.py \
  --ce trabalho/anki_certo_errado.tsv \
  --cloze trabalho/anki_cloze.tsv \
  --relatorios trabalho/relatorios \
  --midia trabalho/midia \
  -o output/PRF_Tema/anki_visual.zip \
  --apkg output/PRF_Tema/anki_visual.apkg
```

Sem `genanki`, omitir `--apkg` e importar o ZIP por TSV + cópia manual dos arquivos dentro de `midia/` para `collection.media`, sem subpastas, habilitando «Permitir HTML nos campos». Com `.apkg`, imagens locais acompanham o pacote. **Não** usar diretamente URL `https://` no atributo `src` dos cartões.

Ao solicitar ZIP e APKG juntos, os exportadores preparam e validam os dois arquivos antes de gravá-los nos destinos finais. Se a geração do APKG falhar, corrija a causa ou execute novamente sem `--apkg` para gerar só o ZIP.

`fontes_visuais.tsv` deve conter cabeçalho `arquivo\tcartao_id\tpagina_origem\tarquivo_url\tautor\tlicenca\tdata_consulta\tmotivo_educacional\tstatus` com ao menos uma linha por arquivo. O validador verifica declaração/presença, mas a veracidade da licença/adequação visual exige revisão humana. Falhar com referência a arquivo ausente, arquivo extra não referenciado, formato inválido ou manifesto faltante.

Os relatórios clássicos continuam obrigatórios (`selecao_e_fontes.txt`, `economia_de_revisao.txt`, `auditoria_pedagogica.txt`); PDF acrescenta cobertura/triagem; Direito o radar; erros o diagnóstico; backup a análise legível. CLI não inventa relatórios de auditoria ou dados de `.colpkg`. `--apkg` cria um arquivo; a importação pode adicionar ou atualizar notas conforme identidade e opções do Anki. Não prometer preservação do histórico sem verificar a correspondência.

## Perfis de exportação

Use os parâmetros de perfil, justificativa e teto definidos na [matriz de quantidades](../../gerar-revisao-anki/references/matriz_tipos_quantidades.md) tanto na exportação quanto na revalidação. A política efetiva fica em `relatorios/politica_validacao.json`.

## Calibração Cebraspe

Em novas exportações que contenham D, executar também `../../gerar-revisao-anki/scripts/validar_calibracao_cebraspe.py DIRETORIO_OU_ZIP`, usando o caminho completo. O diretório deve conter `anki_certo_errado.tsv` e `relatorios/calibracao_cebraspe.json`. Consultar `../../gerar-revisao-anki/references/registro-calibracao-cebraspe.md`. O script retorna 0 para registro consistente ou lote sem D, 1 para falhas documentais e 2 para erro de leitura. Não certifica conteúdo nem consulta às fontes. Exportadores preservam esse JSON; checar novamente o ZIP final. Não aplicar esta exigência retroativamente a auditorias de coleções.
## Notas novas — barreira adicional

`validar_anki.py` não basta para liberar exportação. Os exportadores exigem também `relatorios/revisao_recuperacao.json`, conforme `../../gerar-revisao-anki/references/registro-revisao-recuperacao.md`. Diagnóstico: `python -X utf8 CAMINHO_COMPLETO/validar_revisao_pedagogica.py DIRETORIO --listar-sinais`. Ele lista hashes e sinais, sem criar aprovação. Verificação: o mesmo comando sem `--listar-sinais`, no diretório e no ZIP final. Resolver sinais por correção ou exceção editorial específica, atualizar hashes após edição e manter a calibração de D. Não aplicar o novo esquema retroativamente a backups existentes.
