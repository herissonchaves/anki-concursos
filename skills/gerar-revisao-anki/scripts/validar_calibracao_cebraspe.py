#!/usr/bin/env python3
"""Checa registros de calibração de D novos; NÃO julga semântica nem fontes.

Uso: python validar_calibracao_cebraspe.py DIRETORIO_OU_ZIP
Não altera arquivos, coleção, gabaritos ou tags.
"""
from __future__ import annotations
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse
import zipfile

REPORT = 'relatorios/calibracao_cebraspe.json'
CE = 'anki_certo_errado.tsv'
HARD = 'Tipo_Desafiadora_Cebraspe'
CRITERIA = ('correcao', 'determinacao', 'operacao_d', 'comparacao', 'autoria', 'feedback', 'linguagem_didatica', 'utilidade')
ANALYSIS = ('alvo', 'operacao_autoral', 'regra', 'dado_decisivo', 'solucao',
            'erro_plausivel', 'leitura_concorrente', 'originalidade')
LIMIT = 20_000_000


def filled(value):
    return isinstance(value, str) and bool(value.strip())


def url(value):
    if not filled(value):
        return False
    try:
        parsed = urlparse(value)
        return parsed.scheme in ('https', 'http') and bool(parsed.netloc) and not parsed.username and not parsed.password
    except ValueError:
        return False


def fingerprint(row):
    """SHA256 dos três campos exatos unidos por TAB, sem terminador de linha."""
    return hashlib.sha256('\t'.join(row).encode('utf-8')).hexdigest()


