# Banco de questões de referência

Questões de concursos já usadas como referência ou inspiração para os cartões, uma por
arquivo em `questoes/<disciplina>/<assunto>/<id>.md`, com frontmatter padronizado.

- `assuntos.md`: árvore disciplina > assunto com contagens (gerada; leia primeiro).
- `indice.tsv`: uma linha por questão (gerado; consulte pelo script, não à mão).

Regras, formato e comandos: [skills/referencias-questoes/SKILL.md](../skills/referencias-questoes/SKILL.md).

```text
python -X utf8 skills/referencias-questoes/scripts/referencias.py assuntos
python -X utf8 skills/referencias-questoes/scripts/referencias.py buscar -d informatica -t smtp
python -X utf8 skills/referencias-questoes/scripts/referencias.py mostrar ID
```

Só o item oficial (enunciado, alternativas, gabarito e fonte) entra aqui: nada de
comentários de cursos ou sites de questões, nem dados pessoais de marcas-d'água.
