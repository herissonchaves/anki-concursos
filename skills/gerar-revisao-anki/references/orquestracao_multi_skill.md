> Política comum: [nucleo-pedagogico.md](nucleo-pedagogico.md). Distribuição, equilíbrio e exceções: [matriz_tipos_quantidades.md](matriz_tipos_quantidades.md). Este documento complementa essas regras.

## Perfil PRF e Agente PF

Antes da triagem, carregar `../../perfil-carreiras-policiais/SKILL.md` e seu registro de disciplinas quando o alvo for PRF/PF. Reusar o perfil já resolvido nesta tarefa. As skills são instruções lidas pelo agente, não serviços ou subagentes. Inglês é a opção configurada para PRF; Espanhol está excluído. Outros cargos PF não herdam a matriz de Agente.

## ROTEAMENTO OBRIGATÓRIO: conteúdo de Língua Portuguesa

PRIMEIRO identificar disciplina. Sempre que o usuário mencionar Língua Portuguesa OU pedir cartões sobre gramática, pronome, verbo, análise sintática, concordância, regência, crase, pontuação, coesão, semântica, reescrita, tipologia ou interpretação de texto: **encaminhar antes de elaborar/avaliar os cartões** para `../../portugues-cebraspe-qualidade/SKILL.md` e seus três arquivos `../../portugues-cebraspe-qualidade/references/atlas_operacoes_cebraspe_portugues.md`, `../../portugues-cebraspe-qualidade/references/roteiro_auditoria_e_modelos.md` e `../../portugues-cebraspe-qualidade/references/evidencias_e_limitacoes.md`. A obrigação abrange revisão, caderno de erros, melhoria e auditoria de Português, não apenas criação explícita de C/E. Aplicar conjuntamente o pipeline geral; **o especializado não relaxa formatação, backup, atualização de Direito ou auditoria**. No relatório registrar `ROTEAMENTO=portugues-cebraspe-qualidade`, além de evidência de aplicação a cada ID. Se roteamento não foi comprovadamente executado, não alegar que foi.

## Seleção da rota pela intenção

| Pedido | Rota principal | Portões obrigatórios |
| --- | --- | --- |
| Crie revisão do PDF / C/E e Cloze | `gerar-revisao-anki` | Roteiro curto `roteiro-lote-pdf.md` -> ler (texto limpo) -> triagem -> backup se disponível -> banco `referencias/` (`importar` do anexo + busca) -> gerar -> crítica -> revalidar -> exportar; + **especialização para Português** |
| Quais tópicos merecem Anki? | `selecionar-conteudos-pdf-anki` | Mapa A/B/C, sem inventar cartão; + **especialização para Português** |
| Gere caderno de erros | `caderno-erros-anki` | Verificar erro marcado -> salvar a questão no banco `referencias/` -> diagnosticar -> novo item -> auditoria; + **especialização para Português** |
| Analise `.colpkg` | `analisar-colecao-anki` | Diagnóstico somente leitura; sem gerar cartões |
| Não entendi / melhore um card | `melhorar-cartoes-anki` | Reescrever -> crítica -> revalidar; + **especialização para Português** |
| Audite cartões / ZIP | `auditar-cartoes-anki` | Analisar lote real; reprovar os que falham; + **especialização para Português** |
| Consultar ou salvar questões de concursos de referência | `referencias-questoes` | `assuntos -d DISC` -> `buscar` -> `mostrar`; salvar só o item oficial com `nova`; `indexar` sem erros |
| Tarefa de extração, deduplicação, exportação | `automacao-anki-python` | Usar scripts somente quando disponíveis; não equivalem a validação pedagógica |

## Prioridades

1. Skills são instruções especializadas, **não agentes autônomos**. Não inventar invocação de uma ferramenta de execução que não existe.
2. Português => sempre especialização; misto => Português apenas onde pertinente; não Português => fluxo normal. Não atribuir ao formato C/E a banca real de provas da FCC.
3. PDF + `.colpkg`: comparar backup acessível antes de gerar. PDFs só: triagem A/B/C antes de escrever. Prints de erros sem resposta marcada não revelam erro real. Lote existente só com pedido de auditoria não autoriza recriar.
4. O núcleo é a política comum; a matriz é a fonte única de composição e exceções. `pipeline_qualidade_obrigatorio.md` é atalho, não regra superior. `triagem_previa_pdf.md` precede qualquer geração a partir de material. Especialização acrescenta critérios linguísticos e matriz G/S/C.
5. Não inventar leitura, teste, pesquisa, desempenho, gabarito de banca ou arquivo ZIP. Cada item exige primeira crítica e segunda conferência da solução.
6. Para automação, consultar `../../automacao-anki-python/SKILL.md`; scripts não comprovam nível cognitivo, e nenhuma ação deve editar backup original.

## Testes de regressão obrigatórios após alteração de roteamento

- Pedido `Gere revisão do PDF de pronomes` mesmo sem palavra Português: selecionar **gerar-revisao-anki + portugues-cebraspe-qualidade**.
- Pedido `Caderno de erros: uso do se`: **caderno-erros + especialização**; não inferir erro de print sem resposta marcada.
- Pedido `Melhore este card de regência`: **melhorar-cartoes + especialização**; reescrever e auditar.
- Pedido `Audite cartões sobre reescrita`: **auditar-cartoes + especialização**; validar separadamente gramática, sentido e coesão.
- Pedido `Gere cards de Direito Administrativo`: **perfil PRF/PF quando pertinente + rota geral + Direito transversal + Administrativo**, sem especialização de Português.
- Pedido de lista de tópicos de Português sem gerar cartões: **triagem + especialização**, sem exportar.
- Pedido misto Português + Direito: **especialização somente para Português**.
- Com ambiente que não invoque a UI do plugin: verificar corretamente presença do encaminhamento no pacote e testes executáveis, mas registrar `end-to-end UI=NAO EXECUTADO`.