def validate(ce: bytes, report: bytes | None) -> list[str]:
    errors = []
    try:
        lines = ce.decode('utf-8').splitlines()
    except UnicodeError:
        return ['TSV não é UTF-8']
    cards = {}
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        row = line.split('\t')
        if len(row) != 3:
            errors.append(f'linha {number}: esperados três campos')
        elif HARD in row[2].split():
            cards[number] = row
    if not cards:
        return errors  # Não impõe metadados D a rápidos/Cloze ou coleção antiga.
    if report is None:
        return errors + [f'{REPORT} ausente: {len(cards)} D sem registro; não fabricar revisão']
    try:
        data = json.loads(report.decode('utf-8'))
    except (ValueError, UnicodeError):
        return errors + ['Registro JSON inválido']
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        return errors + ['schema_version deve ser 1']
    refs, records = data.get('referencias'), data.get('cartoes')
    if not isinstance(refs, list) or not isinstance(records, list):
        return errors + ['referencias e cartoes devem ser listas']
    ref_map = {}
    for ref in refs:
        if not isinstance(ref, dict) or not filled(ref.get('id')):
            errors.append('Referência sem id válido')
            continue
        ident = ref['id']
        if ident in ref_map:
            errors.append(f'Referência duplicada: {ident}')
        ref_map[ident] = ref
        for key in ('concurso', 'cargo', 'caderno', 'item', 'operacao_observada'):
            if not filled(ref.get(key)):
                errors.append(f'{ident}: {key} ausente')
        if type(ref.get('ano')) is not int or not 1900 <= ref['ano'] <= 2100:
            errors.append(f'{ident}: ano inválido')
        if not url(ref.get('url')):
            errors.append(f'{ident}: URL de prova inválida')
        try:
            value = ref.get('consulta')
            if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                raise ValueError()
            date.fromisoformat(value)
        except ValueError:
            errors.append(f'{ident}: consulta requer data ISO válida')
        status = ref.get('gabarito_status')
        if status not in ('definitivo', 'justificativa_oficial', 'nao_verificado', 'anulado'):
            errors.append(f'{ident}: situação do gabarito inválida')
        if status in ('definitivo', 'justificativa_oficial') and not url(ref.get('gabarito_url')):
            errors.append(f'{ident}: URL do gabarito/justificativa ausente')
    seen, ids = set(), set()
    for record in records:
        if not isinstance(record, dict):
            errors.append('Registro de cartão deve ser objeto')
            continue
        ident, line = record.get('id'), record.get('linha')
        if not filled(ident):
            errors.append('Cartão sem ID')
        elif ident in ids:
            errors.append(f'ID duplicado: {ident}')
        else:
            ids.add(ident)
        if type(line) is not int or line not in cards:
            errors.append(f'{ident}: linha não corresponde a D no TSV')
            continue
        if line in seen:
            errors.append(f'{ident}: linha D duplicada')
        seen.add(line)
        row = cards[line]
        if record.get('sha256') != fingerprint(row):
            errors.append(f'{ident}: SHA256 diverge; refazer revisão após alteração')
        if 'Estilo_Cebraspe' not in row[2].split():
            errors.append(f'{ident}: tag Estilo_Cebraspe ausente')
        answer = 'C' if row[1].startswith('✅ Certo<br><br>') else 'E' if row[1].startswith('❌ Errado<br><br>') else None
        if answer is None or record.get('gabarito') != answer:
            errors.append(f'{ident}: gabarito declarado diverge do verso')
        for key in ANALYSIS:
            if not filled(record.get(key)):
                errors.append(f'{ident}: {key} ausente')
        sources = record.get('fontes_conteudo')
        if not isinstance(sources, list) or not sources or not all(url(x) for x in sources):
            errors.append(f'{ident}: fontes_conteudo requer URLs consultadas')
        linked = record.get('referencias')
        if not isinstance(linked, list) or not all(isinstance(x, str) for x in linked):
            errors.append(f'{ident}: referencias deve listar IDs')
            linked = []
        for key in linked:
            if key not in ref_map:
                errors.append(f'{ident}: referência desconhecida {key}')
            elif ref_map[key].get('gabarito_status') == 'anulado':
                errors.append(f'{ident}: referência anulada não sustenta aprovação; registrar fora do conjunto de apoio')
        fidelity = record.get('fidelidade')
        if fidelity == 'comparada':
            if not linked or not filled(record.get('comparacao')):
                errors.append(f'{ident}: comparação exige referência e justificativa')
        elif fidelity == 'inspiracao_geral':
            if not filled(record.get('limitacao')):
                errors.append(f'{ident}: inspiração geral exige limitação')
        else:
            errors.append(f'{ident}: fidelidade inválida')
        if record.get('segunda_conferencia') is not True or record.get('decisao') != 'APROVAR':
            errors.append(f'{ident}: revisão final não concluída; não exportar como aprovado')
        rubric = record.get('rubrica')
        for criterion in CRITERIA:
            entry = rubric.get(criterion) if isinstance(rubric, dict) else None
            allowed = ('PASSA', 'PENDENTE') if criterion == 'comparacao' and fidelity == 'inspiracao_geral' else ('PASSA',)
            if not isinstance(entry, dict) or entry.get('resultado') not in allowed or not filled(entry.get('evidencia')):
                errors.append(f'{ident}: rubrica {criterion} incompleta ou não aprovada')
    for line in sorted(set(cards) - seen):
        errors.append(f'linha {line}: D sem revisão registrada')
    return errors


def read_package(path):
    if path.is_dir():
        def read(name, required=False):
            target = path / name
            if not target.exists() and not required:
                return None
            if target.stat().st_size > LIMIT:
                raise ValueError('Arquivo excede 20 MB')
            return target.read_bytes()
        return read(CE, True), read(REPORT)
    with zipfile.ZipFile(path) as archive:
        def read(name, required=False):
            matches = [info for info in archive.infolist() if info.filename == name]
            if not matches and not required:
                return None
            if len(matches) != 1 or matches[0].file_size > LIMIT:
                raise ValueError(f'{name}: ausente, duplicado ou maior que 20 MB')
            return archive.read(matches[0])
        return read(CE, True), read(REPORT)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args(argv)
    try:
        errors = validate(*read_package(args.source))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f'ERRO DE LEITURA: {exc}')
        return 2
    if errors:
        print('REGISTRO REPROVADO:')
        for error in errors:
            print(' -', error)
        return 1
    print('REGISTRO CONSISTENTE (ou lote sem D): cobertura e declarações verificadas.')
    print('Não comprova consulta às fontes, correção, autoria, dificuldade ou fidelidade Cebraspe. Revisão semântica obrigatória.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
