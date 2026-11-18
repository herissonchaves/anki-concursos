"""Gera o lote Anki de Correio Eletrônico (PRF, Missão 08) — padrão visual 2.15.

Uso (na raiz do repositório):
  python -X utf8 lotes/PRF/Missao_08_Correio_Eletronico/fonte/gerar_lote.py

Escreve lote/ (TSVs + relatorios/*.json) e previa_cards.html. Os relatórios .txt
são escritos à mão e ficam em lote/relatorios/.
"""
import html as _html, json, random, sys
from pathlib import Path

PASTA = Path(__file__).resolve().parents[1]
RAIZ = PASTA.parents[2]
OUT = PASTA / 'lote'
sys.path.insert(0, str(RAIZ / 'skills' / 'gerar-revisao-anki' / 'scripts'))
from validar_revisao_pedagogica import batch_hash, fingerprint  # funções oficiais do projeto
from html_anki import (verso_ce, extra_cloze, regra, caso, erro, certo, esquema, tabela, fluxo, frente)

HOJE = '2026-11-18'
BASE = 'Informatica Correio_Eletronico PRF Missao_08'
R_TAG, D_TAG = 'Tipo_Revisao_Rapida', 'Tipo_Desafiadora_Cebraspe Estilo_Cebraspe'

# ---------------------------------------------------------------- esquemas reutilizados
T_PROTOCOLOS = tabela(['Protocolo', 'Função', 'Porta padrão'], [
    ['<b>SMTP</b>', 'Envia (cliente → servidor e servidor → servidor)', '25 (repasse) · 587 (submissão)'],
    ['<b>POP3</b>', 'Recebe: baixa para o aparelho', '110'],
    ['<b>IMAP</b>', 'Recebe: trabalha no servidor', '143']])
T_POP_IMAP = tabela(['', 'POP3', 'IMAP'], [
    ['Onde ficam as mensagens', 'No aparelho (em regra, saem do servidor)', 'No servidor'],
    ['Vários aparelhos', 'Não sincroniza', 'Sincroniza'],
    ['Porta sem TLS', '110', '143']])
ETAPAS = ['MUA do remetente', 'MSA', 'MTA', 'MTA', 'MDA', 'MUA do destinatário']
F_PERCURSO = fluxo(ETAPAS)
def percurso(*foco): return fluxo(ETAPAS, destaque=set(foco))
T_CAMPOS = tabela(['Campo', 'Recebe a mensagem?', 'Os outros veem o endereço?'], [
    ['Para', 'Sim', 'Sim'], ['Cc (com cópia)', 'Sim', 'Sim'], ['Cco / Bcc (cópia oculta)', 'Sim', '<b>Não</b>']])
T_COMANDOS = tabela(['Comando', 'Vai para', 'Anexo original'], [
    ['Responder', 'Só o remetente', 'Não vai'],
    ['Responder a todos', 'Remetente + Para + Cc', 'Não vai'],
    ['Encaminhar', 'Quem você escolher', '<b>Vai junto</b>']])
T_WEB_CLIENTE = tabela(['', 'Webmail', 'Cliente de e-mail'], [
    ['Como acessa', 'Navegador (Gmail na web, Outlook.com)', 'Programa instalado (Outlook, Thunderbird)'],
    ['Protocolo no aparelho do usuário', 'HTTP/HTTPS', 'SMTP + POP3 ou IMAP'],
    ['Precisa instalar?', 'Não', 'Sim']])
T_TLS = tabela(['Opção', 'Como protege'], [
    ['587 + STARTTLS', 'Começa sem cifra e é convertida para TLS'],
    ['465 + TLS implícito', 'Já começa cifrada'],
    ['S/MIME ou PGP', 'Cifra o conteúdo da mensagem (ponta a ponta)']])
T_ASSINATURA = tabela(['', 'Assinatura comum', 'Assinatura digital'], [
    ['O que é', 'Texto no fim (nome, cargo, telefone)', 'Cálculo com certificado (ID digital)'],
    ['Prova quem enviou?', 'Não (qualquer um copia)', 'Sim'],
    ['Mostra se foi alterada?', 'Não', 'Sim']])
T_PORTAS = tabela(['Uso', 'Porta'], [
    ['SMTP entre servidores (repasse)', '<b>25</b>'], ['Submissão pelo usuário (com login)', '587 ou 465'],
    ['POP3 / POP3S', '110 / 995'], ['IMAP / IMAPS', '143 / 993']])

# ---------------------------------------------------------------- fontes
F = {
 'rfc5321': ('https://www.rfc-editor.org/rfc/rfc5321', 'RFC 5321, seção 1.1 (objetivo: transferir mensagens) e 4.5.4.2 (porta 25 registrada na IANA); relaying entre servidores'),
 'rfc1939': ('https://www.rfc-editor.org/rfc/rfc1939', 'RFC 1939, seções 3–6: porta TCP 110; estados AUTHORIZATION/TRANSACTION/UPDATE; POP3 não se destina a manipular extensamente a caixa no servidor'),
 'rfc9051': ('https://www.rfc-editor.org/rfc/rfc9051', 'RFC 9051 (IMAP4rev2), resumo: manipular caixas remotas de modo equivalente a pastas locais, com ressincronização; seção 2.1: portas 143 e 993'),
 'rfc5598': ('https://www.rfc-editor.org/rfc/rfc5598', 'RFC 5598, seção 4: papéis MUA, MSA, MTA e MDA e ordem autor → MSA → MTAs → MDA → MUA do destinatário (store-and-forward)'),
 'rfc6409': ('https://www.rfc-editor.org/rfc/rfc6409', 'RFC 6409, seção 3.1 (porta 587 para submissão), 4.3 (MSA exige autenticação) e resumo (repasse continua na porta 25)'),
 'rfc8314': ('https://www.rfc-editor.org/rfc/rfc8314', 'RFC 8314, seções 3.1–3.3: TLS implícito nas portas 465 (submissão), 993 (IMAP) e 995 (POP3); STARTTLS na 587'),
 'rfc5322': ('https://www.rfc-editor.org/rfc/rfc5322#section-3.6.3', 'RFC 5322, seção 3.6.3: To (destinatários principais), Cc (outros destinatários) e Bcc (endereços não revelados aos demais destinatários)'),
 'ms_block': ('https://support.microsoft.com/en-us/office/block-or-allow-junk-email-settings-48c9f6f7-2309-4f95-9a4d-de987e880e46', 'Microsoft Support, Blocked Senders: mensagens de remetentes bloqueados vão direto para a pasta Lixo Eletrônico'),
 'ms_reply': ('https://support.microsoft.com/en-au/outlook/reply-to-or-forward-an-email-message', 'Microsoft Support (Outlook clássico): Responder só ao remetente; Responder a todos inclui Para e Cc; anexos não vão na resposta; ao encaminhar, os anexos originais são incluídos'),
 'ms_digsig': ('https://support.microsoft.com/en-us/office/secure-messages-by-using-a-digital-signature-in-outlook-549ca2f1-a68f-4366-85fa-b3f4b5856fc6', 'Microsoft Support: assinatura digital vem do ID digital (certificado), garante autenticidade e integridade e não é a mesma coisa que a assinatura de texto comum'),
 'gmail_clients': ('https://support.google.com/mail/answer/7126229?hl=pt-BR', 'Ajuda do Gmail: é possível adicionar o Gmail a clientes como Outlook, Apple Mail e Thunderbird; acesso IMAP sempre ativado'),
}
def fontes(*keys): return [{'url': F[k][0], 'consulta': HOJE, 'trecho': F[k][1]} for k in keys]
def urls(*keys): return [F[k][0] for k in keys]

