> Política comum: [nucleo-pedagogico.md](nucleo-pedagogico.md). Distribuição, equilíbrio e exceções: [matriz_tipos_quantidades.md](matriz_tipos_quantidades.md). Este documento complementa essas regras.

## Finalidade e prioridade

O usuário tem forte preferência por aprendizagem visual. Para C/E rápida, Cebraspe desafiador e Cloze, oferecer **imagens reais de origem verificável na internet** nas frentes quando elas aumentarem a identificação, discriminação ou compreensão necessária para resolver o cartão. Imagens são opcionais e sua utilidade deve ser avaliada caso a caso. NÃO há proporção obrigatória; evitar poluição, decorativismo e pistas involuntárias. A regra daqui substitui proibições antigas de imagens nos cartões.

## Fontes permitidas e verificadas

- Fotografias autênticas, placas, mapas, máquinas, estruturas, anatomia ou fenômenos; esquemas e diagramas **já publicados por terceiros** em fontes verificáveis, preferencialmente sites oficiais, acadêmicos, educacionais, repositórios institucionais e acervos com licença clara. Diagrama autêntico encontrado na internet é permitido; diagrama feito, refeito ou redesenhado pelo assistente é proibido.
- PESQUISAR fonte de origem na internet para cada imagem candidata; abrir o conteúdo original e conferir que o arquivo é o que o buscador descreveu, origem, data quando afetar exatidão, autoria, texto da licença e permissões para uso no material. Página de resultado do buscador sem confirmação não é fonte suficiente. Evitar marcas d'água, conteúdo não autorizado, fotos manipuladas, stock pago não licenciado, imagens cuja licença não permita distribuir.
- Preferir domínio público, Creative Commons compatível com reutilização e distribuição ou autorização explícita. Respeitar exigência de atribuição e proibição de alterações. Registrar URL exata da página de origem, URL do arquivo (quando disponível), titular, licença e data de consulta no `relatorios/fontes_visuais.tsv`. Não colocar bibliografia na frente do card.
- Nunca inventar links nem indicar que baixou imagem quando apenas viu miniatura. Ferramenta de busca de imagem do chat não salva mídia automaticamente. Exigir arquivo efetivo local acessível e legível antes de referenciar em TSV/APKG.

## Proibição absoluta de criação

**Não gerar por IA, não desenhar, não criar imagens sintéticas, não montar colagens, não compor diagramas, não gerar SVG novo, não recriar imagens de questões, não aplicar filtros que mudem conteúdo ou apagar rótulos para fabricar outra figura.** Conversão de formato e redução proporcional de resolução, sem adicionar informação e respeitando a licença, só se estritamente necessário; registrar alterações técnicas. Não usar imagens de IA encontradas na internet como se fossem fotografias reais.

## Decisão visual: checklist

Para cada cartão perguntar:
1. Esta imagem exige reconhecimento visual real que seria difícil de adquirir lendo? Ex.: via arterial x coletora, forma de sinalização, órgão de máquina, rocha, forma de onda, mapa institucional.
2. Um diagrama AUTÊNTICO de fonte verificável esclarece relação/fluxo/estrutura mais rapidamente que texto sem criar ambiguidade?
3. É essencial para uma distinção cobrada no exame? Caso contrário, texto simples costuma ser melhor.
4. A imagem contém a resposta, o nome do objeto, legenda que entrega gabarito, marcação sugestiva ou uma pista que facilita artificialmente um C/E desafiador ou Cloze? Se sim, rejeitar figura ou usar card de identificação apenas se isso for a operação cognitiva correta e o gabarito não estiver exposto.
5. A cena permite resposta única sem depender de detalhes invisíveis, suposições ou normas não identificadas? Ex.: imagens de via urbana sem confirmação dos critérios de classificação não devem ser rotuladas como um tipo viário só pela aparência.
6. Aumenta manutenção, tempo de revisão, peso do pacote ou duplicação sem benefício? Se sim, não inserir.
7. Foi obtida, validada e verificada com direitos de uso? Se não, manter card textual.

**Priorizar**: geometria e figuras em Física/Matemática, identificação de tipos de via e sinalização de trânsito, itens anatômicos, processos com diagrama verificado, peças e equipamentos, mapas/autorizadas. **Baixa prioridade**: prazos, conceitos jurídicos abstratos, negações normativas, exceções textuais sem representação visual fiel.

## Estrutura de cartão e importação

- Na frente do C/E ou no campo Texto de Cloze, colocar imagem como `<img src="anki_vis_HASH.ext">` e a pergunta/assertiva curta autossuficiente, em ordem que ajude a resolver; nunca `<img src="https://...">` para pacotes offline. Usar nomes seguros ASCII exclusivos e estáveis, extensões .jpg/.jpeg/.png/.webp só quando suportadas; preferir PNG/JPEG.
- Uma imagem pode aparecer em várias notas se cada nota exigir operação cognitiva realmente distinta; não gerar notas extras só para mostrar a mesma figura.
- Guardar arquivos originais aprovados em `midia/` no ZIP e `fontes_visuais.tsv` em relatórios, com colunas `arquivo`, `cartao_id`, `pagina_origem`, `arquivo_url`, `autor`, `licenca`, `data_consulta`, `motivo_educacional`, `status`.
- ZIP+TSV: o Anki NÃO lê automaticamente imagens soltas dentro do ZIP ao importar TSV. Orientar a extrair e copiar somente os arquivos de `midia/` para a pasta `collection.media` do perfil Anki (sem subpastas), depois importar TSV habilitando HTML; não afirmar que a importação do TSV embute mídia. Para `.apkg` gerado com mídia incorporada, importar o pacote diretamente; teste de conteúdo deve confirmar inclusão.
- Se o ambiente não permite baixar/validar, **não escrever tag `<img>` para arquivo ausente**. Informar impedimento e fornecer versão textual; no relatório indicar imagens candidatas não incorporadas apenas com URLs comprovadas, sem simular media.

## Auditoria e critérios de aceite

- Verificar todas as referências `img src` no TSV, arquivos em `midia/`, hash/abertura e tipo real, tamanho não abusivo, unicidade de nome, coerência da licença e proveniência do arquivo, e se pacote APKG inclui as mídias. Falhar exportação se imagem referenciada estiver ausente.
- Não inserir URLs remotas como mídia do cartão; não confundir preview de buscador com arquivo entregue.
- Simular frente sem verso e sem solução com imagem visível; identificar vazamento de gabarito por legenda/posição/contexto e ambiguidade de classificação. Validar cada `cN` separadamente.
- Registrar decisão por cartão `SEM_IMAGEM`, `COM_IMAGEM` ou `IMAGEM_REJEITADA`; quantidade, fontes, direitos e testes realmente feitos. Sem garantia de melhoria de memória: protocolo é heurística pedagógica, não teste individual de retenção.
