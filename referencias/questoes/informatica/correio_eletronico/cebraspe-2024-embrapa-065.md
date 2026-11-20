---
id: cebraspe-2024-embrapa-065
tipo: questao
banca: Cebraspe
formato: certo_errado
ano: 2024
orgao: EMBRAPA
concurso: "EMBRAPA — Edital 2024 (aplicação 23/3/2025)"
cargo: "Técnico — Gestão da Informação — Tecnologia da Informação"
caderno: 043_EMBRAPA_001_01
item: "65"
disciplina: informatica
assunto: correio_eletronico
subassuntos: [protocolos, portas, smtp, firewall]
palavras_chave: ["porta 25", tcp, smtp, firewall, "envio de e-mail"]
gabarito: C
gabarito_status: definitivo
url: "https://cdn.cebraspe.org.br/concursos/EMBRAPA_24/arquivos/043_EMBRAPA_001_01.pdf"
gabarito_url: "https://cdn.cebraspe.org.br/concursos/EMBRAPA_24/arquivos/GAB_DEFINITIVO_043_EMBRAPA_001_01.pdf"
origem: pesquisa_internet
fonte_descoberta: "Caderno oficial no CDN do Cebraspe (migrado do lote PRF/Missao_08_Correio_Eletronico)"
consulta: 2026-11-20
concursos_alvo: [PRF, PF_AGENTE]
operacao_observada: "Situação de firewall que deve permitir envio de correio eletrônico; exige associar o serviço à porta/protocolo (TCP 25)."
usado_em: ["PRF/Missao_08_Correio_Eletronico#D03,D04,D12"]
hash: 3ac45623631831db
---
# Cebraspe 2024 — EMBRAPA — item 65

## Enunciado

> Considere que uma das diretivas de segurança da Embrapa requeira que firewalls locais estejam instalados e que permitam envio de correio eletrônico e serviço DNS. A partir dessa situação hipotética, julgue os itens seguintes.

Na situação em apreço, a porta 25 com o protocolo TCP deve estar aberta.

## Gabarito

**Certo** — definitivo ([gabarito oficial](https://cdn.cebraspe.org.br/concursos/EMBRAPA_24/arquivos/GAB_DEFINITIVO_043_EMBRAPA_001_01.pdf))

## Análise

Aplicação: envio de e-mail é SMTP, que usa TCP; a porta registrada para o SMTP é a 25.