REFS = [
 dict(id='MPTO24_99', concurso='MPTO — VI Concurso, Edital nº 1/2024 (aplicação 3/3/2024)', cargo='Técnico Ministerial Especializado — Fotografia (cargo 16)', ano=2024,
      caderno='952_MP_TO_016_01', item='99', url='https://cdn.cebraspe.org.br/concursos/MP_TO_24_SERVIDOR/arquivos/952_MP_TO_016_01.PDF', consulta=HOJE,
      operacao_observada='Atribui funções trocadas aos protocolos (SMTP para receber, POP para enviar); exige reconhecer a função de cada protocolo.',
      gabarito_status='definitivo', gabarito_url='https://cdn.cebraspe.org.br/concursos/MP_TO_24_SERVIDOR/arquivos/GAB_DEFINITIVO_952_MP_TO_016_01.PDF'),
 dict(id='EMBRAPA24_65', concurso='EMBRAPA — Edital 2024 (aplicação 23/3/2025)', cargo='Técnico — Gestão da Informação — Tecnologia da Informação', ano=2024,
      caderno='043_EMBRAPA_001_01', item='65', url='https://cdn.cebraspe.org.br/concursos/EMBRAPA_24/arquivos/043_EMBRAPA_001_01.pdf', consulta=HOJE,
      operacao_observada='Situação de firewall que deve permitir envio de correio eletrônico; exige associar o serviço à porta/protocolo (TCP 25) — Certo.',
      gabarito_status='definitivo', gabarito_url='https://cdn.cebraspe.org.br/concursos/EMBRAPA_24/arquivos/GAB_DEFINITIVO_043_EMBRAPA_001_01.pdf'),
 dict(id='ANP22_26', concurso='ANP — Processo Seletivo Simplificado, Edital nº 1/2022 (aplicação 9/10/2022)', cargo='Conhecimentos gerais para todas as atividades de nível superior', ano=2022,
      caderno='725_ANP_CG1_01', item='26', url='https://cdn.cebraspe.org.br/concursos/ANP_22_PSS/arquivos/725_ANP_CG1_01.PDF', consulta=HOJE,
      operacao_observada='Confunde o efeito de Encaminhar com Responder a todos no Outlook; exige saber a quem cada comando envia — Errado.',
      gabarito_status='definitivo', gabarito_url='https://cdn.cebraspe.org.br/concursos/ANP_22_PSS/arquivos/GAB_DEFINITIVO_725_ANP_CG1_01.PDF'),
 dict(id='CAU23_20', concurso='CAU/BR — Edital nº 1/2023 (aplicação 21/1/2024)', cargo='Conhecimentos básicos para os empregos 2 e 5 a 8', ano=2023,
      caderno='921_CAU_BR_CB3_01', item='20', url='https://cdn.cebraspe.org.br/concursos/CAU_BR_23/arquivos/921_CAU_BR_CB3_01.PDF', consulta=HOJE,
      operacao_observada='Atribui à opção Inserir Assinatura do Outlook o efeito de assinatura digital com criptografia; exige distinguir assinatura de texto de assinatura digital — Errado.',
      gabarito_status='definitivo', gabarito_url='https://cdn.cebraspe.org.br/concursos/CAU_BR_23/arquivos/GAB_DEFINITIVO_921_CAU_BR_CB3_01.PDF'),
]

