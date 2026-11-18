"""Gera o lote Anki de Correio Eletrônico (PRF, Missão 08) e os registros de revisão.

Uso: python gerar_lote.py DIRETORIO_SAIDA CAMINHO_SKILLS
"""
import hashlib, json, random, sys
from pathlib import Path

OUT = Path(sys.argv[1]); SKILLS = Path(sys.argv[2])
sys.path.insert(0, str(SKILLS / 'gerar-revisao-anki' / 'scripts'))
from validar_revisao_pedagogica import batch_hash, fingerprint  # funções oficiais do projeto

HOJE = '2026-11-18'
BASE = 'Informatica Correio_Eletronico PRF Missao_08'
R_TAG, D_TAG = 'Tipo_Revisao_Rapida', 'Tipo_Desafiadora_Cebraspe Estilo_Cebraspe'
C = '✅ Certo<br><br>'; E = '❌ Errado<br><br>'

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
def fontes(*keys):
    return [{'url': F[k][0], 'consulta': HOJE, 'trecho': F[k][1]} for k in keys]
def urls(*keys):
    return [F[k][0] for k in keys]

# ---------------------------------------------------------------- referências Cebraspe (gabaritos oficiais conferidos)
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

# ---------------------------------------------------------------- cartões rápidos (R)
R = [
 dict(k='R01', tags='Protocolos',
  f='O SMTP (Simple Mail Transfer Protocol) é o protocolo de envio de e-mail, usado do programa do usuário até o servidor e entre servidores.',
  v=C+'O SMTP cuida do envio (transferência) das mensagens: é usado quando o programa do usuário entrega a mensagem ao servidor e quando um servidor repassa a mensagem ao servidor do destinatário. Para ler a caixa postal, o programa do usuário usa POP3 ou IMAP.<br><br>💡 Memorize: SMTP = Sua Mensagem Tá Partindo.',
  alvo='Função do SMTP: envio/transferência de mensagens (submissão e repasse entre servidores).', fx=('rfc5321','rfc6409'),
  sol='Certo: RFC 5321 define o SMTP para transferir mensagens e descreve o repasse entre servidores; a RFC 6409 usa SMTP também na submissão pelo cliente.',
  alt='Testei a leitura "SMTP também recebe": o servidor de destino recebe a mensagem de outro servidor por SMTP, mas o usuário lê a caixa por POP3/IMAP; a frase fala só de envio, então continua Certa.',
  rec='Exige recuperar a função do protocolo a partir do nome; a frente não diz que POP3/IMAP recebem.', fb='Verso separa envio (SMTP) de leitura (POP3/IMAP) e dá mnemônico do próprio material.'),
 dict(k='R02', tags='Protocolos',
  f='O POP3 (Post Office Protocol versão 3) é o protocolo usado pelo programa de e-mail para enviar as mensagens que o usuário escreveu.',
  v=E+'O POP3 é protocolo de recebimento: o programa do usuário o usa para baixar as mensagens da caixa postal no servidor. O envio é feito pelo SMTP.<br><br>Correção: o POP3 serve para receber (baixar) mensagens; o SMTP, para enviá-las.',
  alvo='Função do POP3: recebimento (download) de mensagens, não envio.', fx=('rfc1939','rfc5321'),
  sol='Errado: RFC 1939 define o POP3 para o cliente acessar a caixa postal e recuperar mensagens; envio é SMTP.',
  alt='Considerei clientes que usam POP3 e SMTP na mesma conta: ainda assim cada protocolo tem papel próprio; não há envio por POP3.',
  rec='Recupera a direção (receber × enviar) do POP3; a frente não oferece pista do papel correto.', fb='Verso corrige a troca de funções, erro explorado em item real (MPTO 2024, item 99).'),
 dict(k='R03', tags='Protocolos',
  f='No IMAP (Internet Message Access Protocol), as mensagens ficam no servidor, e o que se faz em um aparelho (ler, mover, apagar) aparece nos demais aparelhos da mesma conta.',
  v=C+'O IMAP permite trabalhar diretamente na caixa postal do servidor, como se as pastas remotas fossem locais. Por isso a conta fica sincronizada entre celular, notebook e webmail. O POP3, em regra, baixa as mensagens para o aparelho e as apaga do servidor.',
  alvo='Característica do IMAP: armazenamento no servidor e sincronização entre dispositivos.', fx=('rfc9051',),
  sol='Certo: RFC 9051 descreve a manipulação de caixas remotas equivalente a pastas locais e a ressincronização de clientes.',
  alt='Testei "IMAP só funciona on-line": a RFC prevê clientes off-line que ressincronizam, mas isso não afeta a afirmação, que trata de onde ficam as mensagens.',
  rec='Exige lembrar a propriedade distintiva do IMAP diante do POP3.', fb='Verso explica o porquê da sincronização e contrasta com POP3.'),
 dict(k='R04', tags='Protocolos',
  f='No POP3, em seu funcionamento padrão, as mensagens continuam guardadas no servidor e não são baixadas para o computador do usuário.',
  v=E+'O POP3 faz o contrário: baixa as mensagens para o dispositivo do usuário e, em regra, as remove do servidor depois do download (muitos programas permitem manter uma cópia). Quem mantém as mensagens no servidor é o IMAP.<br><br>Correção: no POP3, as mensagens são baixadas para o dispositivo local.',
  alvo='Comportamento padrão do POP3: download para o dispositivo local, em regra com remoção do servidor.', fx=('rfc1939',),
  sol='Errado: RFC 1939 trata o POP3 como recuperação da caixa postal, sem manipulação extensa no servidor; exclusão das marcadas ocorre no estado UPDATE.',
  alt='Considerei a opção "deixar cópia no servidor": ela existe, mas não torna a frase certa, porque a mensagem ainda é copiada para o computador.',
  rec='Recupera o local de armazenamento no POP3; não repete a frente do R03 (que trata do IMAP).', fb='Verso corrige e indica a exceção (cópia no servidor) para evitar absolutismo.'),
 dict(k='R05', tags='Webmail_Cliente',
  f='Para acessar um webmail, como o Gmail pelo navegador, basta um navegador com acesso à internet; não é necessário instalar um programa cliente de e-mail.',
  v=C+'Webmail é o acesso ao e-mail por uma página web. O navegador conversa com o servidor do provedor por HTTP/HTTPS, e o próprio provedor cuida do envio (SMTP) e do armazenamento. Por isso não é preciso instalar Outlook, Thunderbird ou similar.',
  alvo='Webmail: acesso pelo navegador, sem instalar cliente.', fx=('rfc5598','gmail_clients'),
  sol='Certo: na RFC 5598 o MUA pode ser uma interface web; o Gmail é usado no navegador e, opcionalmente, em clientes.',
  alt='Considerei a necessidade de "plugin" ou aplicativo: webmail não exige; aplicativo móvel é forma alternativa de acesso, não requisito.',
  rec='Recupera a característica definidora do webmail.', fb='Verso explica quem faz cada parte (navegador × provedor).'),
 dict(k='R06', tags='Webmail_Cliente',
  f='Os programas Mozilla Thunderbird e Microsoft Outlook instalado no computador são exemplos de webmail, pois só funcionam dentro do navegador.',
  v=E+'Thunderbird e o Outlook instalado são clientes de e-mail: programas instalados no dispositivo, que usam SMTP para enviar e POP3 ou IMAP para receber, e podem guardar mensagens localmente. Webmail é o acesso pelo navegador (ex.: Gmail na web, Outlook.com).<br><br>Correção: Thunderbird e Outlook instalado são clientes de e-mail, não webmail.',
  alvo='Distinguir cliente de e-mail instalado de webmail.', fx=('gmail_clients','rfc5598'),
  sol='Errado: a Ajuda do Gmail cita Outlook e Thunderbird como clientes aos quais se adiciona a conta; não são páginas web.',
  alt='Considerei o Outlook na web (Outlook.com), que é webmail; por isso a frente especifica "instalado no computador".',
  rec='Exige classificar exemplos conhecidos; a frente não informa a categoria correta.', fb='Verso dá o critério (instalado × navegador) e exemplos de cada lado.'),
 dict(k='R07', tags='Campos_Cabecalho',
  f='Os destinatários incluídos no campo Cco (com cópia oculta) recebem a mensagem, mas seus endereços não são mostrados aos destinatários dos campos Para e Cc.',
  v=C+'Cco (com cópia oculta), em inglês Bcc (blind carbon copy), envia a mensagem a destinatários cujos endereços não são revelados aos demais. É útil para proteger a privacidade de uma lista e dificultar a coleta de endereços por spammers.',
  alvo='Efeito do campo Cco/Bcc.', fx=('rfc5322',),
  sol='Certo: RFC 5322, 3.6.3 — Bcc contém endereços que não devem ser revelados aos outros destinatários.',
  alt='Testei "Cco oculta o remetente": não oculta; a frase não afirma isso, então segue Certa.',
  rec='Recupera o efeito do campo a partir de seu nome.', fb='Verso explica o sinônimo Bcc, que a banca usa como pegadinha.'),
 dict(k='R08', tags='Campos_Cabecalho',
  f='Os endereços informados no campo Cc (com cópia) ficam ocultos para os demais destinatários da mensagem.',
  v=E+'No Cc, os endereços ficam visíveis para todos os destinatários, como no campo Para. Quem fica oculto é o destinatário colocado no Cco (Bcc).<br><br>Correção: Cc é cópia visível; Cco é cópia oculta.',
  alvo='Cc é cópia visível (contraste com Cco).', fx=('rfc5322',),
  sol='Errado: RFC 5322 descreve o Cc como lista de outros destinatários, sem ocultação; ocultação é do Bcc.',
  alt='Considerei clientes que exibem resumo de destinatários: não altera a regra do campo Cc.',
  rec='Contraste direto entre Cc e Cco, confusão comum de nomenclatura.', fb='Verso corrige com a regra dos dois campos.'),
 dict(k='R09', tags='Respostas',
  f='No Outlook, a opção Responder a todos envia a resposta ao remetente original e aos destinatários que estavam nos campos Para e Cc da mensagem.',
  v=C+'Responder envia só para o remetente. Responder a todos inclui o remetente e os endereços que estavam em Para e Cc. Quem estava em Cco não entra, porque seu endereço não aparece para quem responde. Nas respostas, o anexo original não vai junto.',
  alvo='Alcance do comando Responder a todos.', fx=('ms_reply',),
  sol='Certo: a Microsoft define Responder a todos como resposta ao remetente e a todos nas linhas Para e Cc.',
  alt='Considerei o Cco: não é incluído; a frase lista só Para e Cc, coerente com a fonte.',
  rec='Recupera o alcance exato do comando.', fb='Verso diferencia os três comandos e cita o caso do Cco.'),
 dict(k='R10', tags='Respostas',
  f='No Outlook, ao encaminhar uma mensagem, os anexos que ela continha deixam de ser enviados.',
  v=E+'Encaminhar envia a mensagem recebida a outra pessoa e mantém os anexos originais. Já em Responder e Responder a todos, o Outlook não inclui os anexos, pois eles voltariam a quem os enviou.<br><br>Correção: ao encaminhar, os anexos originais vão junto.',
  alvo='Encaminhar mantém anexos; responder não.', fx=('ms_reply',),
  sol='Errado: a Microsoft informa que anexos da mensagem original são incluídos automaticamente ao encaminhar.',
  alt='Considerei que o usuário pode remover o anexo manualmente antes de encaminhar: isso é escolha do usuário, não comportamento do comando.',
  rec='Recupera a regra dos anexos por comando.', fb='Verso explica o motivo de responder não incluir anexos.'),
 dict(k='R11', tags='Endereco',
  f='Em um endereço como ana@empresa.com.br, o caractere @ separa o nome do usuário (ana) do domínio (empresa.com.br).',
  v=C+'O endereço tem a forma usuário@domínio. Antes do @ fica a parte local, que identifica a caixa postal; depois, o domínio, que indica quem recebe as mensagens (aqui, empresa.com.br; o .br indica o Brasil). O @ pode ser lido como "em": ana em empresa.com.br.',
  alvo='Estrutura do endereço de e-mail: parte local @ domínio.', fx=('rfc5322',),
  sol='Certo: na RFC 5322 o endereço (addr-spec) é parte local + "@" + domínio.',
  alt='Considerei endereço com dois @: inválido; não afeta o exemplo.',
  rec='Exige reconhecer as duas partes do endereço e a função do @.', fb='Verso nomeia as partes e explica a leitura "em", cobrada em item da PF 2018 citado no material.'),
 dict(k='R12', tags='Seguranca_Email',
  f='O SMTP, por si só, criptografa o conteúdo das mensagens enviadas.',
  v=E+'O SMTP, sozinho, transmite as mensagens sem criptografia. A proteção vem de camadas adicionais: TLS na conexão (STARTTLS ou TLS implícito, como nas variantes "seguras" SMTPS, IMAPS e POP3S) ou criptografia do conteúdo (S/MIME, PGP).<br><br>Correção: o SMTP não criptografa por padrão; depende de TLS ou de S/MIME/PGP.',
  alvo='SMTP não cifra por padrão; segurança vem de TLS ou S/MIME/PGP.', fx=('rfc8314','rfc5321'),
  sol='Errado: a RFC 8314 trata o TLS como camada adicionada (STARTTLS ou TLS implícito) aos protocolos de e-mail.',
  alt='Considerei provedores que forçam TLS: é configuração adicional, não propriedade do SMTP "por si só".',
  rec='Recupera a ausência de criptografia nativa.', fb='Verso aponta as camadas que fornecem a proteção.'),
 dict(k='R13', tags='Webmail_Cliente',
  f='No Outlook, bloquear um remetente impede que essa pessoa consiga enviar mensagens para o seu endereço.',
  v=E+'Bloquear um remetente no Outlook faz as novas mensagens dele irem direto para a pasta Lixo Eletrônico. A pessoa continua podendo enviar mensagens ao seu endereço; o bloqueio só muda onde elas aparecem para você.<br><br>Correção: o bloqueio desvia as mensagens para o Lixo Eletrônico, sem impedir o envio.',
  alvo='Efeito do bloqueio de remetente no Outlook.', fx=('ms_block',),
  sol='Errado: a Microsoft informa que mensagens de remetentes bloqueados vão direto para Lixo Eletrônico.',
  alt='Considerei bloqueio feito pelo administrador do servidor (regras de transporte): é outro mecanismo; a frente trata da opção do usuário.',
  rec='Recupera o efeito real do bloqueio, apontado no material como já cobrado.', fb='Verso corrige com a pasta de destino.'),
 dict(k='R14', tags='Arquitetura_Email',
  f='O correio eletrônico é uma forma de comunicação assíncrona: o destinatário não precisa estar conectado no momento do envio para receber a mensagem depois.',
  v=C+'Comunicação assíncrona é a que não exige os dois lados conectados ao mesmo tempo. A mensagem fica guardada na caixa postal do destinatário, no servidor, até ele acessá-la. Uma chamada de vídeo, ao contrário, é síncrona.',
  alvo='Caráter assíncrono (armazenar e repassar) do e-mail.', fx=('rfc5598',),
  sol='Certo: a RFC 5598 descreve o e-mail como serviço de armazenar e repassar (store-and-forward), com entrega na caixa postal.',
  alt='Considerei entrega quase instantânea em serviços modernos: rapidez não muda o caráter assíncrono.',
  rec='Recupera o significado de assíncrono aplicado ao e-mail.', fb='Verso define o termo e dá contraexemplo síncrono.'),
]

