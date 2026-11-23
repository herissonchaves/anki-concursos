---
id: conteudo-informatica-internet-intranet-extranet-vpn-www-e
tipo: conteudo
titulo: "Informática — internet, intranet, extranet, VPN, WWW e camadas da web (surface, deep, dark)"
disciplina: informatica
assunto: navegadores_internet
subassuntos: [intranet_extranet, vpn, internet_www, deep_web, conceitos_basicos]
palavras_chave: [intranet, extranet, TCP/IP, VPN, tunelamento, WWW, HTTP, HTTPS, "deep web", "dark web", Tor]
concursos_alvo: [PRF, PF_AGENTE]
norma: "Conceitos técnicos — Cartilha de Segurança para Internet (CERT.br, glossário: VPN) e material do curso (Projeto Missão)"
dispositivos: [VPN, intranet, extranet, "deep web"]
situacao: vigente
verificado_em: 2026-11-22
url: "https://cartilha.cert.br/livro/cartilha-seguranca-internet.pdf"
fonte_descoberta: "Busca restrita a cert.br para o lote PRF Missão 03 (INF010004), em 22/11/2026"
consulta: 2026-11-22
usado_em: ["PRF_M03_INF010004_Internet_Intranet#R01,R02,R03,R04,R05,R06,R07,R08,R09,R10,R11,R12,D01,D02,D03,D04,C01"]
hash: d4936ab8a31a7584
---
# Informática — internet, intranet, extranet, VPN, WWW e camadas da web (surface, deep, dark)

## Escopo e método

- Conceitos técnicos estáveis; definição de VPN conferida no glossário da Cartilha do CERT.br (resumo de busca); demais pontos conferidos com o material e com as questões Cebraspe do banco.

## Ambientes

- Internet: rede pública, mundial e descentralizada de redes, baseada na pilha TCP/IP; acesso por provedor (ISP).
- Intranet: rede privada de uma organização, restrita a usuários internos autorizados (login e senha), com as mesmas tecnologias e protocolos da internet (TCP/IP, HTTP/HTTPS, SMTP, FTP); pode ser acessada remotamente por usuários autorizados, por exemplo via VPN; compartilha recursos como impressoras e bancos de dados.
- Extranet: extensão da intranet a usuários externos autorizados (clientes, fornecedores, parceiros), acessada pela internet.
- VPN: rede privada construída sobre infraestrutura pública, com criptografia e autenticação (túnel), para que só autorizados acessem e os dados não sejam interceptados.
- HTTPS indica conexão protegida por certificado e criptografia; não indica, por si, que o site é de intranet.

## Web

- WWW não é protocolo: é o sistema de hipertexto distribuído acessado por navegadores via HTTP/HTTPS; páginas em HTML, ligadas por hiperlinks.
- Surface web: conteúdo indexado por buscadores. Deep web: não indexado (área com login, bancos, e-mails); origem legítima. Dark web: parte da deep web acessível só com software específico (ex.: Tor), voltada ao anonimato, com usos lícitos e ilícitos.
- Termos: download = baixar; upload = enviar; update = atualizar; wireless = sem fio.