# ---------------------------------------------------------------- rápidos (R)
R = [
 dict(k='R01', tags='Protocolos', g='C',
  f='O SMTP (Simple Mail Transfer Protocol) é o protocolo de envio de e-mail, usado do programa do usuário até o servidor e entre servidores.',
  b=[regra('O SMTP cuida do <b>envio</b> (transferência) das mensagens: quando o programa do usuário entrega a mensagem ao servidor e quando um servidor repassa a mensagem ao servidor do destinatário. Para <b>ler</b> a caixa postal, o programa usa POP3 ou IMAP.'),
     esquema(T_PROTOCOLOS)],
  m='SMTP = envio (<i>Sua Mensagem Tá Partindo</i>). Receber/ler é com POP3 ou IMAP.',
  alvo='Função do SMTP: envio/transferência de mensagens (submissão e repasse entre servidores).', fx=('rfc5321','rfc6409'),
  sol='Certo: RFC 5321 define o SMTP para transferir mensagens e descreve o repasse entre servidores; a RFC 6409 usa SMTP também na submissão pelo cliente.',
  alt='Testei a leitura "SMTP também recebe": o servidor de destino recebe a mensagem de outro servidor por SMTP, mas o usuário lê a caixa por POP3/IMAP; a frase fala só de envio, então continua Certa.',
  rec='Exige recuperar a função do protocolo a partir do nome; a frente não diz que POP3/IMAP recebem.', fb='Regra separa envio (SMTP) de leitura (POP3/IMAP); tabela compara os três protocolos; Memorize resume com o mnemônico do material.'),
 dict(k='R02', tags='Protocolos', g='E',
  f='O POP3 (Post Office Protocol versão 3) é o protocolo usado pelo programa de e-mail para enviar as mensagens que o usuário escreveu.',
  b=[regra('O POP3 é protocolo de <b>recebimento</b>: o programa do usuário o usa para baixar as mensagens da caixa postal no servidor.'),
     erro('A frase atribui ao POP3 o <b>envio</b>, que é função do SMTP.')],
  m='POP3 recebe (baixa) mensagens; quem envia é o SMTP.',
  alvo='Função do POP3: recebimento (download) de mensagens, não envio.', fx=('rfc1939','rfc5321'),
  sol='Errado: RFC 1939 define o POP3 para o cliente acessar a caixa postal e recuperar mensagens; envio é SMTP.',
  alt='Considerei clientes que usam POP3 e SMTP na mesma conta: ainda assim cada protocolo tem papel próprio; não há envio por POP3.',
  rec='Recupera a direção (receber × enviar) do POP3; a frente não oferece pista do papel correto.', fb='Bloco de erro aponta a troca de funções (explorada no item MPTO 2024, 99); Memorize traz a formulação correta.'),
 dict(k='R03', tags='Protocolos', g='C',
  f='No IMAP (Internet Message Access Protocol), as mensagens ficam no servidor, e o que se faz em um aparelho (ler, mover, apagar) aparece nos demais aparelhos da mesma conta.',
  b=[regra('O IMAP permite trabalhar <b>diretamente na caixa postal do servidor</b>, como se as pastas remotas fossem locais. Por isso a conta fica sincronizada entre celular, notebook e webmail.'),
     esquema(T_POP_IMAP)],
  m='IMAP = mensagens no servidor e tudo sincronizado entre aparelhos.',
  alvo='Característica do IMAP: armazenamento no servidor e sincronização entre dispositivos.', fx=('rfc9051',),
  sol='Certo: RFC 9051 descreve a manipulação de caixas remotas equivalente a pastas locais e a ressincronização de clientes.',
  alt='Testei "IMAP só funciona on-line": a RFC prevê clientes off-line que ressincronizam, mas isso não afeta a afirmação, que trata de onde ficam as mensagens.',
  rec='Exige lembrar a propriedade distintiva do IMAP diante do POP3.', fb='Regra explica a sincronização; tabela contrasta POP3 × IMAP; Memorize resume.'),
 dict(k='R04', tags='Protocolos', g='E',
  f='No POP3, em seu funcionamento padrão, as mensagens continuam guardadas no servidor e não são baixadas para o computador do usuário.',
  b=[regra('O POP3 <b>baixa</b> as mensagens para o dispositivo do usuário e, em regra, as remove do servidor depois do download (muitos programas permitem manter uma cópia).'),
     erro('Manter as mensagens no servidor é característica do <b>IMAP</b>, não do POP3.'),
     esquema(T_POP_IMAP)],
  m='No POP3, as mensagens são baixadas para o aparelho e, em regra, saem do servidor.',
  alvo='Comportamento padrão do POP3: download para o dispositivo local, em regra com remoção do servidor.', fx=('rfc1939',),
  sol='Errado: RFC 1939 trata o POP3 como recuperação da caixa postal, sem manipulação extensa no servidor; exclusão das marcadas ocorre no estado UPDATE.',
  alt='Considerei a opção "deixar cópia no servidor": ela existe, mas não torna a frase certa, porque a mensagem ainda é copiada para o computador.',
  rec='Recupera o local de armazenamento no POP3; não repete a frente do R03 (que trata do IMAP).', fb='Erro localizado (confusão com IMAP), exceção da cópia no servidor e Memorize com a formulação correta.'),
 dict(k='R05', tags='Webmail_Cliente', g='C',
  f='Para acessar um webmail, como o Gmail pelo navegador, basta um navegador com acesso à internet; não é necessário instalar um programa cliente de e-mail.',
  b=[regra('Webmail é o acesso ao e-mail por uma <b>página web</b>. O navegador conversa com o servidor do provedor por HTTP/HTTPS, e o provedor cuida do envio (SMTP) e do armazenamento.'),
     esquema(T_WEB_CLIENTE)],
  m='Webmail = só o navegador; nada para instalar.',
  alvo='Webmail: acesso pelo navegador, sem instalar cliente.', fx=('rfc5598','gmail_clients'),
  sol='Certo: na RFC 5598 o MUA pode ser uma interface web; o Gmail é usado no navegador e, opcionalmente, em clientes.',
  alt='Considerei a necessidade de "plugin" ou aplicativo: webmail não exige; aplicativo móvel é forma alternativa de acesso, não requisito.',
  rec='Recupera a característica definidora do webmail.', fb='Regra mostra quem faz cada parte; tabela compara webmail × cliente; Memorize resume.'),
 dict(k='R06', tags='Webmail_Cliente', g='E',
  f='Os programas Mozilla Thunderbird e Microsoft Outlook instalado no computador são exemplos de webmail, pois só funcionam dentro do navegador.',
  b=[regra('Thunderbird e o Outlook instalado são <b>clientes de e-mail</b>: programas instalados no dispositivo, que usam SMTP para enviar e POP3 ou IMAP para receber, e podem guardar mensagens localmente.'),
     erro('Webmail é o acesso <b>pelo navegador</b> (Gmail na web, Outlook.com), não um programa instalado.'),
     esquema(T_WEB_CLIENTE)],
  m='Thunderbird e Outlook instalado são clientes de e-mail; webmail é o que roda no navegador.',
  alvo='Distinguir cliente de e-mail instalado de webmail.', fx=('gmail_clients','rfc5598'),
  sol='Errado: a Ajuda do Gmail cita Outlook e Thunderbird como clientes aos quais se adiciona a conta; não são páginas web.',
  alt='Considerei o Outlook na web (Outlook.com), que é webmail; por isso a frente especifica "instalado no computador".',
  rec='Exige classificar exemplos conhecidos; a frente não informa a categoria correta.', fb='Critério (instalado × navegador) com exemplos de cada lado e Memorize com a classificação correta.'),
 dict(k='R07', tags='Campos_Cabecalho', g='C',
  f='Os destinatários incluídos no campo Cco (com cópia oculta) recebem a mensagem, mas seus endereços não são mostrados aos destinatários dos campos Para e Cc.',
  b=[regra('<b>Cco</b> (com cópia oculta), em inglês <b>Bcc</b> (<i>blind carbon copy</i>), envia a mensagem a destinatários cujos endereços não são revelados aos demais. Serve para proteger a privacidade de uma lista e dificultar a coleta de endereços por spammers.'),
     esquema(T_CAMPOS)],
  m='Cco = Bcc: recebe a mensagem, mas fica invisível para os outros.',
  alvo='Efeito do campo Cco/Bcc.', fx=('rfc5322',),
  sol='Certo: RFC 5322, 3.6.3 — Bcc contém endereços que não devem ser revelados aos outros destinatários.',
  alt='Testei "Cco oculta o remetente": não oculta; a frase não afirma isso, então segue Certa.',
  rec='Recupera o efeito do campo a partir de seu nome.', fb='Regra traz o sinônimo Bcc (pegadinha de banca); tabela de visibilidade; Memorize resume.'),
 dict(k='R08', tags='Campos_Cabecalho', g='E',
  f='Os endereços informados no campo Cc (com cópia) ficam ocultos para os demais destinatários da mensagem.',
  b=[regra('No <b>Cc</b>, os endereços ficam <b>visíveis</b> para todos os destinatários, como no campo Para.'),
     erro('Quem fica oculto é o destinatário do <b>Cco</b> (Bcc), não o do Cc.'),
     esquema(T_CAMPOS)],
  m='Cc é cópia visível; Cco é cópia oculta.',
  alvo='Cc é cópia visível (contraste com Cco).', fx=('rfc5322',),
  sol='Errado: RFC 5322 descreve o Cc como lista de outros destinatários, sem ocultação; ocultação é do Bcc.',
  alt='Considerei clientes que exibem resumo de destinatários: não altera a regra do campo Cc.',
  rec='Contraste direto entre Cc e Cco, confusão comum de nomenclatura.', fb='Regra e erro separam os dois campos; tabela de visibilidade; Memorize com a formulação correta.'),
 dict(k='R09', tags='Respostas', g='C',
  f='No Outlook, a opção Responder a todos envia a resposta ao remetente original e aos destinatários que estavam nos campos Para e Cc da mensagem.',
  b=[regra('<b>Responder</b> vai só para o remetente. <b>Responder a todos</b> inclui o remetente e todos os endereços de Para e Cc. Quem estava em Cco não entra, porque seu endereço não aparece para quem responde.'),
     esquema(T_COMANDOS)],
  m='Responder a todos = remetente + Para + Cc (nunca o Cco).',
  alvo='Alcance do comando Responder a todos.', fx=('ms_reply',),
  sol='Certo: a Microsoft define Responder a todos como resposta ao remetente e a todos nas linhas Para e Cc.',
  alt='Considerei o Cco: não é incluído; a frase lista só Para e Cc, coerente com a fonte.',
  rec='Recupera o alcance exato do comando.', fb='Regra diferencia os comandos e o caso do Cco; tabela de comandos; Memorize resume.'),
 dict(k='R10', tags='Respostas', g='E',
  f='No Outlook, ao encaminhar uma mensagem, os anexos que ela continha deixam de ser enviados.',
  b=[regra('<b>Encaminhar</b> envia a mensagem recebida a outra pessoa e <b>mantém os anexos originais</b>. Em Responder e Responder a todos, o Outlook não inclui os anexos, pois eles voltariam a quem os enviou.'),
     erro('A frase atribui ao Encaminhar o comportamento das <b>respostas</b>.'),
     esquema(T_COMANDOS)],
  m='Encaminhar leva os anexos; responder não leva.',
  alvo='Encaminhar mantém anexos; responder não.', fx=('ms_reply',),
  sol='Errado: a Microsoft informa que anexos da mensagem original são incluídos automaticamente ao encaminhar.',
  alt='Considerei que o usuário pode remover o anexo manualmente antes de encaminhar: isso é escolha do usuário, não comportamento do comando.',
  rec='Recupera a regra dos anexos por comando.', fb='Regra explica o motivo; erro localiza a troca; tabela de comandos; Memorize com a formulação correta.'),
 dict(k='R11', tags='Endereco', g='C',
  f='Em um endereço como ana@empresa.com.br, o caractere @ separa o nome do usuário (ana) do domínio (empresa.com.br).',
  b=[regra('O endereço tem a forma <b>usuário@domínio</b>. Antes do @ fica a parte local, que identifica a caixa postal; depois, o domínio, que indica quem recebe as mensagens (o <b>.br</b> indica o Brasil). O @ pode ser lido como "em": ana <i>em</i> empresa.com.br.'),
     esquema(fluxo(['ana', '@', 'empresa.com.br'], seta='·') + 'parte local · separador · domínio')],
  m='usuário @ domínio: o @ (lido "em") separa quem é de onde está a caixa postal.',
  alvo='Estrutura do endereço de e-mail: parte local @ domínio.', fx=('rfc5322',),
  sol='Certo: na RFC 5322 o endereço (addr-spec) é parte local + "@" + domínio.',
  alt='Considerei endereço com dois @: inválido; não afeta o exemplo.',
  rec='Exige reconhecer as duas partes do endereço e a função do @.', fb='Regra nomeia as partes e a leitura "em" (item PF 2018 citado no material); esquema visual do endereço; Memorize resume.'),
 dict(k='R12', tags='Seguranca_Email', g='E',
  f='O SMTP, por si só, criptografa o conteúdo das mensagens enviadas.',
  b=[regra('O SMTP, sozinho, transmite as mensagens <b>sem criptografia</b>. A proteção vem de camadas adicionais.'),
     erro('A criptografia não é do SMTP: vem do <b>TLS</b> na conexão (STARTTLS ou TLS implícito — as variantes "seguras" SMTPS, IMAPS, POP3S) ou do <b>S/MIME/PGP</b> no conteúdo.'),
     esquema(T_TLS)],
  m='SMTP não cifra sozinho: a segurança vem do TLS (conexão) ou de S/MIME/PGP (conteúdo).',
  alvo='SMTP não cifra por padrão; segurança vem de TLS ou S/MIME/PGP.', fx=('rfc8314','rfc5321'),
  sol='Errado: a RFC 8314 trata o TLS como camada adicionada (STARTTLS ou TLS implícito) aos protocolos de e-mail.',
  alt='Considerei provedores que forçam TLS: é configuração adicional, não propriedade do SMTP "por si só".',
  rec='Recupera a ausência de criptografia nativa.', fb='Erro aponta de onde vem a proteção; tabela das opções; Memorize com a formulação correta.'),
 dict(k='R13', tags='Webmail_Cliente', g='E',
  f='No Outlook, bloquear um remetente impede que essa pessoa consiga enviar mensagens para o seu endereço.',
  b=[regra('Bloquear um remetente no Outlook faz as novas mensagens dele irem direto para a pasta <b>Lixo Eletrônico</b>.'),
     erro('O bloqueio não impede o envio: a pessoa continua mandando mensagens; só muda <b>onde elas aparecem</b> para você.')],
  m='Bloquear remetente desvia as mensagens para o Lixo Eletrônico; não impede o envio.',
  alvo='Efeito do bloqueio de remetente no Outlook.', fx=('ms_block',),
  sol='Errado: a Microsoft informa que mensagens de remetentes bloqueados vão direto para Lixo Eletrônico.',
  alt='Considerei bloqueio feito pelo administrador do servidor (regras de transporte): é outro mecanismo; a frente trata da opção do usuário.',
  rec='Recupera o efeito real do bloqueio, apontado no material como já cobrado.', fb='Regra indica a pasta de destino; erro corrige a ideia de impedimento; Memorize resume.'),
 dict(k='R14', tags='Arquitetura_Email', g='C',
  f='O correio eletrônico é uma forma de comunicação assíncrona: o destinatário não precisa estar conectado no momento do envio para receber a mensagem depois.',
  b=[regra('<b>Assíncrona</b> é a comunicação que não exige os dois lados conectados ao mesmo tempo. A mensagem fica guardada na caixa postal do destinatário, no servidor, até ele acessá-la.'),
     certo('Uma chamada de vídeo, ao contrário, é <b>síncrona</b>: os dois precisam estar presentes ao mesmo tempo.')],
  m='E-mail é assíncrono: a mensagem espera na caixa postal até o destinatário abrir.',
  alvo='Caráter assíncrono (armazenar e repassar) do e-mail.', fx=('rfc5598',),
  sol='Certo: a RFC 5598 descreve o e-mail como serviço de armazenar e repassar (store-and-forward), com entrega na caixa postal.',
  alt='Considerei entrega quase instantânea em serviços modernos: rapidez não muda o caráter assíncrono.',
  rec='Recupera o significado de assíncrono aplicado ao e-mail.', fb='Regra define o termo; contraexemplo síncrono; Memorize resume.'),
]