# ---------------------------------------------------------------- Cloze
CZ = [
 dict(k='C01', tags='Arquitetura_Email',
  t='Caminho de uma mensagem de e-mail na arquitetura da internet:<br>1. o programa em que o usuário escreve e lê as mensagens é o {{c1::MUA (Mail User Agent)}};<br>2. o agente que recebe a mensagem do autor, confere a autenticação e a aceita para envio é o {{c1::MSA (Mail Submission Agent)}};<br>3. o agente que repassa a mensagem de servidor em servidor até o domínio de destino é o {{c1::MTA (Mail Transfer Agent)}};<br>4. o agente que coloca a mensagem na caixa postal do destinatário é o {{c1::MDA (Mail Delivery Agent)}}.',
  x='MUA (User = usuário): Outlook, Thunderbird, app do Gmail ou a página do webmail.<br>MSA (Submission = submissão): porta de entrada no provedor; exige login do remetente (porta 587).<br>MTA (Transfer = transferência): servidores que trocam a mensagem entre si por SMTP (porta 25).<br>MDA (Delivery = entrega): deposita na caixa postal; depois o MUA do destinatário a lê por POP3 ou IMAP.<br>Aceitar só a sigla (MUA, MSA, MTA, MDA) como resposta.',
  alvo='Papéis MUA, MSA, MTA e MDA na ordem do percurso.', fx=('rfc5598','rfc6409'),
  sol='Lacunas: MUA, MSA, MTA, MDA (sigla basta). RFC 5598 define os papéis e a ordem; RFC 6409 atribui ao MSA a autenticação.',
  alt='Testei trocar MTA por MDA na etapa 3: a descrição "de servidor em servidor" só cabe no MTA; "coloca na caixa postal" só cabe no MDA.',
  rec='As descrições funcionais determinam cada sigla sem revelá-la; as quatro formam um único percurso coerente.', fb='Extra decodifica cada letra (User/Submission/Transfer/Delivery) e liga às portas e protocolos.',
  cob={'1': ['D02'], '2': ['D01'], '3': ['D02'], '4': ['D01']}),
 dict(k='C02', tags='Portas',
  t='Na transferência de mensagens entre servidores de e-mail, o SMTP usa, por padrão, a porta TCP {{c1::25}}.',
  x='A porta 25 é a porta registrada do SMTP para o repasse entre servidores (MTA → MTA). A submissão pelo usuário autenticado usa a 587 (com STARTTLS) ou a 465 (TLS implícito). Não confundir com 53 (DNS) nem 110 (POP3).',
  alvo='Porta padrão do SMTP no repasse entre servidores.', fx=('rfc5321','rfc6409'),
  sol='Lacuna: 25. RFC 5321, 4.5.4.2 (porta 25 registrada na IANA); RFC 6409 confirma que o repasse continua na 25 e a submissão usa 587.',
  alt='Testei 587 e 465: são de submissão pelo usuário, não de repasse entre servidores; a frente especifica "entre servidores".',
  rec='Contexto "entre servidores" determina 25 e afasta 587/465.', fb='Extra separa repasse de submissão e lista portas confundíveis.',
  cob={'1': ['D03', 'D12']}),
 dict(k='C03', tags='Portas',
  t='Portas TCP padrão, sem TLS, dos protocolos de recebimento: POP3 → {{c1::110}}; IMAP → {{c1::143}}.',
  x='POP3 escuta na porta 110 e IMAP na 143. Nas versões com TLS implícito: POP3S 995 e IMAPS 993. Dica: a porta do IMAP (143) é maior que a do POP3 (110), e as seguras começam com 99.',
  alvo='Portas padrão de POP3 e IMAP.', fx=('rfc1939','rfc9051','rfc8314'),
  sol='Lacunas: 110 (RFC 1939) e 143 (RFC 9051, 2.1).',
  alt='Testei 995/993: são as portas com TLS implícito; a frente pede "sem TLS".',
  rec='Recupera o par de portas que o material apresenta na tabela POP3 × IMAP.', fb='Extra acrescenta as portas seguras para evitar confusão.',
  cob={'1': ['D04'], '2': ['D04']}),
]

