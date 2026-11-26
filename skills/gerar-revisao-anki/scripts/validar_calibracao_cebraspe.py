#!/usr/bin/env python3
"""Checa registros de calibração de D novos; NÃO julga semântica nem fontes.

Uso: python validar_calibracao_cebraspe.py DIRETORIO_OU_ZIP
Não altera arquivos, coleção, gabaritos ou tags.

schema_version 2 (lotes a partir da 2.16) exige `banca` e `formato` em cada
referência, referência CESPE/Cebraspe Certo/Errado nos D comparados e, em todo
D, uma questão de outra banca vinculada ou `outras_bancas_pendencia`. Desde a 2.31, no
schema 2, cada ID de `referencias` e `referencias_sem_prova` de um D precisa estar nas tags
da linha do D (a tag é o nome do arquivo da questão em `referencias/questoes/`).
Desde a 2.37 (schema_version 3, o que o `montar_lote.py` grava), todo D precisa de ao menos uma
questão real de concurso em `referencias` ou `referencias_sem_prova`: `outras_bancas_pendencia` só
complementa um D que já tem questão e nunca a substitui. schema_version 1 e 2 continuam aceitos
para lotes anteriores, com as regras da época.
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
HARDS = {'Desafiadora', 'Tipo_Desafiadora_Cebraspe'}  # 2.33: novo e antigo
CRITERIA = ('correcao', 'determinacao', 'operacao_d', 'comparacao', 'autoria', 'feedback', 'linguagem_didatica', 'utilidade')
# Desde a 2.24 (economia de tokens), estes passam com resultado PASSA mesmo sem texto de evidência.
CRITERIA_SEM_EVIDENCIA = ('autoria', 'feedback', 'utilidade')
ANALYSIS = ('alvo', 'operacao_autoral', 'regra', 'dado_decisivo', 'solucao',
            'erro_plausivel', 'leitura_concorrente', 'originalidade')
FORMATS = ('certo_errado', 'multipla_escolha')
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


def cebraspe(ref):
    banca = ref.get('banca')
    return isinstance(banca, str) and bool(re.search(r'cespe|cebraspe', banca, re.IGNORECASE))


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
        elif HARDS & set(row[2].split()):
            cards[number] = row
    if not cards:
        return errors  # Não impõe metadados D a rápidos/Cloze ou coleção antiga.
    if report is None:
        return errors + [f'{REPORT} ausente: {len(cards)} D sem registro; não fabricar revisão']
    try:
        data = json.loads(report.decode('utf-8'))
    except (ValueError, UnicodeError):
        return errors + ['Registro JSON inválido']
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data['schema_version'] not in (1, 2, 3):
        return errors + ['schema_version deve ser 1 ou 2 (legados) ou 3']
    v2 = data['schema_version'] >= 2
    v3 = data['schema_version'] >= 3
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
        for key in ('concurso', 'cargo', 'caderno', 'item', 'operacao_observada') + (('banca',) if v2 else ()):
            if not filled(ref.get(key)):
                errors.append(f'{ident}: {key} ausente')
        if v2 and ref.get('formato') not in FORMATS:
            errors.append(f'{ident}: formato deve ser certo_errado ou multipla_escolha')
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
    # Questões sem prova oficial localizada (ex.: do PDF enviado): inspiração, nunca fidelidade comparada.
    sem_prova = data.get('referencias_sem_prova', [])
    sem_map = {}
    if not isinstance(sem_prova, list):
        errors.append('referencias_sem_prova deve ser lista')
        sem_prova = []
    for ref in sem_prova:
        if not isinstance(ref, dict) or not filled(ref.get('id')):
            errors.append('Referência sem prova sem id válido')
            continue
        for key in ('banca', 'formato', 'operacao_observada', 'fonte_descoberta'):
            if not filled(ref.get(key)):
                errors.append(f'{ref["id"]}: {key} ausente (referência sem prova)')
        if ref['id'] in ref_map:
            errors.append(f'{ref["id"]}: está em referencias e em referencias_sem_prova')
        sem_map[ref['id']] = ref
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
        sem_linked = record.get('referencias_sem_prova', [])
        if not isinstance(sem_linked, list) or not all(isinstance(x, str) for x in sem_linked):
            errors.append(f'{ident}: referencias_sem_prova deve listar IDs')
            sem_linked = []
        for key in sem_linked:
            if key not in sem_map:
                errors.append(f'{ident}: referência sem prova desconhecida {key}')
        tags = row[2].split()  # 2.31: cada questão de origem vira tag do D (nome do arquivo no banco)
        for key in dict.fromkeys(linked + sem_linked) if v2 else ():
            if key not in tags:
                errors.append(f'{ident}: tag da questão de origem {key} ausente')
        fidelity = record.get('fidelidade')
        known = [ref_map[key] for key in linked if key in ref_map]
        inspiracoes = known + [sem_map[key] for key in sem_linked if key in sem_map]
        if v3 and not inspiracoes:
            errors.append(f'{ident}: D sem questão real de concurso em referencias ou referencias_sem_prova (2.37); '
                          'outras_bancas_pendencia não substitui a questão')
        if v2:
            if not any(not cebraspe(ref) for ref in inspiracoes) and not filled(record.get('outras_bancas_pendencia')):
                errors.append(f'{ident}: vincular questão de outra banca ou registrar outras_bancas_pendencia com as buscas feitas')
        if fidelity == 'comparada':
            if not linked or not filled(record.get('comparacao')):
                errors.append(f'{ident}: comparação exige referência e justificativa')
            elif v2 and not any(cebraspe(ref) and ref.get('formato') == 'certo_errado' for ref in known):
                errors.append(f'{ident}: comparada exige referência CESPE/Cebraspe Certo/Errado; outra banca não basta')
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
            evidencia_ok = filled(entry.get('evidencia')) if isinstance(entry, dict) else False
            if criterion in CRITERIA_SEM_EVIDENCIA and isinstance(entry, dict) and entry.get('evidencia', '') == '':
                evidencia_ok = True
            if not isinstance(entry, dict) or entry.get('resultado') not in allowed or not evidencia_ok:
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