# ---------------------------------------------------------------- Cloze (uma omissão por nota)
CZ = [
 dict(k='C01', tags='Arquitetura_Email',
  t='No percurso do e-mail, o programa em que o próprio usuário escreve e lê suas mensagens (como Outlook, Thunderbird ou a página do webmail) é chamado de {{c1::MUA (Mail User Agent)}}.',
  b=[regra('<b>MUA</b> = <i>User</i> Agent, o agente do <b>usuário</b>. É a ponta do percurso: o remetente escreve no MUA dele e o destinatário lê no MUA dele (por POP3 ou IMAP).'), esquema(percurso(0, 5))],
  m='MUA = programa do usuário (onde se escreve e se lê).',
  alvo='Papel do MUA.', fx=('rfc5598',), sol='Lacuna: MUA (aceitar só a sigla). RFC 5598 define o MUA como o agente que atua para o usuário.',
  alt='Testei MSA: aceita a submissão no provedor, não é o programa do usuário; a descrição "escreve e lê" determina o MUA.',
  rec='A descrição funcional determina a sigla sem revelá-la.', fb='Extra decodifica a letra U (User) e mostra o fluxo completo.', cob={'1': ['D02']}),
 dict(k='C02', tags='Arquitetura_Email',
  t='No provedor do remetente, o agente que recebe a mensagem vinda do programa do usuário, exige o login dele e só então a aceita para envio é o {{c1::MSA (Mail Submission Agent)}}.',
  b=[regra('<b>MSA</b> = <i>Submission</i> Agent, o agente de <b>submissão</b>: a porta de entrada no provedor. Exige autenticação (login) e costuma usar a porta 587.'), esquema(percurso(1))],
  m='MSA = porta de entrada do provedor: confere o login e aceita a mensagem.',
  alvo='Papel do MSA.', fx=('rfc5598','rfc6409'), sol='Lacuna: MSA. RFC 6409 atribui ao MSA a submissão autenticada na porta 587.',
  alt='Testei MTA: repassa entre servidores, sem exigir login do usuário; "exige o login" determina o MSA.',
  rec='A exigência de login é o dado que diferencia MSA de MTA.', fb='Extra decodifica Submission e liga à porta 587.', cob={'1': ['D01']}),
 dict(k='C03', tags='Arquitetura_Email',
  t='Os servidores que passam a mensagem adiante, de um servidor de e-mail para outro, até chegar ao domínio do destinatário, atuam como {{c1::MTA (Mail Transfer Agent)}}.',
  b=[regra('<b>MTA</b> = <i>Transfer</i> Agent, o agente de <b>transferência</b>. Cada MTA repassa a mensagem um "salto" adiante, por SMTP, na porta 25.'), esquema(percurso(2, 3))],
  m='MTA = repassa de servidor em servidor (SMTP, porta 25).',
  alvo='Papel do MTA.', fx=('rfc5598','rfc5321'), sol='Lacuna: MTA. RFC 5598: o MTA repassa a mensagem por um salto; RFC 5321: relaying por SMTP.',
  alt='Testei MDA: entrega na caixa postal final, não repassa entre servidores.',
  rec='"De um servidor para outro" determina o MTA.', fb='Extra decodifica Transfer e liga ao SMTP/porta 25.', cob={'1': ['D02']}),
 dict(k='C04', tags='Arquitetura_Email',
  t='No servidor do destinatário, o componente que faz a entrega final, depositando a mensagem na caixa postal dele, é o {{c1::MDA (Mail Delivery Agent)}}.',
  b=[regra('<b>MDA</b> = <i>Delivery</i> Agent, o agente de <b>entrega</b>. Depois dele, o destinatário lê a mensagem no próprio MUA, por POP3 ou IMAP.'), esquema(percurso(4))],
  m='MDA = entrega final na caixa postal do destinatário.',
  alvo='Papel do MDA.', fx=('rfc5598',), sol='Lacuna: MDA. RFC 5598: o MDA faz a entrega na caixa postal.',
  alt='Testei MTA: repassa, mas a entrega final na caixa postal é do MDA.',
  rec='"Entrega final na caixa postal" determina o MDA.', fb='Extra decodifica Delivery e mostra o que vem depois.', cob={'1': ['D01']}),
 dict(k='C05', tags='Portas',
  t='Na transferência de mensagens entre servidores de e-mail, o SMTP usa, por padrão, a porta TCP {{c1::25}}.',
  b=[regra('A <b>25</b> é a porta registrada do SMTP para o <b>repasse entre servidores</b> (MTA → MTA). A submissão pelo usuário autenticado usa a 587 (STARTTLS) ou a 465 (TLS implícito).'), esquema(T_PORTAS)],
  m='SMTP entre servidores = porta 25.',
  alvo='Porta padrão do SMTP no repasse entre servidores.', fx=('rfc5321','rfc6409'),
  sol='Lacuna: 25. RFC 5321, 4.5.4.2 (porta 25 registrada na IANA); RFC 6409 confirma que o repasse continua na 25 e a submissão usa 587.',
  alt='Testei 587 e 465: são de submissão pelo usuário, não de repasse entre servidores; a frente especifica "entre servidores".',
  rec='Contexto "entre servidores" determina 25 e afasta 587/465.', fb='Extra separa repasse de submissão; tabela de portas.', cob={'1': ['D03', 'D12']}),
 dict(k='C06', tags='Portas',
  t='Sem TLS, o servidor POP3 aguarda conexões, por padrão, na porta TCP {{c1::110}}.',
  b=[regra('O POP3 escuta na <b>110</b>. Com TLS implícito (POP3S), a porta é a 995.'), esquema(T_PORTAS)],
  m='POP3 = porta 110 (POP3S = 995).',
  alvo='Porta padrão do POP3.', fx=('rfc1939','rfc8314'), sol='Lacuna: 110 (RFC 1939).',
  alt='Testei 995 (POP3S) e 143 (IMAP): a frente fixa POP3 e "sem TLS".',
  rec='Protocolo e "sem TLS" determinam a porta.', fb='Extra traz a versão segura e a tabela de portas.', cob={'1': ['D04']}),
 dict(k='C07', tags='Portas',
  t='Sem TLS, o servidor IMAP aguarda conexões, por padrão, na porta TCP {{c1::143}}.',
  b=[regra('O IMAP escuta na <b>143</b>. Com TLS implícito (IMAPS), a porta é a 993.'), esquema(T_PORTAS)],
  m='IMAP = porta 143 (IMAPS = 993).',
  alvo='Porta padrão do IMAP.', fx=('rfc9051','rfc8314'), sol='Lacuna: 143 (RFC 9051, seção 2.1).',
  alt='Testei 993 (IMAPS) e 110 (POP3): a frente fixa IMAP e "sem TLS".',
  rec='Protocolo e "sem TLS" determinam a porta.', fb='Extra traz a versão segura e a tabela de portas.', cob={'1': ['D04']}),
]

# ---------------------------------------------------------------- desafiadores (D)
def rub(c, de, op, cmp, au, fb, ling, ut):
    k = ('correcao','determinacao','operacao_d','comparacao','autoria','feedback','linguagem_didatica','utilidade')
    return {key: {'resultado': ('PENDENTE' if (key == 'comparacao' and val.startswith('PENDENTE')) else 'PASSA'),
                  'evidencia': val.replace('PENDENTE: ', '')} for key, val in zip(k, (c, de, op, cmp, au, fb, ling, ut))}