# ---------------------------------------------------------------- desafiadores (D)
def rub(c, de, op, cmp, au, fb, ling, ut):
    k = ('correcao','determinacao','operacao_d','comparacao','autoria','feedback','linguagem_didatica','utilidade')
    vals = (c, de, op, cmp, au, fb, ling, ut)
    return {key: {'resultado': ('PENDENTE' if (key == 'comparacao' and val.startswith('PENDENTE')) else 'PASSA'), 'evidencia': val.replace('PENDENTE: ', '')} for key, val in zip(k, vals)}

D = [
 dict(k='D01', g='C', tags='Arquitetura_Email',
  f='Paula, do provedor A, envia um e-mail a Rui, do provedor B. Um servidor de A confere o login de Paula e aceita a mensagem; ela é repassada até B, onde outro componente a coloca na caixa postal de Rui. O componente que conferiu o login é o MSA, e o que colocou a mensagem na caixa postal é o MDA.',
  v=C+'O MSA (Mail Submission Agent) recebe a mensagem do autor, exige autenticação e a aceita para envio. O MDA (Mail Delivery Agent) faz a entrega final na caixa postal. Entre os dois atuam os MTAs (Mail Transfer Agents), que repassam a mensagem de servidor em servidor; o aplicativo de Paula é o MUA (Mail User Agent).<br><br>Dado decisivo: "conferiu o login e aceitou" = submissão (MSA); "colocou na caixa postal" = entrega (MDA).',
  alvo='Identificar MSA e MDA pelas ações descritas.', op='Mapear ações concretas (autenticar/aceitar; depositar) aos papéis da arquitetura.',
  regra='MSA aceita e autentica a submissão; MDA entrega na caixa postal (RFC 5598; RFC 6409).', dado='As ações "confere o login e aceita" e "coloca na caixa postal".',
  solucao='Autenticar e aceitar = MSA; depositar na caixa = MDA; logo Certo.', erro='Chamar de MTA quem aceita a mensagem ou quem entrega, por ser "servidor".',
  conc='Testei a leitura de que o servidor de A seria MTA: ele também repassa, mas a ação descrita (conferir login e aceitar) é a de submissão; conclusão mantida.',
  orig='Situação autoral com dois provedores e ações concretas; não há item Cebraspe localizado com essa estrutura.', fx=('rfc5598','rfc6409'), refs=[], fid='inspiracao_geral',
  lim='Nenhum item CESPE/Cebraspe C/E sobre MSA/MDA foi localizado nas buscas em cadernos oficiais (MPTO 2024, EMBRAPA 2024, ANP 2022, CAU/BR 2023, PCDF 2024, PF 2018, PRF 2021); construção baseada no conteúdo das RFCs.',
  rb=rub('Conferido com RFC 5598 (papéis) e RFC 6409 (autenticação no MSA).','Ações descritas sem ambiguidade; cada uma corresponde a um papel único.','Exige associar ações a papéis, não lembrar definição isolada.','PENDENTE: sem item Cebraspe específico localizado; inspiração geral declarada.','Cenário e redação autorais.','Verso explica os quatro papéis e o dado decisivo.','Frases curtas, quem faz o quê explícito; siglas expandidas no verso.','Cobre lacunas MSA e MDA do Cloze C01.')),
 dict(k='D02', g='E', tags='Arquitetura_Email',
  f='Rui lê, no aplicativo de e-mail do celular configurado com IMAP, a mensagem que chegou à sua caixa postal no servidor. Nessa situação, o aplicativo de Rui atua como MTA, pois é ele que retira a mensagem do servidor para exibi-la.',
  v=E+'O programa que o usuário usa para ler e escrever mensagens é o MUA (Mail User Agent). O MTA (Mail Transfer Agent) é o servidor que repassa mensagens a outros servidores, por SMTP. Acessar a caixa postal por IMAP ou POP3 é tarefa do MUA.<br><br>Correção: o aplicativo de Rui atua como MUA; MTA é o repasse entre servidores.',
  alvo='Distinguir MUA de MTA.', op='Classificar o papel do aplicativo do destinatário a partir da ação (ler a caixa por IMAP).',
  regra='MUA é o agente do usuário; MTA repassa entre servidores (RFC 5598).', dado='Aplicativo do celular lendo a caixa postal por IMAP.',
  solucao='Ler a caixa = MUA; repasse entre servidores = MTA; a frase atribui MTA ao aplicativo, logo Errado.', erro='Achar que "retirar do servidor" é transferência (MTA).',
  conc='Testei se algum aplicativo pode ser MTA: um cliente não faz repasse entre servidores; a justificativa "retira do servidor" não caracteriza MTA.',
  orig='Situação autoral que completa a de D01 do lado do destinatário.', fx=('rfc5598',), refs=[], fid='inspiracao_geral',
  lim='Nenhum item CESPE/Cebraspe C/E sobre MUA/MTA foi localizado nas buscas em cadernos oficiais; construção baseada na RFC 5598.',
  rb=rub('Conferido com RFC 5598: MUA atua para o usuário; MTA repassa um "salto".','Um só papel possível para o aplicativo; justificativa testada.','Exige distinguir papéis pela ação; a frase traz justificativa plausível a julgar.','PENDENTE: sem item Cebraspe específico localizado; inspiração geral declarada.','Redação e situação autorais.','Verso localiza o erro na justificativa e dá a correção.','Linguagem direta; siglas explicadas no verso.','Cobre lacunas MUA e MTA do Cloze C01.')),
 dict(k='D03', g='E', tags='Portas',
  f='O firewall de um órgão bloqueia todo o tráfego de saída, exceto nas portas TCP 80 e 443. O servidor de e-mail do órgão precisa repassar mensagens diretamente aos servidores de e-mail de outros domínios. Nessa configuração, o repasse funcionará, pois a transferência de e-mail entre servidores usa HTTPS.',
  v=E+'A transferência de mensagens entre servidores de e-mail é feita pelo SMTP, que usa por padrão a porta TCP 25 — não pelo HTTPS (porta 443). Com a porta 25 de saída bloqueada, o servidor do órgão não consegue entregar mensagens aos outros domínios.<br><br>Correção: para o repasse funcionar, a porta TCP 25 (SMTP) precisaria estar liberada.',
  alvo='Associar o repasse entre servidores ao SMTP/porta 25.', op='Avaliar se uma regra de firewall permite um serviço, identificando protocolo e porta.',
  regra='Repasse entre servidores usa SMTP na porta 25 (RFC 5321; RFC 6409).', dado='Só 80 e 443 liberadas; repasse direto a outros domínios.',
  solucao='Repasse exige 25; 25 bloqueada; justificativa (HTTPS) falsa; logo Errado.', erro='Achar que todo serviço da internet passa por HTTPS.',
  conc='Considerei relay por um provedor externo via HTTPS (API): a frente diz "diretamente aos servidores de outros domínios", o que exige SMTP.',
  orig='Inspirado na operação do item 65 (EMBRAPA): firewall × porta do serviço de e-mail; situação, portas liberadas e conclusão reconstruídas.', fx=('rfc5321','rfc6409'), refs=['EMBRAPA24_65'], fid='comparada',
  cmp='Mesma operação (identificar porta exigida pelo envio de e-mail sob regra de firewall), com gabarito invertido e justificativa a julgar.',
  rb=rub('Conferido com RFC 5321 (porta 25) e RFC 6409 (repasse na 25).','"Diretamente" afasta intermediários; só uma conclusão.','Aplica conhecimento de porta a uma regra de firewall.','Compara com EMBRAPA 2024, item 65 (gabarito definitivo C).','Cenário inverso e com justificativa, não paráfrase do item.','Verso aponta a porta correta e a consequência.','Termos "firewall" e "porta" usados em contexto simples; verso explica.','Cobre a lacuna do Cloze C02.')),
 dict(k='D04', g='C', tags='Portas',
  f='Em uma rede, o firewall bloqueia a porta TCP 110 e libera a porta TCP 143. O servidor de e-mail oferece POP3 e IMAP sem TLS, nas portas padrão. Nessa situação, um cliente de e-mail configurado com IMAP conseguirá acessar a caixa postal, mas um configurado com POP3 não conseguirá.',
  v=C+'As portas padrão sem TLS são 110 para o POP3 e 143 para o IMAP. Com a 110 bloqueada, o cliente POP3 não alcança o servidor; com a 143 liberada, o cliente IMAP funciona normalmente.<br><br>Dado decisivo: saber qual protocolo usa cada porta.',
  alvo='Portas 110 (POP3) e 143 (IMAP) aplicadas.', op='Deduzir o efeito de bloqueio/liberação de portas sobre cada protocolo.',
  regra='POP3 = 110; IMAP = 143 (RFC 1939; RFC 9051).', dado='110 bloqueada, 143 liberada, servidores nas portas padrão sem TLS.',
  solucao='IMAP via 143 funciona; POP3 via 110 falha; logo Certo.', erro='Inverter as portas dos dois protocolos.',
  conc='Considerei portas TLS (993/995): a frente fixa "sem TLS, nas portas padrão", eliminando essa leitura.',
  orig='Mesma família operacional do item EMBRAPA 65 (porta × serviço sob firewall), aplicada a protocolos de recebimento; redação autoral.', fx=('rfc1939','rfc9051'), refs=['EMBRAPA24_65'], fid='comparada',
  cmp='Transfere a operação porta → serviço do item 65 para POP3/IMAP; gabarito próprio conferido nas RFCs.',
  rb=rub('Conferido: RFC 1939 (110) e RFC 9051 (143).','Hipóteses explícitas (sem TLS, portas padrão).','Dedução sobre duas configurações a partir das portas.','Compara com EMBRAPA 2024, item 65.','Situação nova, com dois protocolos.','Verso associa cada porta e conclui.','Curto e direto; termos técnicos mínimos.','Cobre as duas lacunas do Cloze C03.')),
 dict(k='D05', g='C', tags='Protocolos',
  f='Um servidor público configurou o Thunderbird com IMAP como servidor de entrada e SMTP como servidor de saída. Certo dia, o servidor SMTP do provedor ficou fora do ar, mas o servidor IMAP continuou funcionando. Nessa situação, ele continuou conseguindo ler as mensagens da caixa postal, mas não conseguiu enviar novas mensagens.',
  v=C+'Cada protocolo tem sua função: o IMAP dá acesso às mensagens guardadas no servidor (recebimento); o SMTP envia as mensagens. Se só o SMTP falha, a leitura continua possível, mas o envio fica impedido.<br><br>Erro comum: achar que o mesmo protocolo faz as duas coisas ou trocar as funções (SMTP para receber, POP/IMAP para enviar).',
  alvo='Funções separadas de IMAP (receber) e SMTP (enviar).', op='Inferir a consequência da falha de um protocolo sobre envio e leitura.',
  regra='SMTP envia; IMAP acessa a caixa (RFC 5321; RFC 9051).', dado='SMTP fora do ar, IMAP funcionando.',
  solucao='Leitura depende de IMAP (ok); envio depende de SMTP (falha); logo Certo.', erro='Supor que o servidor de entrada também envia, ou trocar os papéis.',
  conc='Considerei envio via webmail do provedor: a frente trata do Thunderbird configurado com SMTP; o webmail não está em jogo.',
  orig='Inspirado na operação do item 99 (MPTO 2024): papéis trocados dos protocolos; aqui o aluno aplica os papéis a uma falha concreta.', fx=('rfc5321','rfc9051'), refs=['MPTO24_99'], fid='comparada',
  cmp='O item 99 cobra a função de cada protocolo; este D exige aplicar essa função para prever consequência de falha.',
  rb=rub('Conferido nas RFCs 5321 e 9051.','Falha isolada e configuração explícita.','Exige inferir efeito, não só lembrar função.','Compara com MPTO 2024, item 99 (gabarito definitivo E).','Situação nova, sem reutilizar texto do item.','Verso explica cada função e o erro comum.','Situação cotidiana, sem jargão desnecessário.','Aplica R01/R02/R03 a um caso.')),
 dict(k='D06', g='E', tags='Protocolos',
  f='Carla configurou sua conta de e-mail no notebook com POP3, no modo padrão, que apaga as mensagens do servidor depois de baixá-las. Mais tarde, configurou a mesma conta no celular com IMAP. Nessa situação, as mensagens que o notebook já havia baixado aparecerão no celular, pois o IMAP mantém a conta sincronizada.',
  v=E+'O IMAP sincroniza o que está no servidor. Como o POP3 do notebook baixou as mensagens e as apagou do servidor, elas ficaram só no notebook; o celular, via IMAP, não tem de onde buscá-las.<br><br>Correção: as mensagens removidas do servidor pelo POP3 não aparecerão no celular; só as que ainda estão no servidor.',
  alvo='Limite da sincronização do IMAP diante da remoção feita pelo POP3.', op='Combinar o comportamento de dois protocolos na mesma conta para prever o resultado.',
  regra='POP3 baixa e, no modo padrão, remove do servidor; IMAP trabalha sobre o que está no servidor (RFC 1939; RFC 9051).', dado='POP3 no modo que apaga do servidor; IMAP configurado depois.',
  solucao='Mensagens saíram do servidor antes; IMAP não as encontra; justificativa não salva a conclusão; logo Errado.', erro='Achar que "sincronizar" recupera dados de outro aparelho.',
  conc='Considerei a opção "deixar cópia no servidor": a frente fixa o modo que apaga, eliminando essa leitura.',
  orig='Situação autoral; o material cita itens de outras bancas (AOCP) sobre POP3/IMAP, não usados como referência Cebraspe.', fx=('rfc1939','rfc9051'), refs=[], fid='inspiracao_geral',
  lim='Os itens sobre POP3 × IMAP localizados com gabarito eram de outras bancas (AOCP/UFOB) ou de bancos sem caderno oficial; nenhum item Cebraspe C/E oficial específico foi confirmado.',
  rb=rub('Conferido nas RFCs 1939 e 9051.','Modo do POP3 explicitado; ordem dos fatos clara.','Combina dois comportamentos para chegar à conclusão.','PENDENTE: sem item Cebraspe oficial específico confirmado; inspiração geral declarada.','Cenário autoral.','Verso explica por que a sincronização não alcança as mensagens.','Linguagem cotidiana; termos POP3/IMAP explicados no verso.','Transfere R03/R04 a um caso de uso real.')),
 dict(k='D07', g='C', tags='Campos_Cabecalho',
  f='Um coordenador envia um aviso a 40 candidatos. Põe o próprio endereço em Para, o da chefia em Cc e os 40 candidatos em Cco. Nessa situação, em regra, cada candidato verá o endereço da chefia, mas não o dos demais candidatos.',
  v=C+'Endereços em Para e Cc são visíveis a todos os destinatários; endereços em Cco (Bcc) não são revelados aos outros. Assim, cada candidato vê o coordenador (Para) e a chefia (Cc), mas não os outros candidatos (Cco).<br><br>Dado decisivo: o campo em que cada endereço foi colocado define quem o enxerga.',
  alvo='Aplicar visibilidade de Para/Cc/Cco.', op='Prever o que cada destinatário vê conforme o campo usado.',
  regra='Para e Cc visíveis; Bcc não revelado aos demais (RFC 5322, 3.6.3).', dado='Chefia em Cc; candidatos em Cco.',
  solucao='Chefia visível (Cc); candidatos ocultos entre si (Cco); logo Certo.', erro='Achar que quem está em Cco não vê ninguém, ou que Cc também oculta.',
  conc='Considerei implementações em que a cópia do Bcc mostra a linha Bcc (RFC 5322, método 2); por isso a frente usa "em regra"; nos clientes usuais (Outlook, Gmail) cada Cco não vê os outros.',
  orig='Situação autoral de uso legítimo do Cco com contraste Cc.', fx=('rfc5322',), refs=[], fid='inspiracao_geral',
  lim='Itens Cebraspe sobre Cco localizados apenas em bancos não oficiais, sem caderno/gabarito oficial confirmado nesta tarefa.',
  rb=rub('Conferido com RFC 5322, 3.6.3.','"Em regra" delimita a variação de implementação registrada na RFC.','Exige combinar dois campos para prever a visibilidade.','PENDENTE: sem item Cebraspe oficial confirmado; inspiração geral declarada.','Cenário autoral, diferente do exemplo da festa do material.','Verso explica campo por campo.','Situação simples, sem jargão.','Aplica R07/R08 a uma decisão prática.')),
 dict(k='D08', g='E', tags='Respostas',
  f='Lia enviou uma mensagem para Bruno (campo Para), com Caio em Cc e Davi em Cco. Bruno usou a opção Responder a todos. A resposta de Bruno chegará a Lia, Caio e Davi.',
  v=E+'Responder a todos envia ao remetente original e aos endereços que estavam em Para e Cc. Como Davi estava em Cco, o endereço dele não aparece na mensagem que Bruno recebeu; a resposta vai para Lia e Caio, não para Davi.<br><br>Correção: a resposta chega a Lia e Caio; quem estava em Cco não é incluído.',
  alvo='Alcance de Responder a todos com destinatário em Cco.', op='Combinar a regra do Cco com a do comando de resposta.',
  regra='Responder a todos = remetente + Para + Cc (Microsoft); Bcc não revelado (RFC 5322).', dado='Davi em Cco; Bruno responde a todos.',
  solucao='Bruno não vê Davi; resposta vai a Lia e Caio; logo Errado.', erro='Achar que "todos" inclui quem estava oculto.',
  conc='Considerei Davi usando Responder a todos (caso diferente e controverso em comentários): a frente trata da resposta de Bruno, que não conhece Davi.',
  orig='Inspirado no item 26 (ANP 2022), que cobra o efeito de um comando de resposta/encaminhamento sobre os destinatários; situação reconstruída com Cco.', fx=('ms_reply','rfc5322'), refs=['ANP22_26'], fid='comparada',
  cmp='Mesma operação (a quem o comando envia), acrescida do dado decisivo Cco.',
  rb=rub('Conferido com Microsoft (Responder a todos) e RFC 5322 (Bcc).','Papéis e campos explícitos; caso de Davi responder excluído.','Combina duas regras.','Compara com ANP 2022, item 26 (gabarito definitivo E).','Situação autoral com quatro pessoas.','Verso explica por que Davi fica de fora.','Nomes curtos e campos entre parênteses facilitam a leitura.','Aplica R07/R09.')),
 dict(k='D09', g='E', tags='Respostas',
  f='No Outlook, Marcos recebeu um e-mail com um relatório anexado e precisa que Joana, que não estava entre os destinatários, receba o arquivo. Se ele usar Responder a todos e acrescentar o endereço de Joana, o anexo original irá junto; se usar Encaminhar, o anexo não irá.',
  v=E+'É o contrário. Encaminhar repassa a mensagem a outra pessoa e mantém os anexos originais. Responder e Responder a todos não incluem os anexos originais (seria devolvê-los a quem já os tem); seria preciso anexar de novo.<br><br>Correção: para Joana receber o relatório sem reanexar, Marcos deve usar Encaminhar.',
  alvo='Escolher o comando que leva o anexo a um novo destinatário.', op='Decidir entre comandos pela consequência sobre o anexo.',
  regra='Encaminhar inclui anexos; responder não (Microsoft Support).', dado='Joana não estava na conversa; arquivo anexado no original.',
  solucao='Responder a todos não leva o anexo; Encaminhar leva; a frase inverte; logo Errado.', erro='Inverter o comportamento dos comandos quanto aos anexos.',
  conc='Considerei a opção de anexar manualmente na resposta: a frente fala de envio "automático", que não ocorre ao responder.',
  orig='Inspirado no item 26 (ANP 2022) sobre o comando Encaminhar no Outlook; aqui o alvo é o anexo, em situação autoral.', fx=('ms_reply',), refs=['ANP22_26'], fid='comparada',
  cmp='Mesma ferramenta e família (efeito de Encaminhar × responder), com dado decisivo diferente (anexo).',
  rb=rub('Conferido com a página da Microsoft sobre responder/encaminhar.','Comandos e objetivo explícitos; uma conclusão.','Exige escolher comando pela consequência.','Compara com ANP 2022, item 26.','Situação nova (anexo e terceira pessoa).','Verso explica o motivo e a ação correta.','Linguagem de escritório, sem termos técnicos.','Aplica R10 a uma decisão.')),
 dict(k='D10', g='E', tags='Seguranca_Email',
  f='Um servidor quer que os destinatários possam comprovar que os e-mails foram mesmo enviados por ele e que não foram alterados no caminho. Para isso, configurou no Outlook uma assinatura com nome, cargo e telefone, inserida automaticamente ao fim de cada mensagem. Essa configuração atende ao objetivo.',
  v=E+'A assinatura comum do Outlook é só um bloco de texto (nome, cargo, contatos) que qualquer pessoa pode copiar; não garante autoria nem integridade. Para isso existe a assinatura digital, feita com um certificado digital (ID digital), que permite ao destinatário verificar quem assinou e se o conteúdo foi alterado.<br><br>Correção: o objetivo exige assinatura digital com certificado, não a assinatura de texto.',
  alvo='Distinguir assinatura de texto de assinatura digital.', op='Avaliar se um recurso atende a um requisito de segurança (autenticidade e integridade).',
  regra='Assinatura digital usa ID digital e garante autenticidade e integridade; assinatura comum não (Microsoft).', dado='Assinatura configurada com nome, cargo e telefone.',
  solucao='Bloco de texto não comprova autoria nem integridade; logo Errado.', erro='Confundir o nome "assinatura" do Outlook com assinatura digital.',
  conc='Considerei se a assinatura de texto poderia conter um certificado: a frente descreve apenas nome, cargo e telefone.',
  orig='Inspirado no item 20 (CAU/BR 2023), que confunde Inserir Assinatura com assinatura digital; situação reconstruída a partir do requisito.', fx=('ms_digsig',), refs=['CAU23_20'], fid='comparada',
  cmp='Mesma distinção, partindo de um objetivo de segurança em vez do nome do menu.',
  rb=rub('Conferido com a página da Microsoft sobre assinatura digital.','Objetivo e configuração explícitos.','Exige confrontar requisito e recurso.','Compara com CAU/BR 2023, item 20 (gabarito definitivo E).','Redação autoral orientada ao requisito.','Verso explica a diferença e a solução correta.','Termos autenticidade/integridade traduzidos em "quem enviou" e "não alterado".','Liga a parte "Assinatura" do corpo do e-mail (PDF) à segurança.')),
 dict(k='D11', g='C', tags='Seguranca_Email',
  f='Um provedor oferece envio de e-mail por SMTP na porta 587 com STARTTLS ou na porta 465 com TLS implícito. Um usuário configura seu cliente de e-mail com uma dessas opções. Nesse caso, a conexão entre o cliente e o servidor de envio trafega criptografada, ainda que o SMTP, por si só, não preveja criptografia.',
  v=C+'O SMTP não cifra nada sozinho. A proteção vem do TLS: no STARTTLS (porta 587), a conexão começa sem cifra e é convertida para TLS; no TLS implícito (porta 465), ela já começa cifrada. Em ambos, o trecho cliente → servidor de envio fica protegido.<br><br>Limite: isso protege a conexão, não o conteúdo de ponta a ponta; para cifrar a mensagem em si, usa-se S/MIME ou PGP.',
  alvo='Origem da criptografia no envio (TLS) e seu alcance.', op='Julgar o efeito de uma configuração de segurança sobre o trecho de rede.',
  regra='STARTTLS na 587 e TLS implícito na 465 protegem a submissão (RFC 8314).', dado='Cliente configurado com 587+STARTTLS ou 465+TLS.',
  solucao='Ambas as opções cifram a conexão de submissão; SMTP puro não cifra; logo Certo.', erro='Achar que a criptografia é do SMTP ou que vale de ponta a ponta.',
  conc='Considerei falha na negociação STARTTLS: a frente assume a configuração escolhida funcionando; a afirmação limita-se ao trecho cliente → servidor.',
  orig='Situação autoral; o material traz item inédito do próprio curso sobre SMTP e criptografia, não usado como referência Cebraspe.', fx=('rfc8314',), refs=[], fid='inspiracao_geral',
  lim='Nenhum item CESPE/Cebraspe C/E oficial sobre STARTTLS/TLS implícito no e-mail foi localizado nas buscas desta tarefa.',
  rb=rub('Conferido com RFC 8314, seções 3.1–3.3.','Trecho delimitado (cliente → servidor de envio).','Aplica a regra a uma configuração concreta e separa conexão de conteúdo.','PENDENTE: sem item Cebraspe oficial localizado; inspiração geral declarada.','Redação autoral.','Verso explica os dois modos e o limite.','Siglas explicadas no verso em palavras simples.','Aplica R12 e prepara itens de segurança.')),
 dict(k='D12', g='C', tags='Webmail_Cliente',
  f='Em um computador, o firewall só libera a saída nas portas TCP 80 e 443. O usuário acessa seu e-mail pelo webmail do provedor, no navegador. Nessa situação, ele consegue enviar mensagens a outros domínios, pois o navegador fala com o provedor por HTTPS, e o repasse por SMTP é feito pelos servidores do provedor.',
  v=C+'No webmail, o navegador se comunica com o servidor do provedor por HTTP/HTTPS (portas 80/443). Quem envia a mensagem aos outros domínios, por SMTP (porta 25), são os servidores do provedor, fora do computador do usuário. Por isso o bloqueio das demais portas no computador não impede o envio.<br><br>Contraste: um cliente instalado (Outlook, Thunderbird) precisaria das portas de SMTP, IMAP ou POP3, que estão bloqueadas.',
  alvo='Divisão de tarefas no webmail (HTTPS no navegador; SMTP nos servidores).', op='Inferir se o envio funciona dada a regra de firewall e a forma de acesso.',
  regra='Webmail usa HTTP/HTTPS entre navegador e provedor; o repasse SMTP ocorre entre servidores (RFC 5598; RFC 5321).', dado='Só 80/443 liberadas no computador; acesso por webmail.',
  solucao='Navegador usa 443 (liberada); SMTP sai dos servidores do provedor; logo Certo.', erro='Achar que o computador do usuário precisa da porta 25 também no webmail.',
  conc='Considerei bloqueio no lado do provedor: a frente restringe o firewall ao computador do usuário.',
  orig='Contraponto autoral ao D03, inspirado na mesma família do item 65 (EMBRAPA): o serviço de e-mail exige SMTP, mas no webmail quem usa SMTP é o provedor.', fx=('rfc5598','rfc5321'), refs=['EMBRAPA24_65'], fid='comparada',
  cmp='Mesma operação (porta necessária ao envio sob firewall), com a variável decisiva "forma de acesso".',
  rb=rub('Conferido com RFC 5598 (MUA web) e RFC 5321 (repasse SMTP).','Firewall no computador e acesso via navegador explícitos.','Exige localizar onde cada protocolo opera.','Compara com EMBRAPA 2024, item 65.','Situação autoral, contraste com D03.','Verso explica a divisão de tarefas e o contraste com cliente instalado.','Linguagem direta, portas explicadas.','Cobre a lacuna do Cloze C02 e aplica R05.')),
]

