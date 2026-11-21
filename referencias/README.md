# Banco de referências

Tudo o que já foi lido e verificado para os cartões, um item por arquivo Markdown com
frontmatter padronizado:

- `questoes/<disciplina>/<assunto>/`: questões oficiais de concursos;
- `editais/<concurso>/`: programas dos concursos-alvo por disciplina;
- `conteudos/<disciplina>/<assunto>/`: texto normativo verificado (reuso por até 90 dias, com checagem rápida);
- `noticias/<disciplina>/<assunto>/`: alterações legais, decisões judiciais, mudanças de edital;
- `prioridades/<concurso>/<disciplina>/`: prioridade por assunto e o que mais cai (contado).

Arquivos gerados (não editar à mão):

- `assuntos.md`: árvore disciplina > assunto com contagens por tipo (leia primeiro);
- `indice.tsv`: uma linha por item, com coluna `tipo` (consulte pelo script).

Regras, formato e comandos: [skills/referencias-questoes/SKILL.md](../skills/referencias-questoes/SKILL.md).

```text
python -X utf8 skills/referencias-questoes/scripts/referencias.py assuntos
python -X utf8 skills/referencias-questoes/scripts/referencias.py buscar --tipo prioridade --alvo PRF -d transito
python -X utf8 skills/referencias-questoes/scripts/referencias.py buscar --tipo conteudo -t 67-C --recentes 90
python -X utf8 skills/referencias-questoes/scripts/referencias.py mostrar ID --secao "Legislação de Trânsito"
```

Questões: só o item oficial (enunciado, alternativas, gabarito e fonte), sem comentários de
cursos ou sites de questões. Notícias: resumo com palavras próprias e link. Nunca dados
pessoais de marcas-d'água.
