---
id: cebraspe-2025-pf-091
tipo: questao
banca: Cebraspe
formato: certo_errado
ano: 2025
orgao: PF
concurso: "PF — Concurso 2025 (Edital nº 1/2025 – PF – Policial; aplicação 27/7/2025)"
cargo: "Agente de Polícia Federal (cargo 16; Bloco II comum aos cargos 15, 16 e 17)"
caderno: 106_PF_CG1_01
item: "91"
disciplina: informatica
assunto: banco_dados
subassuntos: [sql]
palavras_chave: [select, references, "chave estrangeira"]
gabarito: anulada
gabarito_status: anulado
url: "https://cdn.cebraspe.org.br/concursos/PF_25/arquivos/106_PF_CG1_01.pdf"
gabarito_url: "https://cdn.cebraspe.org.br/concursos/PF_25/arquivos/A78F5BA07173AF0B8A5E611A1D7AAB166B7BD473E5D7AC2220F0F1B7DDB641E9.pdf"
origem: pesquisa_internet
fonte_descoberta: "Caderno e gabarito definitivo oficiais no CDN do Cebraspe (página do concurso PF_25), p. 2"
consulta: 2026-11-21
concursos_alvo: [PF_AGENTE, PRF]
operacao_observada: "Item anulado. Leitura de relacionamento no código SQL."
usado_em: []
hash: 4bdc58d8368cb3a6
---
# Cebraspe 2025 — PF — item 91

## Enunciado

> ```sql
> CREATE TABLE catalogo (
>   id_tabela INT,
>   nome_tabela VARCHAR(255),
>   descricao TEXT,
>   colunas TEXT,
>   relacionamentos TEXT,
>   regras_negocio TEXT,
>   data_criacao DATE,
>   data_ultima_atualizacao DATE
> );
> INSERT INTO catalogo VALUES (
>   1, 'vendas', 'Registros de vendas realizadas',
>   'id_venda INT, data_venda DATE, valor_venda DECIMAL, id_produto INT',
>   'id_produto REFERENCES produtos(id)', 'valor_venda > 0',
>   '2023-01-01', '2023-10-05'
> );
> SELECT * FROM catalogo WHERE nome_tabela = 'vendas';
> ```
>
> Com base nas informações do código precedente, julgue os próximos itens.

O comando SELECT mostra que existe uma relação com uma tabela de nome produtos mediante id_produto.

## Gabarito

**Anulada** — anulado ([gabarito oficial](https://cdn.cebraspe.org.br/concursos/PF_25/arquivos/A78F5BA07173AF0B8A5E611A1D7AAB166B7BD473E5D7AC2220F0F1B7DDB641E9.pdf))
