---
name: anki-concursos
description: Skill principal do Anki-Concursos. Use para criar, selecionar, auditar ou melhorar flashcards Anki de concursos (PRF por padrão, Agente PF e outros quando pedidos) em Certo/Errado estilo Cebraspe e Cloze, exportados em APKG; para caderno de erros, consulta somente leitura da coleção do Anki (ou de backup .colpkg), saber o que revisar ou estudar agora e orientar a rotina no Anki/FSRS. Encaminha à skill especializada e diz onde ficam os arquivos e o Git.
---

# Anki-Concursos

**Versão 2.29.** É o único número de versão do projeto: os demais `SKILL.md` e
documentos de `references/` não levam versão no título. Ao mudar regras, scripts ou
fluxos, suba a versão aqui no mesmo commit; o histórico de cada regra fica no Git
(`git log -- ARQUIVO`).

O repositório fica em `D:\NextCloud - Arquivos\IA Agents\Anki-Concursos` (sincronizado
pelo Nextcloud). A skill instalada no Claude (`~/.claude/skills/anki-concursos/SKILL.md`)
é só um lançador que manda ler este arquivo; roteamento, perfil e regras ficam aqui. Sua
fonte é [`instalacao/anki-concursos/SKILL.md`](instalacao/anki-concursos/SKILL.md):
recopie-a só quando a descrição (gatilhos) ou o caminho do repositório mudar.

## Perfil do usuário

- Foco atual: **PRF** (Policial Rodoviário Federal). Pedido explícito de outro cargo ou
  banca prevalece e exige conferir o programa próprio. Sem alvo, PRF; PF sem cargo =
  Agente. Língua estrangeira: Inglês (sem Espanhol).
- Não é formado em Direito: linguagem clara, termos técnicos explicados no verso (sem
  escrever isso nos cartões).
- Aprende melhor com recursos visuais: cards em HTML com blocos e esquemas, sempre com o
  💡 Memorize no fim do verso.
- Coleção do Anki: perfil `concursos`, lida só em cópia temporária
  ([colecao_anki.py](skills/automacao-anki-python/scripts/colecao_anki.py)); nunca alterar,
  importar ou sincronizar: quem importa é Hérisson.

## Escolha do fluxo

Abra a skill correspondente ao pedido e siga suas instruções. Carregue as
demais apenas quando o pedido ou a skill escolhida exigir. Os caminhos abaixo
são relativos à raiz do projeto.

| Pedido | Skill |
| --- | --- |
| Selecionar temas de um PDF | [selecionar-conteudos-pdf-anki](skills/selecionar-conteudos-pdf-anki/SKILL.md) |
| Criar cartões C/E ou Cloze | [gerar-revisao-anki](skills/gerar-revisao-anki/SKILL.md) |
| Trabalhar questões erradas | [caderno-erros-anki](skills/caderno-erros-anki/SKILL.md) |
| Conferir a qualidade de cartões | [auditar-cartoes-anki](skills/auditar-cartoes-anki/SKILL.md) |
| Explicar ou reformular cartões existentes | [melhorar-cartoes-anki](skills/melhorar-cartoes-anki/SKILL.md) |
| Inspecionar um backup | [analisar-colecao-anki](skills/analisar-colecao-anki/SKILL.md) |
| Extrair material ou validar e exportar arquivos | [automacao-anki-python](skills/automacao-anki-python/SKILL.md) |
| Consultar, salvar ou vincular referências (questões, editais, conteúdos verificados, notícias, prioridades) | [referencias-questoes](skills/referencias-questoes/SKILL.md) |
| O que revisar ou estudar agora (desempenho, lapsos, lacunas por prioridade); rotina, carga e FSRS | [orientar-estudo-anki](skills/orientar-estudo-anki/SKILL.md) |

Para os portões de cada rota, o roteamento obrigatório de Língua Portuguesa e os
casos de regressão do roteamento, veja
[orquestracao_multi_skill.md](skills/gerar-revisao-anki/references/orquestracao_multi_skill.md).

