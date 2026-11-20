"""Estrutura do repositório: caminhos citados nas instruções existem e o banco está válido."""
import re
from pathlib import Path

import pytest

import referencias as ref

REPO = Path(__file__).resolve().parents[3]
DOCS = sorted([REPO / 'SKILL.md', REPO / 'instalacao' / 'anki-concursos' / 'SKILL.md',
               *REPO.glob('skills/*/SKILL.md'), *REPO.glob('skills/*/references/*.md'), REPO / 'referencias' / 'README.md'])
LINK = re.compile(r'\]\(([^)#\s]+)')
CODIGO = re.compile(r'`((?:\.\./|skills/|references/|scripts/|instalacao/|lotes/|referencias/)[^`\s*<>]+\.(?:md|py|json|txt))`')


def caminhos_citados(doc: Path):
    texto = doc.read_text(encoding='utf-8')
    for alvo in LINK.findall(texto) + CODIGO.findall(texto):
        if alvo.startswith(('http://', 'https://', 'mailto:')):
            continue
        yield alvo


def resolver(doc: Path, alvo: str) -> list[Path]:
    # Caminhos começando em skills/, instalacao/, lotes/ ou referencias/ podem ser relativos à raiz.
    candidatos = [(doc.parent / alvo)]
    if alvo.startswith(('skills/', 'instalacao/', 'lotes/', 'referencias/')):
        candidatos.append(REPO / alvo)
    if alvo.startswith(('scripts/', 'references/')):
        # Mencionados a partir de outra skill (ex.: gerar-revisao-anki) no texto da skill atual.
        candidatos += [p / alvo for p in REPO.glob('skills/*')]
    return candidatos


@pytest.mark.parametrize('doc', DOCS, ids=lambda p: p.relative_to(REPO).as_posix())
def test_caminhos_citados_existem(doc):
    faltando = [alvo for alvo in caminhos_citados(doc) if not any(c.exists() for c in resolver(doc, alvo))]
    assert faltando == [], f'{doc.relative_to(REPO)} cita caminhos inexistentes: {faltando}'


def test_copia_instalada_da_skill_de_entrada_esta_igual():
    instalada = Path.home() / '.claude' / 'skills' / 'anki-concursos' / 'SKILL.md'
    if not instalada.exists():
        pytest.skip('skill de entrada não instalada neste computador')
    fonte = REPO / 'instalacao' / 'anki-concursos' / 'SKILL.md'
    normal = lambda p: p.read_text(encoding='utf-8').replace('\r\n', '\n')
    assert normal(instalada) == normal(fonte), 'copie instalacao/anki-concursos/SKILL.md para ~/.claude/skills/anki-concursos/'


def test_banco_de_referencias_do_repositorio_valido():
    _, erros, _ = ref.validar(REPO / 'referencias')
    assert erros == []
