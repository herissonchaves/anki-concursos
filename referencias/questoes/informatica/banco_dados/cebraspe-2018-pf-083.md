---
id: cebraspe-2018-pf-083
tipo: questao
banca: Cebraspe
formato: certo_errado
ano: 2018
orgao: PF
concurso: "PF — Concurso 2018 (Edital nº 1/2018 – DGP/PF)"
cargo: "Agente de Polícia Federal (cargo 12)"
caderno: 408_DGPPF012
item: "83"
disciplina: informatica
assunto: banco_dados
subassuntos: [chaves]
palavras_chave: ["chave primária", "nomes de atributos"]
gabarito: E
gabarito_status: definitivo
url: "https://cdn.cebraspe.org.br/concursos/PF_18/arquivos/MATRIZ_408_DGPPF012__PAG_9.PDF"
gabarito_url: "https://cdn.cebraspe.org.br/concursos/PF_18/arquivos/GAB_DEFINITIVO_408_DGPPF012__PAG_9.PDF"
origem: pesquisa_internet
fonte_descoberta: "Caderno e gabarito definitivo oficiais no CDN do Cebraspe (página do concurso PF_18), p. 7"
consulta: 2026-11-21
concursos_alvo: [PF_AGENTE, PRF]
operacao_observada: "Atributos de mesmo nome em entidades distintas."
usado_em: []
hash: ac7788f6e42531ae
---
# Cebraspe 2018 — PF — item 83

## Enunciado

> ![[cebraspe-2018-pf-081-fig1.png]]
>
> [Figura do caderno oficial: modelo entidade-relacionamento — entidade “produto” (atributos código, identificador; preço; descrição) ligada por um relacionamento sem nome, com cardinalidade n do lado de produto e 1 do lado de “tipo de produto” (atributos código, identificador; descrição).]
>
> Considerando o modelo entidade-relacionamento (ER) precedente, julgue os seguintes itens, relativos a banco de dados.

Situação hipotética: Ao analisar o modelo ER em questão, Paulo verificou que há duas chaves identificadas com o mesmo nome: código — em tipo de produto e em produto. Paulo sabe que o conceito de chaves é básico para estabelecer relações entre linhas de tabelas de um banco de dados relacional e que as chaves primárias devem ser únicas. Assertiva: Nessa situação, Paulo deve invalidar o modelo ER em questão, pois ele está semanticamente errado, já que não pode haver chaves primárias com nomes iguais, ainda que em entidades distintas.

## Gabarito

**Errado** — definitivo ([gabarito oficial](https://cdn.cebraspe.org.br/concursos/PF_18/arquivos/GAB_DEFINITIVO_408_DGPPF012__PAG_9.PDF))