# ---------------------------------------------------------------- montagem dos TSVs
def row_r(x): return [x['f'], x['v'], f"{BASE} {x['tags']} {R_TAG}"]
def row_d(x): return [x['f'], x['v'], f"{BASE} {x['tags']} {D_TAG}"]
def row_c(x): return [x['t'], x['x'], f"{BASE} {x['tags']}"]

ce_items = [('R', x) for x in R] + [('D', x) for x in D]
random.Random(808).shuffle(ce_items)
ce_rows, line_of = [], {}
for n, (kind, x) in enumerate(ce_items, 1):
    ce_rows.append(row_r(x) if kind == 'R' else row_d(x)); line_of[x['k']] = n
cz_rows = [row_c(x) for x in CZ]

for row in ce_rows + cz_rows:
    assert all('\t' not in f and '\n' not in f for f in row), row

OUT.mkdir(parents=True, exist_ok=True); (OUT / 'relatorios').mkdir(exist_ok=True)
def write_tsv(name, rows):
    data = ('\n'.join('\t'.join(r) for r in rows) + '\n').encode('utf-8')
    (OUT / name).write_bytes(data); return data
items = {'anki_certo_errado.tsv': write_tsv('anki_certo_errado.tsv', ce_rows),
         'anki_cloze.tsv': write_tsv('anki_cloze.tsv', cz_rows)}

