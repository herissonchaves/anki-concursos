#!/usr/bin/env python3
"""Barreira documental de R/C e resolução do lint em exportações NOVAS.

Não resolve questões, não consulta fontes e não certifica aprendizagem.
Não cria nem preenche auditorias. Coleções existentes usam o fluxo de leitura.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
import zipfile

REPORT = 'relatorios/revisao_recuperacao.json'
FILES = ('anki_certo_errado.tsv', 'anki_cloze.tsv')
MAX_BYTES = 20_000_000
_spec = importlib.util.spec_from_file_location('anki_review_lint', Path(__file__).with_name('auditar_clareza.py'))
lint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lint)
_structure_spec = importlib.util.spec_from_file_location('anki_review_structure', Path(__file__).with_name('validar_anki.py'))
structure = importlib.util.module_from_spec(_structure_spec)
_structure_spec.loader.exec_module(structure)


def fingerprint(row):
    return hashlib.sha256('\t'.join(row).encode('utf-8')).hexdigest()


def batch_hash(items):
    # Nomes e fronteiras explícitos evitam ambiguidades entre os dois arquivos.
    payload = [[name, hashlib.sha256(items.get(name, b'')).hexdigest()] for name in FILES]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False).encode('utf-8')).hexdigest()


def cards(items):
    rows = []
    for name in FILES:
        for number, line in enumerate(items.get(name, b'').decode('utf-8').splitlines(), 1):
            if not line.strip():
                continue
            fields = line.split('\t')
            if len(fields) != 3:
                raise ValueError(f'{name}:{number}: requer três campos TSV')
            front, back, tags = fields
            typ = ('cloze' if name == FILES[1] else 'rapida' if 'Tipo_Revisao_Rapida' in tags.split()
                   else 'desafiadora' if 'Tipo_Desafiadora_Cebraspe' in tags.split() else 'C/E-sem-tipo')
            rows.append(dict(id=f'{name}:{number}', front=front, back=back, tags=tags, tipo=typ))
    return rows


def signals(items):
    rows = cards(items)
    hashes = {row['id']: fingerprint([row['front'], row['back'], row['tags']]) for row in rows}
    result = []
    for issue in lint.scan(rows):
        content = [issue['id'], issue['sinal'], issue['detalhes'], hashes.get(issue['id'], batch_hash(items))]
        result.append(dict(issue, sinal_id=hashlib.sha256(json.dumps(content, ensure_ascii=False).encode('utf-8')).hexdigest()))
    return result


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def valid_source(value):
    if not isinstance(value, dict) or not all(nonblank(value.get(key)) for key in ('url', 'consulta', 'trecho')):
        return False
    try:
        parsed = urlsplit(value['url'])
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value['consulta']):
            return False
        date.fromisoformat(value['consulta'])
        return parsed.scheme in ('https', 'http') and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Chave JSON duplicada: {key}')
        result[key] = value
    return result


def validate_cloze_coverage(row, coverage, challenges, errors):
    ident = row['id']
    count = sum(1 for _ in structure.CLOZE_ANY.finditer(row['front']))
    expected = {str(number) for number in range(1, count + 1)}
    if not expected or not isinstance(coverage, dict) or coverage.keys() != expected:
        errors.append(f'{ident}: desafiadores_por_lacuna deve cobrir todas as lacunas na ordem do Texto')
        return
    for gap, references in coverage.items():
        if not isinstance(references, list) or not references or any(
            not isinstance(reference, str) or reference not in challenges for reference in references
        ):
            errors.append(f'{ident}: lacuna {gap} requer IDs de C/E desafiadores do mesmo lote')


def validate(items, report):
    errors = []
    if report is None:
        return [f'Revisão de recuperação ausente: {REPORT}; não fabricar aprovação']
    try:
        data = json.loads(report.decode('utf-8'), object_pairs_hook=_unique_object)
        rows = cards(items)
        current_signals = {item['sinal_id']: item for item in signals(items)}
    except (ValueError, UnicodeError) as exc:
        return [f'Revisão de recuperação inválida: {exc}']
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        return ['Revisão de recuperação requer objeto e schema_version=1']
    if data.get('sha256_lote') != batch_hash(items):
        errors.append('SHA256 do lote divergente; refazer a revisão após alteração dos TSVs')
    if not nonblank(data.get('revisor')) or data.get('tipo_revisao') not in ('autorevisao', 'independente'):
        errors.append('Identificar revisor e tipo_revisao: autorevisao ou independente; não inventar independência')
    expected = {row['id']: row for row in rows if row['tipo'] in ('rapida', 'cloze')}
    challenges = {
        row['id'] for row in rows
        if row['tipo'] == 'desafiadora' and 'Estilo_Cebraspe' in row['tags'].split()
    }
    records = data.get('cartoes')
    if not isinstance(records, list):
        errors.append('cartoes requer lista de registros R/C')
        records = []
    seen = set()
    for record in records:
        if not isinstance(record, dict):
            errors.append('Registro R/C deve ser objeto')
            continue
        ident = record.get('id')
        if not isinstance(ident, str) or ident not in expected or ident in seen:
            errors.append(f'Registro R/C desconhecido ou duplicado: {ident!r}')
            continue
        seen.add(ident)
        row = expected[ident]
        if row['tipo'] == 'cloze':
            validate_cloze_coverage(row, record.get('desafiadores_por_lacuna'), challenges, errors)
        if record.get('sha256') != fingerprint([row['front'], row['back'], row['tags']]):
            errors.append(f'{ident}: SHA256 divergente')
        for key in ('alvo', 'solucao'):
            if not nonblank(record.get(key)):
                errors.append(f'{ident}: {key} requer evidência específica')
        # Opcionais desde a 2.24 (economia de tokens): registrados só quando houver algo a dizer.
        for key in ('alternativa_concorrente', 'recuperacao', 'feedback'):
            if key in record and not nonblank(record.get(key)):
                errors.append(f'{ident}: {key} declarado vazio; omita o campo ou escreva a evidência')
        sources = record.get('fontes')
        if not isinstance(sources, list) or not sources or not all(valid_source(value) for value in sources):
            errors.append(f'{ident}: fontes requer URL, consulta ISO e trecho/localizador efetivamente conferido')
        if record.get('decisao') != 'APROVAR' or record.get('segunda_conferencia') is not True:
            errors.append(f'{ident}: aprovação e segunda conferência pendentes')
    for ident in sorted(expected.keys() - seen):
        errors.append(f'{ident}: revisão R/C ausente')
    resolutions = data.get('sinais')
    if not isinstance(resolutions, list):
        errors.append('sinais requer lista, mesmo quando vazia')
        resolutions = []
    seen_signals = set()
    for resolution in resolutions:
        if not isinstance(resolution, dict):
            errors.append('Resolução de sinal deve ser objeto')
            continue
        key = resolution.get('sinal_id')
        if not isinstance(key, str) or key not in current_signals or key in seen_signals:
            errors.append(f'Sinal desconhecido, obsoleto ou duplicado: {key!r}')
            continue
        seen_signals.add(key)
        if resolution.get('decisao') != 'EXCECAO_JUSTIFICADA' or not nonblank(resolution.get('motivo')):
            errors.append(f'{current_signals[key]["id"]}: sinal requer correção ou EXCECAO_JUSTIFICADA com motivo específico')
    for key in sorted(current_signals.keys() - seen_signals):
        issue = current_signals[key]
        errors.append(f'{issue["id"]}: sinal pendente {issue["sinal"]} ({key})')
    return errors


def read_package(path):
    path = Path(path)
    names = (*FILES, REPORT)
    if path.is_dir():
        values = {}
        for name in names:
            file = path/name
            if file.is_file():
                if file.stat().st_size > MAX_BYTES:
                    raise ValueError(f'Arquivo excessivo: {name}')
                values[name] = file.read_bytes()
    else:
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise ValueError('CRC ZIP inválido')
            values = {}
            for name in names:
                matches = [item for item in archive.infolist() if item.filename == name]
                if len(matches) > 1:
                    raise ValueError(f'Entrada ZIP duplicada: {name}')
                if matches:
                    if matches[0].file_size > MAX_BYTES:
                        raise ValueError(f'Arquivo excessivo: {name}')
                    values[name] = archive.read(matches[0])
    if any(name not in values for name in FILES):
        raise ValueError('Ambos os TSVs são obrigatórios')
    return {name: values[name] for name in FILES}, values.get(REPORT)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path)
    parser.add_argument('--listar-sinais', action='store_true', help='Diagnóstico JSON; não aprova nem cria relatório')
    args = parser.parse_args(argv)
    try:
        items, report = read_package(args.path)
        if args.listar_sinais:
            summary = [dict(id=row['id'], tipo=row['tipo'], sha256=fingerprint([row['front'], row['back'], row['tags']])) for row in cards(items)]
            print(json.dumps(dict(sha256_lote=batch_hash(items), cartoes=summary, sinais=signals(items)), ensure_ascii=False, indent=2))
            return 0
        errors = validate(items, report)
    except (OSError, ValueError, UnicodeError, zipfile.BadZipFile) as exc:
        print(f'ERRO DE LEITURA: {exc}', file=sys.stderr)
        return 2
    if errors:
        print('REVISÃO DOCUMENTAL REPROVADA')
        for error in errors:
            print(' -', error)
        return 1
    print('REVISÃO DOCUMENTAL CONSISTENTE; não certifica verdade, leitura da fonte ou aprendizagem')
    return 0


if __name__ == '__main__':
    sys.exit(main())
