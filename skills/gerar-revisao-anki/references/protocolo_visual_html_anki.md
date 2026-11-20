# Protocolo visual em HTML para cartões Anki

O usuário aprende muito com esquemas visuais. Todo cartão novo usa HTML compatível com o Anki para organizar o verso (C/E) e o Extra (Cloze) em blocos coloridos, tabelas e fluxos. A forma serve ao conteúdo: um esquema só entra quando mostra uma relação (comparação, sequência, causa, classificação) melhor que o texto corrido. Não reduzir a qualidade ou a precisão do texto para caber no visual.

Use o helper `scripts/html_anki.py`, que monta os componentes abaixo com estilos já testados e confere a segurança do HTML (`problemas_html`). Não escreva estilos à mão em cada cartão: isso gera inconsistência.

## Compatibilidade com o Anki (desktop, AnkiMobile, AnkiDroid, AnkiWeb)

- Somente HTML com **estilos inline** (`style="..."`). O modelo Básico e o Cloze padrão não têm CSS próprio para essas classes; não depender de `class`, de `<style>` nem de CSS externo.
- Proibido: `<script>`, `<iframe>`, `<link>`, `<style>`, atributos `on...=`, `javascript:`, imagens remotas (`src="https://..."`), `position: fixed/absolute` e fontes externas. O validador central reprova esses usos.
- Nada de TAB ou quebra de linha dentro do campo: use `<br>` e elementos de bloco. Cada linha do TSV continua com exatamente três campos.
- **Modo noturno:** não definir cor do texto principal nem fundo opaco. Usar fundos translúcidos (`rgba(...)`) e bordas/títulos em tons médios, legíveis no claro e no escuro. Isso evita texto escuro sobre fundo escuro quando o Anki ou o AnkiDroid aplicam o tema noturno.
- **Celular:** nada de largura fixa; tabelas com `width:100%`, poucas colunas (até 3–4) e textos curtos nas células. Fluxos usam etiquetas `inline-block`, que quebram linha sozinhas.
- O modelo padrão centraliza o texto; os blocos do verso alinham à esquerda. Frentes curtas de R podem ficar centralizadas; frentes de D e textos de Cloze usam `frente()` para alinhar à esquerda e facilitar a leitura.
- Importar os TSVs com “Permitir HTML nos campos” marcado.

## Estrutura do verso C/E

1. Prefixo exato `✅ Certo<br><br>` ou `❌ Errado<br><br>` (exigido pelos validadores; não estilizar o prefixo).
2. `regra(...)` — 📌 a regra ou o conceito em linguagem simples, com o termo técnico explicado.
3. Conforme o caso:
   - D: `caso(...)` — 🔎 como o dado decisivo da frente leva à conclusão;
   - Errado: `erro(...)` — ⚠️ onde exatamente a afirmação falha;
   - Certo, quando útil: `certo(...)` — ✔️ por que a confusão concorrente não se aplica.
4. Opcional: `esquema(...)` com `tabela(...)` ou `fluxo(...)`, quando a relação visual ajudar.
5. Obrigatório, por último: `memorize(...)` — 💡 o **resumo da explicação** em uma ou duas frases. Substitui o antigo “Correção:”. No Errado, traz a formulação correta; no Certo, a ideia central. Deve ser algo que o aluno consiga repetir de memória.

`verso_ce(gabarito, blocos, memorize)` monta essa ordem e garante o prefixo e o Memorize final.

## Estrutura do Extra (Cloze)

`extra_cloze(blocos, memorize)`: `regra(...)` explicando o termo omitido (em mnemônico, cada termo), esquema opcional e `memorize(...)` no fim. O Texto do Cloze continua limpo: contexto suficiente e uma única omissão (várias só em mnemônico, com a tag `Mnemonico`).

## Rótulos e linguagem

- Títulos dos blocos: “📌 Regra”, “🔎 No caso”, “⚠️ Onde está o erro”, “✔️ Por que está certo”, “🗺️ Esquema”, “💡 Memorize”. Não usar “Explicação:”, “Justificativa:” nem “Fundamentação:” (o validador proíbe esses rótulos).
- Negrito (`<b>`) só no termo-chave ou no dado decisivo do verso. Na frente, não destacar o dado decisivo, para não entregar a resposta.
- Emojis só nos títulos dos blocos e no prefixo; não espalhar emojis no texto.
- O esquema não substitui a frase: a regra e o Memorize continuam escritos por extenso.

## Quando usar cada esquema

| Relação | Componente |
| --- | --- |
| Comparar dois ou três conceitos por critérios | `tabela` com conceitos nas colunas e critérios nas linhas |
| Sequência, percurso ou etapas | `fluxo` com etiquetas e setas |
| Quem vê / quem recebe / o que acontece | `tabela` de duas colunas (situação → resultado) |
| Associação curta (porta, sigla, função) | `tabela` de duas colunas ou `fluxo` de um passo |

## Verificação

Antes de exportar: rodar `problemas_html` (o helper já faz) e o `validar_anki.py --new`. Abrir uma prévia renderizada de alguns cartões (por exemplo, gerar um HTML de prévia e abrir no navegador, nos temas claro e escuro) para conferir contraste e quebra em tela estreita. A prévia não substitui o teste no aplicativo: declarar renderização no Anki como não testada se não for feita.
