# Testes de desenvolvimento

Executar somente em cópia do pacote e com fixtures sintéticas. Não usar perfil ativo do Anki ou backup privado como fixture. Manter bibliotecas e saídas fora do pacote do plugin.

Instalar `../requirements-dev.txt` no ambiente de testes. O teste de ida e volta da coleção usa a biblioteca oficial `anki==26.9.3`, declarada em `../requirements-optional.txt`. Sem uma dependência, declarar testes não executados; não contabilizá-los como aprovados.

Da raiz do plugin, executar com Python em UTF-8:

```text
python -X utf8 -m pytest skills/gerar-revisao-anki/tests skills/automacao-anki-python/tests -q
```

A suíte deve cobrir: bloqueio de D novos sem calibração; rubrica incompleta ou com linguagem/didática reprovada; verificação do diretório e do ZIP final; paridade separada R/D; Cloze novo com c1 único ou repetido e cobertura opcional por desafiadores (só lacunas existentes e D do lote); leitura de notas antigas sem reequilíbrio; contagem e mídia do APKG; preservação de coleção/histórico em cópia; ausência de biblioteca opcional e argumentos CLI no Windows.

As fixtures de calibração dentro de `tests/` contêm fontes fictícias e não podem gerar relatórios de produção. Testes documentais deliberadamente aceitam exemplos semanticamente errados para demonstrar os limites do verificador. Uma suíte verde não é aprovação pedagógica.

Após testes, aplicar a avaliação editorial multidisciplinar em `../../gerar-revisao-anki/references/avaliacao-pedagogica-multidisciplinar.md`. Para o piloto editorial com fontes reais exigido em atualizações do gerador, usar como modelo `../../gerar-revisao-anki/references/piloto-editorial-prf.md`. Registrar contagens, exceções, falhas, correções e limites. Não publicar “tudo aprovado” quando apenas um subconjunto foi executado.

## Regressões das barreiras de revisão

Incluir `test_revisao_214.py`: falta de revisão R/C, fontes/solução incompletas, hashes obsoletos após alteração de cada campo, resposta Cloze exposta com alerta pendente, exceção justificada, correção real com nova revisão, contagens zero por formato, JSON inválido, diretório e ZIP final. Verificar também exportador visual e preservação de mídia/histórico na suíte anterior. Helpers `recovery_fixture.py` e `calibration_fixture.py` são sintéticos e exclusivos de testes, sem certificação de conteúdo. Um controle negativo com declaração falsa completa deve continuar demonstrando que o esquema não entende a solução. Executar piloto separado com fontes reais, guardar candidatos e declarar autorevisão quando não houver revisor independente. Não converter fixtures no piloto.