D = [
 dict(k='D01', g='C', tags='Arquitetura_Email',
  f='Paula, do provedor A, envia um e-mail a Rui, do provedor B. Um servidor de A confere o login de Paula e aceita a mensagem; ela é repassada até B, onde outro componente a coloca na caixa postal de Rui. O componente que conferiu o login é o MSA, e o que colocou a mensagem na caixa postal é o MDA.',
  b=[regra('Cada agente tem uma função: <b>MSA</b> (submissão) aceita a mensagem do autor e exige login; <b>MTA</b> (transferência) repassa entre servidores; <b>MDA</b> (entrega) deposita na caixa postal; <b>MUA</b> é o programa do usuário.'),
     caso('"Conferiu o login e aceitou" é submissão → <b>MSA</b>. "Colocou na caixa postal" é entrega → <b>MDA</b>.'),
     esquema(percurso(1, 4))],
  m='Login e aceite = MSA; entrega na caixa postal = MDA; entre eles, os MTAs repassam.',
  alvo='Identificar MSA e MDA pelas ações descritas.', op='Mapear ações concretas (autenticar/aceitar; depositar) aos papéis da arquitetura.',
  regra='MSA aceita e autentica a submissão; MDA entrega na caixa postal (RFC 5598; RFC 6409).', dado='As ações "confere o login e aceita" e "coloca na caixa postal".',
  solucao='Autenticar e aceitar = MSA; depositar na caixa = MDA; logo Certo.', erro='Chamar de MTA quem aceita a mensagem ou quem entrega, por ser "servidor".',
  conc='Testei a leitura de que o servidor de A seria MTA: ele também repassa, mas a ação descrita (conferir login e aceitar) é a de submissão; conclusão mantida.',
  orig='Situação autoral com dois provedores e ações concretas; não há item Cebraspe localizado com essa estrutura.', fx=('rfc5598','rfc6409'), refs=[], fid='inspiracao_geral',
  lim='Nenhum item CESPE/Cebraspe C/E sobre MSA/MDA foi localizado nas buscas em cadernos oficiais (MPTO 2024, EMBRAPA 2024, ANP 2022, CAU/BR 2023, PCDF 2024, PF 2018, PRF 2021); construção baseada no conteúdo das RFCs.',
  rb=rub('Conferido com RFC 5598 (papéis) e RFC 6409 (autenticação no MSA).','Ações descritas sem ambiguidade; cada uma corresponde a um papel único.','Exige associar ações a papéis, não lembrar definição isolada.','PENDENTE: sem item Cebraspe específico localizado; inspiração geral declarada.','Cenário e redação autorais.','Verso traz a regra dos quatro papéis, o dado decisivo no bloco "No caso", o fluxo visual e o Memorize.','Frases curtas, quem faz o quê explícito; siglas expandidas no verso.','Cobre as notas Cloze do MSA (C02) e do MDA (C04).')),
 dict(k='D02', g='E', tags='Arquitetura_Email',
  f='Rui lê, no aplicativo de e-mail do celular configurado com IMAP, a mensagem que chegou à sua caixa postal no servidor. Nessa situação, o aplicativo de Rui atua como MTA, pois é ele que retira a mensagem do servidor para exibi-la.',
  b=[regra('O programa que o usuário usa para ler e escrever é o <b>MUA</b> (User Agent). O <b>MTA</b> (Transfer Agent) é o servidor que repassa mensagens a outros servidores, por SMTP.'),
     erro('Acessar a caixa postal por IMAP ou POP3 é tarefa do <b>MUA</b>; "retirar do servidor para exibir" não é transferência entre servidores.'),
     esquema(percurso(2, 3, 5))],
  m='O app de Rui é MUA; MTA é só o repasse entre servidores.',
  alvo='Distinguir MUA de MTA.', op='Classificar o papel do aplicativo do destinatário a partir da ação (ler a caixa por IMAP).',
  regra='MUA é o agente do usuário; MTA repassa entre servidores (RFC 5598).', dado='Aplicativo do celular lendo a caixa postal por IMAP.',
  solucao='Ler a caixa = MUA; repasse entre servidores = MTA; a frase atribui MTA ao aplicativo, logo Errado.', erro='Achar que "retirar do servidor" é transferência (MTA).',
  conc='Testei se algum aplicativo pode ser MTA: um cliente não faz repasse entre servidores; a justificativa "retira do servidor" não caracteriza MTA.',
  orig='Situação autoral que completa a de D01 do lado do destinatário.', fx=('rfc5598',), refs=[], fid='inspiracao_geral',
  lim='Nenhum item CESPE/Cebraspe C/E sobre MUA/MTA foi localizado nas buscas em cadernos oficiais; construção baseada na RFC 5598.',
  rb=rub('Conferido com RFC 5598: MUA atua para o usuário; MTA repassa um "salto".','Um só papel possível para o aplicativo; justificativa testada.','Exige distinguir papéis pela ação; a frase traz justificativa plausível a julgar.','PENDENTE: sem item Cebraspe específico localizado; inspiração geral declarada.','Redação e situação autorais.','Bloco de erro localiza a falha na justificativa; fluxo visual; Memorize com a formulação correta.','Linguagem direta; siglas explicadas no verso.','Cobre as notas Cloze do MUA (C01) e do MTA (C03).')),
 dict(k='D03', g='E', tags='Portas',
  f='O firewall de um órgão bloqueia todo o tráfego de saída, exceto nas portas TCP 80 e 443. O servidor de e-mail do órgão precisa repassar mensagens diretamente aos servidores de e-mail de outros domínios. Nessa configuração, o repasse funcionará, pois a transferência de e-mail entre servidores usa HTTPS.',
  b=[regra('A transferência de mensagens entre servidores de e-mail é feita pelo <b>SMTP</b>, que usa por padrão a <b>porta TCP 25</b>.'),
     erro('A justificativa está errada: o repasse não usa HTTPS (443). Com a porta 25 de saída bloqueada, o servidor do órgão <b>não consegue</b> entregar mensagens aos outros domínios.'),
     esquema(T_PORTAS)],
  m='Servidor → servidor é SMTP na porta 25; sem a 25 liberada, o repasse não sai.',
  alvo='Associar o repasse entre servidores ao SMTP/porta 25.', op='Avaliar se uma regra de firewall permite um serviço, identificando protocolo e porta.',
  regra='Repasse entre servidores usa SMTP na porta 25 (RFC 5321; RFC 6409).', dado='Só 80 e 443 liberadas; repasse direto a outros domínios.',
  solucao='Repasse exige 25; 25 bloqueada; justificativa (HTTPS) falsa; logo Errado.', erro='Achar que todo serviço da internet passa por HTTPS.',
  conc='Considerei relay por um provedor externo via HTTPS (API): a frente diz "diretamente aos servidores de outros domínios", o que exige SMTP.',
  orig='Inspirado na operação do item 65 (EMBRAPA): firewall × porta do serviço de e-mail; situação, portas liberadas e conclusão reconstruídas.', fx=('rfc5321','rfc6409'), refs=['EMBRAPA24_65'], fid='comparada',
  cmp='Mesma operação (identificar porta exigida pelo envio de e-mail sob regra de firewall), com gabarito invertido e justificativa a julgar.',
  rb=rub('Conferido com RFC 5321 (porta 25) e RFC 6409 (repasse na 25).','"Diretamente" afasta intermediários; só uma conclusão.','Aplica conhecimento de porta a uma regra de firewall.','Compara com EMBRAPA 2024, item 65 (gabarito definitivo C).','Cenário inverso e com justificativa, não paráfrase do item.','Erro localizado na justificativa, consequência explicada, tabela de portas e Memorize.','Termos "firewall" e "porta" usados em contexto simples; verso explica.','Cobre a nota Cloze C05 (porta 25).')),
 dict(k='D04', g='C', tags='Portas',
  f='Em uma rede, o firewall bloqueia a porta TCP 110 e libera a porta TCP 143. O servidor de e-mail oferece POP3 e IMAP sem TLS, nas portas padrão. Nessa situação, um cliente de e-mail configurado com IMAP conseguirá acessar a caixa postal, mas um configurado com POP3 não conseguirá.',
  b=[regra('Portas padrão sem TLS: <b>POP3 = 110</b> e <b>IMAP = 143</b>.'),
     caso('Com a 110 bloqueada, o cliente POP3 não alcança o servidor; com a 143 liberada, o cliente IMAP funciona normalmente.'),
     esquema(tabela(['Protocolo', 'Porta', 'No firewall', 'Resultado'], [['POP3', '110', 'Bloqueada', 'Não acessa'], ['IMAP', '143', 'Liberada', '<b>Acessa</b>']]))],
  m='110 é do POP3 e 143 é do IMAP: bloqueou a 110, só o IMAP continua.',
  alvo='Portas 110 (POP3) e 143 (IMAP) aplicadas.', op='Deduzir o efeito de bloqueio/liberação de portas sobre cada protocolo.',
  regra='POP3 = 110; IMAP = 143 (RFC 1939; RFC 9051).', dado='110 bloqueada, 143 liberada, servidores nas portas padrão sem TLS.',
  solucao='IMAP via 143 funciona; POP3 via 110 falha; logo Certo.', erro='Inverter as portas dos dois protocolos.',
  conc='Considerei portas TLS (993/995): a frente fixa "sem TLS, nas portas padrão", eliminando essa leitura.',
  orig='Mesma família operacional do item EMBRAPA 65 (porta × serviço sob firewall), aplicada a protocolos de recebimento; redação autoral.', fx=('rfc1939','rfc9051'), refs=['EMBRAPA24_65'], fid='comparada',
  cmp='Transfere a operação porta → serviço do item 65 para POP3/IMAP; gabarito próprio conferido nas RFCs.',
  rb=rub('Conferido: RFC 1939 (110) e RFC 9051 (143).','Hipóteses explícitas (sem TLS, portas padrão).','Dedução sobre duas configurações a partir das portas.','Compara com EMBRAPA 2024, item 65.','Situação nova, com dois protocolos.','Regra, aplicação ao caso, tabela de resultado e Memorize.','Curto e direto; termos técnicos mínimos.','Cobre as notas Cloze C06 (110) e C07 (143).')),
 dict(k='D05', g='C', tags='Protocolos',
  f='Um servidor público configurou o Thunderbird com IMAP como servidor de entrada e SMTP como servidor de saída. Certo dia, o servidor SMTP do provedor ficou fora do ar, mas o servidor IMAP continuou funcionando. Nessa situação, ele continuou conseguindo ler as mensagens da caixa postal, mas não conseguiu enviar novas mensagens.',
  b=[regra('Cada protocolo tem sua função: o <b>IMAP</b> dá acesso às mensagens guardadas no servidor (recebimento); o <b>SMTP</b> envia as mensagens.'),
     caso('Só o SMTP falhou: a <b>leitura</b> (IMAP) continua possível, mas o <b>envio</b> (SMTP) fica impedido.'),
     certo('O erro comum seria achar que o mesmo protocolo faz as duas coisas, ou trocar as funções (SMTP para receber, POP/IMAP para enviar).'),
     esquema(T_PROTOCOLOS)],
  m='Entrada (IMAP/POP3) e saída (SMTP) são independentes: cai o SMTP, para o envio, mas a leitura segue.',
  alvo='Funções separadas de IMAP (receber) e SMTP (enviar).', op='Inferir a consequência da falha de um protocolo sobre envio e leitura.',
  regra='SMTP envia; IMAP acessa a caixa (RFC 5321; RFC 9051).', dado='SMTP fora do ar, IMAP funcionando.',
  solucao='Leitura depende de IMAP (ok); envio depende de SMTP (falha); logo Certo.', erro='Supor que o servidor de entrada também envia, ou trocar os papéis.',
  conc='Considerei envio via webmail do provedor: a frente trata do Thunderbird configurado com SMTP; o webmail não está em jogo.',
  orig='Inspirado na operação do item 99 (MPTO 2024): papéis trocados dos protocolos; aqui o aluno aplica os papéis a uma falha concreta.', fx=('rfc5321','rfc9051'), refs=['MPTO24_99'], fid='comparada',
  cmp='O item 99 cobra a função de cada protocolo; este D exige aplicar essa função para prever consequência de falha.',
  rb=rub('Conferido nas RFCs 5321 e 9051.','Falha isolada e configuração explícita.','Exige inferir efeito, não só lembrar função.','Compara com MPTO 2024, item 99 (gabarito definitivo E).','Situação nova, sem reutilizar texto do item.','Regra, aplicação, confusão concorrente, tabela e Memorize.','Situação cotidiana, sem jargão desnecessário.','Aplica R01/R02/R03 a um caso.')),
 dict(k='D06', g='E', tags='Protocolos',
  f='Carla configurou sua conta de e-mail no notebook com POP3, no modo padrão, que apaga as mensagens do servidor depois de baixá-las. Mais tarde, configurou a mesma conta no celular com IMAP. Nessa situação, as mensagens que o notebook já havia baixado aparecerão no celular, pois o IMAP mantém a conta sincronizada.',
  b=[regra('O <b>IMAP</b> sincroniza o que está <b>no servidor</b>. O <b>POP3</b>, no modo padrão, baixa as mensagens e as apaga do servidor.'),
     erro('As mensagens baixadas pelo notebook saíram do servidor e ficaram só nele; o celular, via IMAP, <b>não tem de onde buscá-las</b>. Sincronizar não recupera dados de outro aparelho.'),
     esquema(fluxo(['Notebook (POP3) baixa', 'Servidor apaga', 'Celular (IMAP) não encontra']))],
  m='IMAP só mostra o que ainda está no servidor; o que o POP3 apagou de lá não aparece no celular.',
  alvo='Limite da sincronização do IMAP diante da remoção feita pelo POP3.', op='Combinar o comportamento de dois protocolos na mesma conta para prever o resultado.',
  regra='POP3 baixa e, no modo padrão, remove do servidor; IMAP trabalha sobre o que está no servidor (RFC 1939; RFC 9051).', dado='POP3 no modo que apaga do servidor; IMAP configurado depois.',
  solucao='Mensagens saíram do servidor antes; IMAP não as encontra; justificativa não salva a conclusão; logo Errado.', erro='Achar que "sincronizar" recupera dados de outro aparelho.',
  conc='Considerei a opção "deixar cópia no servidor": a frente fixa o modo que apaga, eliminando essa leitura.',
  orig='Situação autoral; o material cita itens de outras bancas (AOCP) sobre POP3/IMAP, não usados como referência Cebraspe.', fx=('rfc1939','rfc9051'), refs=[], fid='inspiracao_geral',
  lim='Os itens sobre POP3 × IMAP localizados com gabarito eram de outras bancas (AOCP/UFOB) ou de bancos sem caderno oficial; nenhum item Cebraspe C/E oficial específico foi confirmado.',
  rb=rub('Conferido nas RFCs 1939 e 9051.','Modo do POP3 explicitado; ordem dos fatos clara.','Combina dois comportamentos para chegar à conclusão.','PENDENTE: sem item Cebraspe oficial específico confirmado; inspiração geral declarada.','Cenário autoral.','Erro localizado com fluxo visual do que aconteceu e Memorize.','Linguagem cotidiana; termos POP3/IMAP explicados no verso.','Transfere R03/R04 a um caso de uso real.')),
 dict(k='D07', g='C', tags='Campos_Cabecalho',
  f='Um coordenador envia um aviso a 40 candidatos. Põe o próprio endereço em Para, o da chefia em Cc e os 40 candidatos em Cco. Nessa situação, em regra, cada candidato verá o endereço da chefia, mas não o dos demais candidatos.',
  b=[regra('Endereços em <b>Para</b> e <b>Cc</b> são visíveis a todos os destinatários; endereços em <b>Cco</b> (Bcc) não são revelados aos outros.'),
     caso('Cada candidato vê o coordenador (Para) e a chefia (Cc), mas <b>não</b> os outros candidatos (Cco).'),
     esquema(T_CAMPOS)],
  m='O campo define a visibilidade: Para e Cc aparecem para todos; Cco não aparece para ninguém.',
  alvo='Aplicar visibilidade de Para/Cc/Cco.', op='Prever o que cada destinatário vê conforme o campo usado.',
  regra='Para e Cc visíveis; Bcc não revelado aos demais (RFC 5322, 3.6.3).', dado='Chefia em Cc; candidatos em Cco.',
  solucao='Chefia visível (Cc); candidatos ocultos entre si (Cco); logo Certo.', erro='Achar que quem está em Cco não vê ninguém, ou que Cc também oculta.',
  conc='Considerei implementações em que a cópia do Bcc mostra a linha Bcc (RFC 5322, método 2); por isso a frente usa "em regra"; nos clientes usuais (Outlook, Gmail) cada Cco não vê os outros.',
  orig='Situação autoral de uso legítimo do Cco com contraste Cc.', fx=('rfc5322',), refs=[], fid='inspiracao_geral',
  lim='Itens Cebraspe sobre Cco localizados apenas em bancos não oficiais, sem caderno/gabarito oficial confirmado nesta tarefa.',
  rb=rub('Conferido com RFC 5322, 3.6.3.','"Em regra" delimita a variação de implementação registrada na RFC.','Exige combinar dois campos para prever a visibilidade.','PENDENTE: sem item Cebraspe oficial confirmado; inspiração geral declarada.','Cenário autoral, diferente do exemplo da festa do material.','Regra, aplicação ao caso, tabela de visibilidade e Memorize.','Situação simples, sem jargão.','Aplica R07/R08 a uma decisão prática.')),
 dict(k='D08', g='E', tags='Respostas',
  f='Lia enviou uma mensagem para Bruno (campo Para), com Caio em Cc e Davi em Cco. Bruno usou a opção Responder a todos. A resposta de Bruno chegará a Lia, Caio e Davi.',
  b=[regra('<b>Responder a todos</b> envia ao remetente original e aos endereços que estavam em <b>Para</b> e <b>Cc</b>.'),
     erro('Davi estava em <b>Cco</b>: o endereço dele não aparece na mensagem que Bruno recebeu. A resposta vai para Lia e Caio, <b>não</b> para Davi.'),
     esquema(tabela(['Pessoa', 'Campo', 'Recebe a resposta de Bruno?'], [['Lia', 'Remetente', 'Sim'], ['Caio', 'Cc', 'Sim'], ['Davi', 'Cco', '<b>Não</b>']]))],
  m='Responder a todos nunca alcança o Cco: a resposta de Bruno chega só a Lia e Caio.',
  alvo='Alcance de Responder a todos com destinatário em Cco.', op='Combinar a regra do Cco com a do comando de resposta.',
  regra='Responder a todos = remetente + Para + Cc (Microsoft); Bcc não revelado (RFC 5322).', dado='Davi em Cco; Bruno responde a todos.',
  solucao='Bruno não vê Davi; resposta vai a Lia e Caio; logo Errado.', erro='Achar que "todos" inclui quem estava oculto.',
  conc='Considerei Davi usando Responder a todos (caso diferente e controverso em comentários): a frente trata da resposta de Bruno, que não conhece Davi.',
  orig='Inspirado no item 26 (ANP 2022), que cobra o efeito de um comando de resposta/encaminhamento sobre os destinatários; situação reconstruída com Cco.', fx=('ms_reply','rfc5322'), refs=['ANP22_26'], fid='comparada',
  cmp='Mesma operação (a quem o comando envia), acrescida do dado decisivo Cco.',
  rb=rub('Conferido com Microsoft (Responder a todos) e RFC 5322 (Bcc).','Papéis e campos explícitos; caso de Davi responder excluído.','Combina duas regras.','Compara com ANP 2022, item 26 (gabarito definitivo E).','Situação autoral com quatro pessoas.','Erro localizado, tabela pessoa a pessoa e Memorize com a formulação correta.','Nomes curtos e campos entre parênteses facilitam a leitura.','Aplica R07/R09.')),
 dict(k='D09', g='E', tags='Respostas',
  f='No Outlook, Marcos recebeu um e-mail com um relatório anexado e precisa que Joana, que não estava entre os destinatários, receba o arquivo. Se ele usar Responder a todos e acrescentar o endereço de Joana, o anexo original irá junto; se usar Encaminhar, o anexo não irá.',
  b=[regra('<b>Encaminhar</b> repassa a mensagem a outra pessoa e <b>mantém os anexos</b>. <b>Responder</b> e <b>Responder a todos</b> não incluem os anexos originais (seria devolvê-los a quem já os tem).'),
     erro('A frase inverte os comandos. Para Joana receber o relatório sem reanexar, Marcos deve usar <b>Encaminhar</b>.'),
     esquema(T_COMANDOS)],
  m='Para mandar o anexo a quem não estava na conversa: Encaminhar. Responder não leva anexo.',
  alvo='Escolher o comando que leva o anexo a um novo destinatário.', op='Decidir entre comandos pela consequência sobre o anexo.',
  regra='Encaminhar inclui anexos; responder não (Microsoft Support).', dado='Joana não estava na conversa; arquivo anexado no original.',
  solucao='Responder a todos não leva o anexo; Encaminhar leva; a frase inverte; logo Errado.', erro='Inverter o comportamento dos comandos quanto aos anexos.',
  conc='Considerei a opção de anexar manualmente na resposta: a frente fala do anexo original indo junto, o que não ocorre ao responder.',
  orig='Inspirado no item 26 (ANP 2022) sobre o comando Encaminhar no Outlook; aqui o alvo é o anexo, em situação autoral.', fx=('ms_reply',), refs=['ANP22_26'], fid='comparada',
  cmp='Mesma ferramenta e família (efeito de Encaminhar × responder), com dado decisivo diferente (anexo).',
  rb=rub('Conferido com a página da Microsoft sobre responder/encaminhar.','Comandos e objetivo explícitos; uma conclusão.','Exige escolher comando pela consequência.','Compara com ANP 2022, item 26.','Situação nova (anexo e terceira pessoa).','Regra, erro com a ação correta, tabela de comandos e Memorize.','Linguagem de escritório, sem termos técnicos.','Aplica R10 a uma decisão.')),
 dict(k='D10', g='E', tags='Seguranca_Email',
  f='Um servidor quer que os destinatários possam comprovar que os e-mails foram mesmo enviados por ele e que não foram alterados no caminho. Para isso, configurou no Outlook uma assinatura com nome, cargo e telefone, inserida automaticamente ao fim de cada mensagem. Essa configuração atende ao objetivo.',
  b=[regra('A <b>assinatura comum</b> do Outlook é só um bloco de texto que qualquer pessoa pode copiar. A <b>assinatura digital</b> usa um certificado (ID digital) e permite verificar <b>quem assinou</b> e se a mensagem <b>foi alterada</b>.'),
     erro('Nome, cargo e telefone no fim da mensagem não provam autoria nem integridade. O objetivo exige <b>assinatura digital</b>.'),
     esquema(T_ASSINATURA)],
  m='Provar autoria e integridade = assinatura digital com certificado; assinatura de texto é só cartão de visita.',
  alvo='Distinguir assinatura de texto de assinatura digital.', op='Avaliar se um recurso atende a um requisito de segurança (autenticidade e integridade).',
  regra='Assinatura digital usa ID digital e garante autenticidade e integridade; assinatura comum não (Microsoft).', dado='Assinatura configurada com nome, cargo e telefone.',
  solucao='Bloco de texto não comprova autoria nem integridade; logo Errado.', erro='Confundir o nome "assinatura" do Outlook com assinatura digital.',
  conc='Considerei se a assinatura de texto poderia conter um certificado: a frente descreve apenas nome, cargo e telefone.',
  orig='Inspirado no item 20 (CAU/BR 2023), que confunde Inserir Assinatura com assinatura digital; situação reconstruída a partir do requisito.', fx=('ms_digsig',), refs=['CAU23_20'], fid='comparada',
  cmp='Mesma distinção, partindo de um objetivo de segurança em vez do nome do menu.',
  rb=rub('Conferido com a página da Microsoft sobre assinatura digital.','Objetivo e configuração explícitos.','Exige confrontar requisito e recurso.','Compara com CAU/BR 2023, item 20 (gabarito definitivo E).','Redação autoral orientada ao requisito.','Regra, erro, tabela comparativa e Memorize com a solução correta.','Termos autenticidade/integridade traduzidos em "quem enviou" e "não alterado".','Liga a parte "Assinatura" do corpo do e-mail à segurança.')),
 dict(k='D11', g='C', tags='Seguranca_Email',
  f='Um provedor oferece envio de e-mail por SMTP na porta 587 com STARTTLS ou na porta 465 com TLS implícito. Um usuário configura seu cliente de e-mail com uma dessas opções. Nesse caso, a conexão entre o cliente e o servidor de envio trafega criptografada, ainda que o SMTP, por si só, não preveja criptografia.',
  b=[regra('O SMTP não cifra nada sozinho; a proteção vem do <b>TLS</b>.'),
     caso('No <b>STARTTLS</b> (587), a conexão começa sem cifra e é convertida para TLS; no <b>TLS implícito</b> (465), já começa cifrada. Nos dois, o trecho cliente → servidor de envio fica protegido.'),
     certo('Limite: isso protege a <b>conexão</b>, não o conteúdo de ponta a ponta; para cifrar a mensagem em si, usa-se S/MIME ou PGP.'),
     esquema(T_TLS)],
  m='587+STARTTLS ou 465+TLS cifram a conexão de envio; o SMTP puro não cifra.',
  alvo='Origem da criptografia no envio (TLS) e seu alcance.', op='Julgar o efeito de uma configuração de segurança sobre o trecho de rede.',
  regra='STARTTLS na 587 e TLS implícito na 465 protegem a submissão (RFC 8314).', dado='Cliente configurado com 587+STARTTLS ou 465+TLS.',
  solucao='Ambas as opções cifram a conexão de submissão; SMTP puro não cifra; logo Certo.', erro='Achar que a criptografia é do SMTP ou que vale de ponta a ponta.',
  conc='Considerei falha na negociação STARTTLS: a frente assume a configuração escolhida funcionando; a afirmação limita-se ao trecho cliente → servidor.',
  orig='Situação autoral; o material traz item inédito do próprio curso sobre SMTP e criptografia, não usado como referência Cebraspe.', fx=('rfc8314',), refs=[], fid='inspiracao_geral',
  lim='Nenhum item CESPE/Cebraspe C/E oficial sobre STARTTLS/TLS implícito no e-mail foi localizado nas buscas desta tarefa.',
  rb=rub('Conferido com RFC 8314, seções 3.1–3.3.','Trecho delimitado (cliente → servidor de envio).','Aplica a regra a uma configuração concreta e separa conexão de conteúdo.','PENDENTE: sem item Cebraspe oficial localizado; inspiração geral declarada.','Redação autoral.','Regra, aplicação aos dois modos, limite, tabela e Memorize.','Siglas explicadas no verso em palavras simples.','Aplica R12 e prepara itens de segurança.')),
 dict(k='D12', g='C', tags='Webmail_Cliente',
  f='Em um computador, o firewall só libera a saída nas portas TCP 80 e 443. O usuário acessa seu e-mail pelo webmail do provedor, no navegador. Nessa situação, ele consegue enviar mensagens a outros domínios, pois o navegador fala com o provedor por HTTPS, e o repasse por SMTP é feito pelos servidores do provedor.',
  b=[regra('No <b>webmail</b>, o navegador se comunica com o provedor por <b>HTTP/HTTPS</b> (portas 80/443). Quem envia a mensagem aos outros domínios, por SMTP (porta 25), são os <b>servidores do provedor</b>.'),
     caso('O bloqueio das demais portas no computador não impede o envio, porque o SMTP não sai do computador do usuário.'),
     certo('Um cliente instalado (Outlook, Thunderbird) precisaria das portas de SMTP, IMAP ou POP3, que estão bloqueadas.'),
     esquema(fluxo(['Navegador', 'HTTPS (443)', 'Provedor', 'SMTP (25)', 'Outros domínios']))],
  m='No webmail, o computador só usa HTTPS; o SMTP fica a cargo do provedor.',
  alvo='Divisão de tarefas no webmail (HTTPS no navegador; SMTP nos servidores).', op='Inferir se o envio funciona dada a regra de firewall e a forma de acesso.',
  regra='Webmail usa HTTP/HTTPS entre navegador e provedor; o repasse SMTP ocorre entre servidores (RFC 5598; RFC 5321).', dado='Só 80/443 liberadas no computador; acesso por webmail.',
  solucao='Navegador usa 443 (liberada); SMTP sai dos servidores do provedor; logo Certo.', erro='Achar que o computador do usuário precisa da porta 25 também no webmail.',
  conc='Considerei bloqueio no lado do provedor: a frente restringe o firewall ao computador do usuário.',
  orig='Contraponto autoral ao D03, inspirado na mesma família do item 65 (EMBRAPA): o serviço de e-mail exige SMTP, mas no webmail quem usa SMTP é o provedor.', fx=('rfc5598','rfc5321'), refs=['EMBRAPA24_65'], fid='comparada',
  cmp='Mesma operação (porta necessária ao envio sob firewall), com a variável decisiva "forma de acesso".',
  rb=rub('Conferido com RFC 5598 (MUA web) e RFC 5321 (repasse SMTP).','Firewall no computador e acesso via navegador explícitos.','Exige localizar onde cada protocolo opera.','Compara com EMBRAPA 2024, item 65.','Situação autoral, contraste com D03.','Regra, aplicação, contraste com cliente instalado, fluxo visual e Memorize.','Linguagem direta, portas explicadas.','Cobre a nota Cloze C05 (porta 25) e aplica R05.')),
]

