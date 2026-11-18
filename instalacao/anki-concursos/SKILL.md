---
name: anki-concursos
description: Cria, seleciona, audita e melhora flashcards Anki para concursos públicos (PRF como prioridade padrão, Agente PF e outros concursos quando pedidos), no estilo Certo/Errado Cebraspe e Cloze, exportados em TSV. Use sempre que o usuário pedir cards/cartões/flashcards de revisão para o Anki a partir de PDF, apostila, aula, questões erradas ou tema de edital; quando pedir para auditar, explicar ou reformular cartões; analisar backup .colpkg; ou orientar rotina de estudo no Anki/FSRS.
---

# Anki-Concursos (skill instalada)

Porta de entrada do repositório **Anki-Concursos**, que guarda as regras completas,
as referências e os scripts de validação e exportação.

Repositório (Windows): `C:\Users\Herisson.DESKTOP-EHB23TA\Nextcloud\IA Agents\Anki-Concursos`

Antes de qualquer trabalho, leia `SKILL.md` na raiz do repositório e siga a skill
especializada que ele indicar. As regras ficam no repositório (núcleo em
`skills/gerar-revisao-anki/references/nucleo-pedagogico.md`); este arquivo não as
repete para não divergir delas. Se o caminho não existir, pergunte ao usuário onde
está o repositório.

## Roteamento rápido (caminhos relativos ao repositório)

| Pedido | Skill |
| --- | --- |
| Selecionar temas de um PDF | `skills/selecionar-conteudos-pdf-anki/SKILL.md` |
| Criar cartões C/E (rápidos e desafiadores) ou Cloze | `skills/gerar-revisao-anki/SKILL.md` |
| Caderno de erros a partir de questões | `skills/caderno-erros-anki/SKILL.md` |
| Auditar qualidade de cartões | `skills/auditar-cartoes-anki/SKILL.md` |
| Explicar ou reformular cartões | `skills/melhorar-cartoes-anki/SKILL.md` |
| Inspecionar backup `.colpkg` (somente leitura) | `skills/analisar-colecao-anki/SKILL.md` |
| Extrair PDF, validar e exportar TSV/ZIP/APKG | `skills/automacao-anki-python/SKILL.md` |
| Rotina, carga de revisão, botões, FSRS | `skills/orientar-estudo-anki/SKILL.md` |

Para PRF ou Agente PF, leia também `skills/perfil-carreiras-policiais/SKILL.md` e a
especialização da disciplina indicada em `skills/perfil-carreiras-policiais/references/disciplinas.json`.

## Perfil do usuário

- Foco atual: **PRF** (Policial Rodoviário Federal). Também vai prestar outros
  concursos: pedido explícito de outro cargo ou banca prevalece e exige conferir o
  programa próprio. Sem alvo, PRF; PF sem cargo = Agente. Língua estrangeira: Inglês.
- Não é formado em Direito: linguagem clara, termos técnicos explicados no verso.
- Aprende melhor com recursos visuais: cards em HTML com blocos e esquemas, sempre
  com o 💡 Memorize no fim do verso.
- Antes de criar desafiadores, sempre pesquisar questões anteriores Cebraspe C/E e de
  outras bancas e usá-las como inspiração.
- Entrega preferida: **arquivos TSV** importáveis no Anki, salvos em `lotes/` dentro
  do repositório.

## Git

Siga a seção "Git local" do `SKILL.md` da raiz: commits locais autorizados; push,
remotos e reescrita de histórico exigem autorização própria.

## Manutenção desta cópia

A fonte desta skill é `instalacao/anki-concursos/SKILL.md` no repositório. Ao mudar o
roteamento ou o perfil, edite a fonte e copie-a para
`~/.claude/skills/anki-concursos/SKILL.md`.
