"""Metadados FICTÍCIOS somente para testes de integração dos exportadores.

Não usar para aprovar conteúdo real ou fabricar auditoria de produção.
"""
import hashlib
import json
from pathlib import Path

CRITERIA = ('correcao', 'determinacao', 'operacao_d', 'comparacao', 'autoria',
            'feedback', 'linguagem_didatica', 'utilidade')


def write_calibration(ce, reports):
    cards = []
    for line, text in enumerate(Path(ce).read_text(encoding='utf-8').splitlines(), 1):
        row = text.split('\t')
        if len(row) != 3 or 'Desafiadora' not in row[2].split():
            continue
        cards.append(dict(
            id=f'TEST-D-{line}', linha=line,
            sha256=hashlib.sha256('\t'.join(row).encode()).hexdigest(),
            gabarito='C' if row[1].startswith('✅ Certo') else 'E',
            alvo='Fixture de integração, não conteúdo aprovado',
            operacao_autoral='Operação sintética para teste documental',
            regra='Premissas do teste, sem certificação de conteúdo',
            dado_decisivo=f'Linha sintética {line}',
            solucao='Solução declarada apenas para testar o esquema',
            erro_plausivel='Erro sintético; não é diagnóstico do usuário',
            leitura_concorrente='Não avaliada pedagogicamente nesta fixture',
            originalidade='Texto sintético de teste',
            fontes_conteudo=['https://example.test/conteudo'], referencias=[],
            fidelidade='inspiracao_geral', limitacao='Fixture sem prova real consultada',
            segunda_conferencia=True, decisao='APROVAR',
            rubrica={k:dict(resultado='PASSA', evidencia=f'Fixture documental de {k}, linha {line}') for k in CRITERIA}))
    target = Path(reports)/'calibracao_cebraspe.json'
    if cards:
        target.write_text(json.dumps(dict(schema_version=1,referencias=[],cartoes=cards)),encoding='utf-8')
    elif target.exists():
        target.unlink()