Toda criação de cartões autorais (R, D, Cloze e caderno de erros) usa também
[referencias-questoes](skills/referencias-questoes/SKILL.md): reaproveita as questões
de concursos do arquivo enviado (extraídas com `referencias.py importar`) e do banco
`referencias/`, que guarda também os editais dos concursos-alvo, conteúdos verificados
(reuso por até 90 dias com checagem rápida de alterações, no lugar de reler a fonte),
notícias (leis novas, decisões) e prioridades por assunto (o que mais cai, contado). O banco
é consultado antes de pesquisar, e tudo o que for pesquisado num pedido é salvo ali ao final,
em Markdown padronizado e no mesmo índice.

Para lote a partir de PDF, o caminho de menor custo é o
[roteiro curto](skills/gerar-revisao-anki/references/roteiro-lote-pdf.md): resume as regras
obrigatórias e os comandos (texto limpo do PDF, importação das questões, cadernos oficiais do
Cebraspe, modelo do gerador e `finalizar_lote.py`), sem precisar abrir todas as referências. Sua
seção 0 (economia de tokens) é obrigatória: PDF nunca por leitor de página da web, PDF lido uma vez,
importação com `--ruido`, sem saídas grandes e com idas e voltas agrupadas. Cards de revisão de PDF anexado
cobrem todo conteúdo de prioridade **Alta ou Média** para o concurso-alvo, do PDF e das questões
de concursos nele, sem duplicar notas da coleção
([cobertura-pdf.md](skills/gerar-revisao-anki/references/cobertura-pdf.md)), levam as tags
`Pagina_NN` da página de origem e seguem a formatação única de
[estilo_anki.py](skills/gerar-revisao-anki/scripts/estilo_anki.py) (Arial 20 px, como os cards de
Informática).

Para conteúdo de PRF ou Agente da Polícia Federal, use
[perfil-carreiras-policiais](skills/perfil-carreiras-policiais/SKILL.md) para
selecionar as especializações por disciplina. Considere o concurso indicado
no pedido. Na ausência de outro alvo explícito, a prioridade do projeto é PRF.

## Testes

As suítes de `automacao-anki-python`, `gerar-revisao-anki` e `referencias-questoes`
(scripts do banco e checagem de que os caminhos citados nas instruções existem)
são configuradas no `pyproject.toml`. Rode o comando na raiz do repositório.

```bash
uv run --python 3.13 --with-requirements skills/automacao-anki-python/requirements-dev.txt pytest
```

Use Python 3.12 ou 3.13 para a suíte padrão. Para cobrir backups modernos e a ida
e volta da coleção nessas versões, inclua também
[`requirements-optional.txt`](skills/automacao-anki-python/requirements-optional.txt)
com outro `--with-requirements`. Os testes que dependem de `zstandard` ou
`anki` são pulados quando a biblioteca correspondente está ausente.

## Arquivos e Git

- Lote em geração e entregáveis: `output/<CONCURSO>_<Tema>/` (fora do Git; Hérisson apaga a
  pasta depois de importar). Do lote, só `referencias/` é versionado, com a linha do lote em
  `referencias/historico_lotes.tsv`.
- Commits locais estão autorizados ao concluir e verificar mudanças importantes; push, remotos e
  reescrita de histórico exigem autorização própria.
- Regras completas (pastas, o que versionar, rotina e limites do Git): leia
  [GIT_E_ARQUIVOS.md](GIT_E_ARQUIVOS.md) ao gravar arquivos ou preparar um commit.

## Banco de referências

`referencias/` guarda, um arquivo Markdown por item, questões (`questoes/`), editais
(`editais/`), conteúdos verificados (`conteudos/`), notícias (`noticias/`) e prioridades
por concurso (`prioridades/`); `referencias/assuntos.md` e `referencias/indice.tsv` (com
coluna `tipo`) são gerados por `skills/referencias-questoes/scripts/referencias.py`, que
busca e mostra itens (ou só uma seção) sem abrir os arquivos. Formato e fluxo em [referencias-questoes](skills/referencias-questoes/SKILL.md).