# ---------------------------------------------------------------- calibração D
cal = {'schema_version': 1, 'referencias': REFS, 'cartoes': []}
for x in D:
    n = line_of[x['k']]; row = ce_rows[n - 1]
    rec = dict(id=x['k'], linha=n, sha256=fingerprint(row), gabarito=x['g'], alvo=x['alvo'], operacao_autoral=x['op'],
               regra=x['regra'], dado_decisivo=x['dado'], solucao=x['solucao'], erro_plausivel=x['erro'],
               leitura_concorrente=x['conc'], originalidade=x['orig'], fontes_conteudo=urls(*x['fx']), referencias=x['refs'],
               fidelidade=x['fid'], segunda_conferencia=True, decisao='APROVAR', rubrica=x['rb'])
    if x['fid'] == 'comparada': rec['comparacao'] = x['cmp']
    else: rec['limitacao'] = x['lim']
    assert row[1].startswith(C if x['g'] == 'C' else E)
    cal['cartoes'].append(rec)
(OUT / 'relatorios' / 'calibracao_cebraspe.json').write_text(json.dumps(cal, ensure_ascii=False, indent=1), encoding='utf-8')

# ---------------------------------------------------------------- revisão de recuperação R/C
def rid(k): return f'anki_certo_errado.tsv:{line_of[k]}'
rev = {'schema_version': 1, 'sha256_lote': batch_hash(items), 'revisor': 'Claude (assistente de IA, modelo Opus 5.5) — mesmo agente que redigiu os cartões',
       'tipo_revisao': 'autorevisao', 'cartoes': [], 'sinais': []}
