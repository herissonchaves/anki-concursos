# Registro documental de calibração — 2.16

Para exportações com D novos, salvar `relatorios/calibracao_cebraspe.json` em UTF-8 sem BOM. Em entregas inline, registrar as mesmas decisões de modo proporcional, sem exigir JSON. Auditoria de coleção antiga não exige fabricação retroativa deste arquivo.

O arquivo complementa os três relatórios existentes e pode referenciá-los; não duplicar longos textos. Incluir somente cartões D finais aprovados. Candidatos rejeitados e fontes anuladas podem ficar no relatório pedagógico, separados das referências de apoio. Compartilhar referências por família é permitido. Cada cartão precisa de análise própria.

Contrato JSON. Lotes novos usam a **versão 2**; a versão 1 continua aceita apenas para lotes anteriores à 2.16.

- Raiz: `schema_version: 2` (ou `1` em lote legado), `referencias: [...]`, `cartoes: [...]`.
- Cada referência: `id`, `banca` (por exemplo `Cebraspe`, `FGV`, `FCC`), `formato` (`certo_errado` ou `multipla_escolha`), `concurso`, `cargo`, `ano` inteiro, `caderno`, `item` como string, `url`, `consulta` YYYY-MM-DD, `operacao_observada`, `gabarito_status` (`definitivo`, `justificativa_oficial`, `nao_verificado` ou `anulado`). Para os dois primeiros, `gabarito_url` obrigatório. A própria URL do caderno comentado pode ser usada. Diferenciar edital/prova no campo concurso/caderno quando necessário. Não inventar cargo ou gabarito não localizado.
- Cada cartão: `id` único; `linha` física do TSV C/E, começando em 1; `sha256`; `gabarito` C/E igual ao verso; `alvo`; `operacao_autoral`; `regra`; `dado_decisivo`; `solucao`; `erro_plausivel`; `leitura_concorrente` com resultado da busca; `originalidade` explicando reconstrução; `fontes_conteudo` como lista de URLs efetivamente consultadas; `referencias` como lista de IDs.
- `fidelidade`: `comparada` exige referências, entre elas ao menos uma CESPE/Cebraspe `certo_errado`, e `comparacao` explicando o vínculo; questão de outra banca não basta para `comparada`. `inspiracao_geral` exige `limitacao` concreta e não deve ser anunciada como fidelidade demonstrada. A falta de referência de forma não dispensa verificação do conteúdo e da pertinência.
- Outras bancas (versão 2): cada D vincula em `referencias` ao menos uma questão de outra banca usada como inspiração ou, se nenhuma acessível for localizada, preenche `outras_bancas_pendencia` com as buscas feitas. A pendência não bloqueia o D. A pesquisa segue `protocolo-modo-estrategico.md`, seção “Pesquisa e comparação por família”.
- `segunda_conferencia: true` e `decisao: "APROVAR"` somente após revisão real.
- `rubrica`: objeto com `correcao`, `determinacao`, `operacao_d`, `comparacao`, `autoria`, `feedback`, `linguagem_didatica`, `utilidade`. Em `linguagem_didatica`, explicar concretamente por que frente e verso são compreensíveis, preservam condições e ensinam a passagem decisiva; mencionar o termo técnico explicado quando pertinente. Cada valor é `{"resultado": "PASSA", "evidencia": "motivo específico"}`. Somente `comparacao` admite PENDENTE quando a fidelidade é `inspiracao_geral`. Não copiar o mesmo motivo genérico entre critérios.

O SHA256 cobre frente, verso e tags exatos, unidos por TAB e sem quebra final. Exemplo de cálculo, não preenchimento de auditoria:

```python
import hashlib
sha256 = hashlib.sha256("\t".join([frente, verso, tags]).encode("utf-8")).hexdigest()
```

Qualquer mudança em um desses campos exige nova conferência semântica e atualização do hash. Igualdade de hash apenas vincula o registro ao conteúdo; não comprova quem revisou nem a verdade da declaração.

Após montar o diretório de entrega, executar:

```text
python skills/gerar-revisao-anki/scripts/validar_calibracao_cebraspe.py DIRETORIO_DO_LOTE
```

Usar caminho completo do script no ambiente real. Rodar novamente no ZIP final. O verificador lê apenas TSV e JSON, sem rede e sem extrair ZIP. Ele falha por referência inexistente, cobertura incompleta, alteração posterior, inconsistência de gabarito declarado ou campos/revisões pendentes; não detecta uma mentira bem preenchida. Nunca usar o resultado para substituir os oito critérios editoriais. Exportações de D novos sem o registro são bloqueadas. A exigência adicional de linguagem_didatica vale para novos registros; um registro antigo incompleto requer revisão real antes de servir a nova exportação, sem preenchimento fictício.