# ---------------------------------------------------------------- montagem
def row_r(x): return [x['f'], verso_ce(x['g'], x['b'], x['m']), f"{BASE} {x['tags']} {R_TAG}"]
def row_d(x): return [frente(x['f']), verso_ce(x['g'], x['b'], x['m']), f"{BASE} {x['tags']} {D_TAG}"]
def row_c(x): return [frente(x['t']), extra_cloze(x['b'], x['m']), f"{BASE} {x['tags']}"]

for x in CZ:
    assert x['t'].count('{{c1::') == 1, x['k']  # 2.15: uma omissão por nota (sem mnemônicos neste lote)

ce_items = [('R', x) for x in R] + [('D', x) for x in D]
random.Random(808).shuffle(ce_items)
ce_rows, line_of = [], {}
for n, (kind, x) in enumerate(ce_items, 1):
    ce_rows.append(row_r(x) if kind == 'R' else row_d(x)); line_of[x['k']] = n
cz_rows = [row_c(x) for x in CZ]

OUT.mkdir(parents=True, exist_ok=True); (OUT / 'relatorios').mkdir(exist_ok=True)
def write_tsv(name, rows):
    data = ('\n'.join('\t'.join(r) for r in rows) + '\n').encode('utf-8')
    (OUT / name).write_bytes(data); return data