for x in R:
    row = ce_rows[line_of[x['k']] - 1]
    rev['cartoes'].append(dict(id=rid(x['k']), sha256=fingerprint(row), alvo=x['alvo'], solucao=x['sol'], fontes=fontes(*x['fx']),
        alternativa_concorrente=x['alt'], recuperacao=x['rec'], feedback=x['fb'], segunda_conferencia=True, decisao='APROVAR'))
for i, x in enumerate(CZ, 1):
    rev['cartoes'].append(dict(id=f'anki_cloze.tsv:{i}', sha256=fingerprint(cz_rows[i - 1]), alvo=x['alvo'], solucao=x['sol'], fontes=fontes(*x['fx']),
        alternativa_concorrente=x['alt'], recuperacao=x['rec'], feedback=x['fb'],
        desafiadores_por_lacuna={g: [rid(k) for k in ks] for g, ks in x['cob'].items()}, segunda_conferencia=True, decisao='APROVAR'))
sinais_path = Path(__file__).with_name('sinais_resolvidos.json')
if sinais_path.is_file():
    rev['sinais'] = json.loads(sinais_path.read_text(encoding='utf-8'))
(OUT / 'relatorios' / 'revisao_recuperacao.json').write_text(json.dumps(rev, ensure_ascii=False, indent=1), encoding='utf-8')

# mapa de IDs para os relatórios
mapa = {x['k']: rid(x['k']) for x in R + D}
mapa.update({x['k']: f'anki_cloze.tsv:{i}' for i, x in enumerate(CZ, 1)})
(OUT.parent / '_mapa_ids.json').write_text(json.dumps(mapa, ensure_ascii=False, indent=1), encoding='utf-8') if False else None
print(json.dumps(mapa, ensure_ascii=False))
print('R', len(R), 'C/E', sum(1 for x in R if x['v'].startswith(C)), sum(1 for x in R if x['v'].startswith(E)))
print('D', len(D), 'C/E', sum(1 for x in D if x['g']=='C'), sum(1 for x in D if x['g']=='E'))
print('Cloze notas', len(CZ))
