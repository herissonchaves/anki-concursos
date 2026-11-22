# Tags e Cloze mnemônico

Fonte única das regras de tags dos cartões novos e do formato do Cloze mnemônico (desde a 2.33).
Os outros documentos só remetem a este. Quem aplica as regras: `scripts/regras_tags.py`, usado por
`scripts/montar_lote.py` (falha ao gerar) e por `scripts/validar_anki.py --new` (reprova o lote).

## Tags de um card novo

Só estas, nesta ordem:

| Tag | Quando | Exemplo |
| --- | --- | --- |
| Conteúdo, hierárquica (`Disciplina::Assunto::Topico`) | sempre, exatamente uma | `Direito_Administrativo::Atos_Administrativos::Delegacao_e_Avocacao` |
| Nome curto do PDF | só em card feito sobre o PDF | `Missao_07`, `Missao_08` |
| Página(s) do PDF de onde saiu o conteúdo | só em card feito sobre o PDF | `Pagina_12` `Pagina_13` |
| Tipo, exatamente uma | sempre | `Rapida`, `Desafiadora` ou `Cloze` |
| Questão de origem, uma por questão | só em `Desafiadora` | `cebraspe-2021-prf-080` |

- **Conteúdo:** disciplina, assunto e tópico do card, em três níveis ou mais, sem espaço e sem
  acento obrigatório (o Anki mostra os níveis como árvore no navegador). No gerador:
  `ASSUNTO = 'Disciplina::Assunto'` e `tags='Topico'` em cada card; o montador junta os dois.
- **PDF e páginas:** entram juntos, e só no card que cobre uma página da `COBERTURA` (ou seja, feito
  sobre o PDF). Card feito de print de questão, de caderno de erros ou de pesquisa avulsa não leva
  nenhum dos dois. No gerador: `PDF = 'Missao_07'` (o montador põe o nome só onde houver `Pagina_NN`).
- **Questão de origem (D):** nome do arquivo `.md` da questão em `referencias/questoes/` que inspirou
  o desafiador, sem a extensão. O montador tira dos `refs` do D.

## Proibidas

Qualquer outra tag. Em especial:

- concurso, cargo ou banca: `PRF`, `PF`, `PF_Agente`, `Agente`, `Cebraspe`, `FGV`…;
- estilo e tipo antigos: `Estilo_Cebraspe`, `Tipo_Revisao_Rapida`, `Tipo_Desafiadora_Cebraspe`;
- genéricas: `Revisao`, `Revisao_PDF`, `Mnemonico`, `PDF`, `Lote`, `Novo`, `Caderno_Erros`, prioridade.

Os nomes antigos de tipo continuam reconhecidos só na leitura da coleção e de lotes antigos; nunca
os use em card novo. A coleção viva nunca é alterada; quando Hérisson enviar um backup e pedir a
coleção corrigida (2.34), as notas antigas são retagueadas por estas mesmas regras numa cópia, com
`reconstruir_colpkg.py` (ver `../../automacao-anki-python/references/uso_scripts.md`). Na retag,
`Pagina_NN` só fica onde o PDF de origem é identificável, e a tag da questão de origem do D só quando
o verso cita um item do banco.

## Cloze mnemônico

Mnemônico é a única nota que pode ter várias lacunas c1. Formato obrigatório da frente:

```
<b>Mnemônico CE-NO-RE:</b><br>
Pela Lei 9.784/1999 (art. 13), não podem ser delegados:<br>
a matéria de C{{c1::ompetência}} E{{c1::xclusiva}},<br>
a edição de atos NO{{c1::rmativos}}<br>
e a decisão de RE{{c1::cursos administrativos}}.
```

1. A frente começa com `Mnemônico SIGLA:`, que identifica a nota. Não existe tag `Mnemonico`.
2. Contexto visível: a regra e o assunto a que a sigla serve.
3. As letras da sigla ficam **visíveis**, e o restante de cada termo vai numa lacuna c1 própria,
   colada à letra (`C{{c1::ompetência}}`). Assim, depois de revelar, a frase fica correta. Cada
   termo ou grupo fica numa linha (`<br>`).
4. **Proibido:** "Dica autoral", "fonte" ou qualquer origem na frente; a lista inteira numa lacuna
   só; lacuna sem letra-pista antes dela.

Exemplo reprovado (não fazer):

```
Dica autoral CE-NO-RE: pela Lei 9.784/1999 (art. 13), não podem ser delegados {{c1::a matéria de
Competência Exclusiva, a edição de atos NOrmativos e a decisão de REcursos administrativos}}.
```

### Verso (Extra) do mnemônico

O Extra explica cada termo e traz, antes do 💡 Memorize, o bloco **📚 Origem do mnemônico**:

- `Autoral: criado para este card, sem fonte externa.`; ou
- `Encontrado em <link>` / `Adaptado de <link>`, com o link (`<a href>`) para a página ou a imagem
  da internet de onde veio.

No gerador: `mn=dict(sigla='CE-NO-RE', origem='autoral')` ou
`mn=dict(sigla='CE-NO-RE', origem=('encontrado', 'https://...', 'Nome da fonte'))` (ou `'adaptado'`).
O montador gera o bloco; não escreva a origem à mão. Pesquisa e conferência do mnemônico: seção
"Mnemônicos pesquisados" de `protocolo_cloze_cientifico.md`.