items = {'anki_certo_errado.tsv': write_tsv('anki_certo_errado.tsv', ce_rows),
         'anki_cloze.tsv': write_tsv('anki_cloze.tsv', cz_rows)}

cal = {'schema_version': 1, 'referencias': REFS, 'cartoes': []}
for x in D:
    n = line_of[x['k']]; row = ce_rows[n - 1]
    rec = dict(id=x['k'], linha=n, sha256=fingerprint(row), gabarito=x['g'], alvo=x['alvo'], operacao_autoral=x['op'],
               regra=x['regra'], dado_decisivo=x['dado'], solucao=x['solucao'], erro_plausivel=x['erro'],
               leitura_concorrente=x['conc'], originalidade=x['orig'], fontes_conteudo=urls(*x['fx']), referencias=x['refs'],
               fidelidade=x['fid'], segunda_conferencia=True, decisao='APROVAR', rubrica=x['rb'])
    rec['comparacao' if x['fid'] == 'comparada' else 'limitacao'] = x['cmp'] if x['fid'] == 'comparada' else x['lim']
    cal['cartoes'].append(rec)
(OUT / 'relatorios' / 'calibracao_cebraspe.json').write_text(json.dumps(cal, ensure_ascii=False, indent=1), encoding='utf-8')

def rid(k): return f'anki_certo_errado.tsv:{line_of[k]}'
rev = {'schema_version': 1, 'sha256_lote': batch_hash(items),
       'revisor': 'Claude (assistente de IA, modelo Opus 5.5) — mesmo agente que redigiu os cartões',
       'tipo_revisao': 'autorevisao', 'cartoes': [], 'sinais': []}
for x in R:
    row = ce_rows[line_of[x['k']] - 1]
    rev['cartoes'].append(dict(id=rid(x['k']), sha256=fingerprint(row), alvo=x['alvo'], solucao=x['sol'], fontes=fontes(*x['fx']),
        alternativa_concorrente=x['alt'], recuperacao=x['rec'], feedback=x['fb'], segunda_conferencia=True, decisao='APROVAR'))
for i, x in enumerate(CZ, 1):
    rev['cartoes'].append(dict(id=f'anki_cloze.tsv:{i}', sha256=fingerprint(cz_rows[i - 1]), alvo=x['alvo'], solucao=x['sol'], fontes=fontes(*x['fx']),
        alternativa_concorrente=x['alt'], recuperacao=x['rec'], feedback=x['fb'],
        desafiadores_por_lacuna={g: [rid(k) for k in ks] for g, ks in x['cob'].items()}, segunda_conferencia=True, decisao='APROVAR'))
from validar_revisao_pedagogica import signals as _sinais_atuais
editorial = {f'anki_certo_errado.tsv:{n}': k for k, n in line_of.items()}
editorial.update({f'anki_cloze.tsv:{i}': x['k'] for i, x in enumerate(CZ, 1)})
motivos = json.loads(Path(__file__).with_name('sinais_resolvidos.json').read_text(encoding='utf-8'))
pendentes = []
for s in _sinais_atuais(items):
    chave = f"{editorial.get(s['id'], s['id'])}|{s['sinal']}"
    if chave in motivos:
        rev['sinais'].append({'sinal_id': s['sinal_id'], 'decisao': 'EXCECAO_JUSTIFICADA', 'motivo': motivos[chave]})
    else:
        pendentes.append(chave)
if pendentes:
    print('SINAIS PENDENTES (corrigir ou justificar em sinais_resolvidos.json):', ', '.join(pendentes))
(OUT / 'relatorios' / 'revisao_recuperacao.json').write_text(json.dumps(rev, ensure_ascii=False, indent=1), encoding='utf-8')

# ---------------------------------------------------------------- prévia visual (não vai para o Anki)
import re
def cloze_view(texto, revelar):
    return re.sub(r'\{\{c1::(.*?)\}\}', (lambda m: f'<span class="cloze">{m[1]}</span>') if revelar else
                  (lambda m: '<span class="cloze">[...]</span>'), texto)
cards = []
for (kind, x), row in zip(ce_items, ce_rows):
    cards.append((x['k'], row[0], row[1], row[2]))
for x, row in zip(CZ, cz_rows):
    cards.append((x['k'], cloze_view(row[0], False), cloze_view(row[0], True) + '<hr id="answer">' + row[1], row[2]))
pares = ''.join(
    f'<section><h2>{k} <small>{_html.escape(t)}</small></h2><div class="lado"><div class="card">{fr}</div>'
    f'<div class="card">{(fr + "<hr id=answer>" + vs) if not k.startswith("C") else vs}</div></div></section>'
    for k, fr, vs, t in cards)
previa = ('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
          '<title>Prévia dos cards — Correio Eletrônico</title><style>'
          'body{font-family:system-ui,sans-serif;margin:0;padding:16px;background:#eceff1;color:#222}'
          'body.noite{background:#1e1e1e;color:#ddd} h1{font-size:18px} h2{font-size:14px;margin:18px 0 6px} small{opacity:.6;font-weight:normal}'
          '.lado{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:10px}'
          '.card{font-family:arial;font-size:20px;text-align:center;background:white;color:black;padding:14px;border-radius:8px;max-width:520px}'
          'body.noite .card{background:#2f2f31;color:#e8e8e8} .cloze{font-weight:bold;color:blue} body.noite .cloze{color:#6ea8ff}'
          'button{padding:6px 12px;margin-bottom:8px}</style>'
          '<h1>Prévia dos cards (frente | verso) — imita o modelo Básico/Cloze padrão do Anki</h1>'
          '<button onclick="document.body.classList.toggle(\'noite\')">Alternar modo noturno</button>'
          + pares + '</html>')
(PASTA / 'previa_cards.html').write_text(previa, encoding='utf-8')

mapa = {x['k']: rid(x['k']) for x in R + D}
mapa.update({x['k']: f'anki_cloze.tsv:{i}' for i, x in enumerate(CZ, 1)})
print(json.dumps(mapa, ensure_ascii=False))
print('R', len(R), 'C/E', sum(x['g'] == 'C' for x in R), sum(x['g'] == 'E' for x in R))
print('D', len(D), 'C/E', sum(x['g'] == 'C' for x in D), sum(x['g'] == 'E' for x in D))
print('Cloze notas', len(CZ))
