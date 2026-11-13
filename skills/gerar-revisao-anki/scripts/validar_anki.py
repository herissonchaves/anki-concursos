#!/usr/bin/env python3
"""Anki-Concursos v2.5: estrutura, contagem, perfis e equilíbrio dos rápidos.

Verificação sintática; não substitui auditoria semântica, fontes ou provas.
Limite do usuário deve ser checado na geração; quando fornecido ao CLI, --max-cards
confere contagem de cartões reais (C/E + índices distintos de Cloze).
"""
from __future__ import annotations
import argparse
import html
import re
import sys
import unicodedata
import zipfile
from pathlib import Path
import importlib.util
_balance_path = Path(__file__).with_name('validar_gabaritos_rapidos.py')
_balance_spec = importlib.util.spec_from_file_location('anki_balance', _balance_path)
_balance_module = importlib.util.module_from_spec(_balance_spec)
_balance_spec.loader.exec_module(_balance_module)
contar_rapidos = _balance_module.contar_rapidos
contar_modos = _balance_module.contar_modos
from pathlib import Path

REQUIRED = (
    'anki_certo_errado.tsv', 'anki_cloze.tsv', 'LEIA-ME.txt',
    'relatorios/selecao_e_fontes.txt', 'relatorios/economia_de_revisao.txt',
    'relatorios/auditoria_pedagogica.txt',
)
# Um índice distinto por cartão. Vários trechos de mesmo índice: um cartão.
CLOZE_ANY = re.compile(r'\{\{c([1-9]\d*)::([^{}]*?)\}\}')
HTML_TAG = re.compile(r'<[^>]*>')
QUICK = 'Tipo_Revisao_Rapida'
HARD = 'Tipo_Desafiadora_Cebraspe'
BAD_META = [
    r'\b(?:segundo|conforme|de acordo com|como consta (?:em|no|na)|como visto (?:em|no|na))\s+'
    r'(?:(?:o|a|os|as|este|esta|esse|essa|aquele|aquela|um|uma)\s+)?'
    r'(?:material(?:\s+(?:enviado|de estudo|de estudos))?|pdf|apostila|arquivo(?:\s+anexo)?|'
    r'texto(?:-base|\s+(?:enviado|apresentado|anexo|estudado|fornecido))?|'
    r'documento(?:\s+(?:anexo|enviado|apresentado))?|print(?:s)?(?:\s+enviado(?:s)?)?|'
    r'aula\s+(?:estudada|do\s+pdf|do\s+material))\b',
    r'\b(?:o|a|este|esta|esse|essa|no|na|nesse|nessa)\s+'
    r'(?:material|pdf|apostila|arquivo(?:\s+anexo)?|texto-base|documento\s+anexo)\s+'
    r'(?:apresenta|afirma|descreve|informa|define|ensina|mostra|ressalta|explica|destaca|considera|diz|trata|indica|classifica|contem|aborda)\b',
    r'\b(?:na|nesta|nessa|conforme|segundo|de acordo com)\s+(?:a\s+)?'
    r'(?:aula\s+(?:estudada|anexa|do\s+material|do\s+pdf)|apostila|pagina\s+\d+)\b',
    r'\b(?:como|conforme)\s+(?:foi\s+)?(?:vimos|estudamos|aprendemos|lido|explicado)\s+'
    r'(?:anteriormente|no\s+material|no\s+pdf|nesta\s+apostila|na\s+aula)\b',
    r'\b(?:material|pdf|arquivo|texto|apostila|documento)\s+(?:enviado|anexado|em\s+anexo|fornecido)\b',
    r'\b(?:segundo|conforme|de acordo com)\s+a\s+comparacao\s+(?:apresentada|exibida)\b',
    r'\b(?:no|na|pelo)\s+(?:pdf|arquivo\s+anexo|texto-base|material\s+de\s+estudo)\b',
    r'\b(?:apresentad[ao]s?|descrit[ao]s?|exibid[ao]s?|feita|feito|estudad[ao]s?)\s+(?:no|na)\s+(?:pdf|material|apostila|aula|arquivo)\b',
    r'\b(?:segundo|conforme|de acordo com)\s+(?:a|o)\s+(?:(?!\.\s).){0,85}\s+(?:estudad[ao]s?|apresentad[ao]s?|feita|feito)\b',
    r'\b(?:visao|interpretacao|classificacao|concepcao|teoria)\s+.{0,85}?\s+(?:apresentad[ao]|estudad[ao]|descrita)\s+(?:no|na)\s+(?:pdf|material|apostila|arquivo|aula)\b',
]
META_RE = [re.compile(p, re.I) for p in BAD_META]
EXPL_LABEL_RE = re.compile(r'\b(?:explicacao|justificativa|fundamentacao)\s*:', re.I)


def folded(s: str) -> str:
    s = html.unescape(HTML_TAG.sub(' ', s))
    return ''.join(c for c in unicodedata.normalize('NFD', s.casefold()) if unicodedata.category(c) != 'Mn')


def parse_cloze(text: str, errors: list[str], position: str) -> set[int]:
    """Cheque estrutural sem limite artificial de palavras ou posição.

    Não suporta aninhamento (decisão explícita da versão 1.6 por confiabilidade
    da auditoria estática); o Anki aceita aninhamento em versões modernas.
    """
    found = list(CLOZE_ANY.finditer(text))
    indices: set[int] = set()
    if not found:
        errors.append(f'{position}: Cloze ausente ou sintaxe inválida')
        return indices
    plain = CLOZE_ANY.sub('', text)
    if '{{' in plain or '}}' in plain or re.search(r'\{\{c\d*:', plain):
        errors.append(f'{position}: marcação Cloze malformada ou aninhada')
    for m in found:
        idx = int(m.group(1))
        payload = m.group(2)
        if '::' in payload:
            answer, hint = payload.split('::', 1)
            if not hint.strip():
                errors.append(f'{position}: dica Cloze vazia no índice c{idx}')
            if '::' in hint:
                errors.append(f'{position}: campo Cloze c{idx} tem separadores adicionais')
            if folded(hint).strip() == folded(answer).strip() and answer.strip():
                errors.append(f'{position}: dica Cloze idêntica à resposta no índice c{idx}')
        else:
            answer = payload
        if not answer.strip() or not any(ch.isalnum() for ch in answer):
            errors.append(f'{position}: resposta Cloze vazia ou sem conteúdo no índice c{idx}')
        if '\n' in payload or '\t' in payload:
            errors.append(f'{position}: Cloze contém quebra de linha ou TAB')
        indices.add(idx)
    if indices != set(range(1, max(indices)+1)):
        errors.append(f'{position}: índices Cloze devem ser contíguos, começando em c1')
    return indices


def count_cloze_cards(body: bytes, errors: list[str] | None = None) -> dict[str, int]:
    """Retorna notas e cartões efetivos; índices repetidos na nota contam 1."""
    errs = errors if errors is not None else []
    try:
        text = body.decode('utf-8')
    except UnicodeDecodeError:
        errs.append('anki_cloze.tsv: UTF-8 inválido')
        return {'notas_cloze': 0, 'cartoes_cloze': 0}
    notes, cards = 0, 0
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) != 3 or not all(x.strip() for x in parts):
            # verify_tsvo tem responsabilidade pela mensagem de formato.
            continue
        notes += 1
        cards += len(parse_cloze(parts[0], errs, f'anki_cloze.tsv:{n}'))
    return {'notas_cloze': notes, 'cartoes_cloze': cards}


def verify_tsvo(name: str, body: bytes, errors: list[str]) -> int:
    try:
        t = body.decode('utf-8')
    except UnicodeDecodeError as e:
        errors.append(f'{name}: UTF-8 inválido: {e}')
        return 0
    if t.startswith('\ufeff'):
        errors.append(f'{name}: BOM UTF-8 inesperado')
    seen = set()
    count = 0
    for i, line in enumerate(t.splitlines(), 1):
        if not line.strip():
            errors.append(f'{name}:{i}: linha vazia')
            continue
        parts = line.split('\t')
        if len(parts) != 3 or not all(x.strip() for x in parts):
            errors.append(f'{name}:{i}: requer 3 campos não vazios / 2 TABs')
            continue
        front, back, tags = parts
        count += 1
        if '\\n' in front + back or '\\t' in front + back:
            errors.append(f'{name}:{i}: sequência escapada literal \\n/\\t')
        for field, value in (('frente/texto', front), ('verso/extra', back)):
            normalized = folded(value)
            for pattern in META_RE:
                match = pattern.search(normalized)
                if match:
                    errors.append(f'{name}:{i} {field}: menção à fonte proibida ({match.group()!r})')
                    break
        if EXPL_LABEL_RE.search(folded(back)):
            errors.append(f'{name}:{i}: rótulo explicativo proibido')
        if not re.fullmatch(r'[A-Za-zÀ-ÖØ-öø-ÿ0-9_ \-]+', tags):
            errors.append(f'{name}:{i}: tags com caracteres incompatíveis')
        sem = re.sub(r'\s+', ' ', folded(front)).strip()
        if sem in seen:
            errors.append(f'{name}:{i}: duplicata textual')
        seen.add(sem)
        if name == 'anki_certo_errado.tsv':
            if not re.match(r'^(?:✅ Certo|❌ Errado)<br><br>\S', back):
                errors.append(f'{name}:{i}: gabarito+explicação devem iniciar o verso')
            if re.search(r'\bcerto\s+ou\s+errado\b', folded(front)):
                errors.append(f'{name}:{i}: frente expõe comando Certo ou Errado')
            if '{{' in front + back or '}}' in front + back:
                errors.append(f'{name}:{i}: C/E não pode ter Cloze')
        else:
            parse_cloze(front, errors, f'{name}:{i}')
            if '{{' in back or '}}' in back:
                errors.append(f'{name}:{i}: Extra não deve conter lacuna')
            if QUICK in tags.split() or HARD in tags.split():
                errors.append(f'{name}:{i}: tag de C/E proibida em Cloze')
    return count


def validate_new_cloze(body: bytes, errors: list[str]) -> None:
    """Policy for new notes only; list meaning and Extra quality need human review."""
    try:
        text = body.decode('utf-8')
    except UnicodeDecodeError:
        return  # UTF-8 error is reported by verify_tsvo.
    for number, row in enumerate(text.splitlines(), 1):
        fields = row.split('\t')
        if len(fields) != 3 or not row.strip():
            continue
        matches = list(CLOZE_ANY.finditer(fields[0]))
        if not matches or any(match.group(1) != '1' for match in matches):
            errors.append(f'anki_cloze.tsv:{number}: nota nova requer uma ou mais omissões, todas com índice c1')


def validate_type_distribution(body: bytes, errors: list[str], require_types: bool = False, require_ratio: bool = False) -> dict[str, int]:
    try:
        text = body.decode('utf-8')
    except UnicodeDecodeError:
        return {'rapidos': 0, 'desafiadores': 0, 'sem_tipo': 0}
    rows = [row.split('\t') for row in text.splitlines() if row.strip()]
    tags_per_row = [set(row[2].split()) for row in rows if len(row) == 3]
    rapidos = sum(QUICK in t for t in tags_per_row)
    desafiadores = sum(HARD in t for t in tags_per_row)
    sem_tipo = sum(QUICK not in t and HARD not in t for t in tags_per_row)
    both = sum(QUICK in t and HARD in t for t in tags_per_row)
    if both:
        errors.append(f'anki_certo_errado.tsv: {both} cartões apresentam simultaneamente os dois tipos')
    if rapidos+desafiadores or require_types:
        if sem_tipo:
            errors.append(f'anki_certo_errado.tsv: {sem_tipo} cartões sem tag obrigatória de modalidade')
        # Legacy require_ratio is retained for compatibility and has no effect.
    return {'rapidos': rapidos, 'desafiadores': desafiadores, 'sem_tipo': sem_tipo}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('path', help='Diretório ou ZIP exportado para Anki')
    p.add_argument('--new', action='store_true', help='Lote novo: tags e equilíbrio; perfil mixed exige R/D, sem limite de rápidos')
    p.add_argument('--max-cards', type=int, help='Teto explícito de CARTÕES efetivos do usuário')
    p.add_argument('--require-r-le-d', action='store_true', help='Opção legada sem efeito: rápidos não têm limite de proporção')
    p.add_argument('--profile', choices=('mixed', 'focused'), default='mixed')
    p.add_argument('--exception-reason', default='', help='Justificativa obrigatória do perfil focado')
    p.add_argument('--balance-exception', default='', help='Motivo concreto para não impor 50/50')
    args = p.parse_args()
    source = Path(args.path)
    errors: list[str] = []
    if args.profile == 'focused' and not args.exception_reason.strip():
        errors.append('Perfil focado requer --exception-reason não vazio')
    if args.profile == 'mixed' and args.exception_reason.strip():
        errors.append('--exception-reason requer --profile focused')
    if not args.new and (args.profile != 'mixed' or args.balance_exception.strip()):
        errors.append('Perfil e exceções de geração requerem --new')
    items: dict[str, bytes] = {}
    if source.is_dir():
        for k in REQUIRED:
            f = source / k
            if not f.is_file():
                errors.append(f'Arquivo obrigatório ausente: {k}')
            else:
                items[k] = f.read_bytes()
    elif source.is_file() and zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as z:
            if z.testzip() is not None:
                errors.append('CRC ZIP falhou')
            for k in REQUIRED:
                try:
                    info = z.getinfo(k)
                    if info.file_size > 20_000_000:
                        errors.append(f'Arquivo excessivo: {k}')
                    else:
                        items[k] = z.read(k)
                except KeyError:
                    errors.append(f'Arquivo obrigatório ausente: {k}')
            for info in z.infolist():
                if info.filename.startswith('/') or '..' in Path(info.filename).parts:
                    errors.append(f'Caminho ZIP inválido: {info.filename}')
    else:
        errors.append('É preciso informar diretório existente ou ZIP válido')
    counts = {}
    for k in ('anki_certo_errado.tsv', 'anki_cloze.tsv'):
        if k in items:
            counts[k] = verify_tsvo(k, items[k], errors)
    dist = validate_type_distribution(items.get('anki_certo_errado.tsv', b''), errors, require_types=args.new, require_ratio=False)
    cloze = count_cloze_cards(items.get('anki_cloze.tsv', b''))
    if args.new:
        validate_new_cloze(items.get('anki_cloze.tsv', b''), errors)
        _, balance_errors = contar_modos(items.get('anki_certo_errado.tsv', b''), strict_balance=True)
        if args.balance_exception.strip():
            errors.append('Lotes novos exigem 50/50 por modo; --balance-exception não é permitido')
        errors.extend(balance_errors)
    if args.new and args.profile == 'mixed':
        for name, count in (('rápidos', dist['rapidos']), ('desafiadores', dist['desafiadores'])):
            if count == 0:
                errors.append(f'Lote novo deve incluir rápidos e desafiadores: faltam {name}')
    total = counts.get('anki_certo_errado.tsv', 0) + cloze['cartoes_cloze']
    if not counts or total == 0:
        errors.append('Não foram encontrados cartões aprovados (arquivos vazios)')
    if args.max_cards is not None:
        if args.max_cards < 0:
            errors.append('--max-cards não pode ser negativo')
        elif total > args.max_cards:
            errors.append(f'Teto do usuário excedido: {total} cartões efetivos > {args.max_cards}')
    if errors:
        print(f'REPROVADO: {len(errors)} ocorrência(s)')
        for error in errors: print(' -', error)
        return 1
    if args.new:
        print(f'Perfil={args.profile}; motivo={args.exception_reason.strip() or "padrão"}; exceção equilíbrio={args.balance_exception.strip() or "nenhuma"}')
    print('APROVADO NA AUDITORIA ESTÁTICA — não substitui avaliação pedagógica')
    print('Notas:', ', '.join(f'{k}={v}' for k, v in counts.items()))
    print('Modalidades:', ', '.join(f'{k}={v}' for k, v in dist.items()))
    print(f'notas_cloze={cloze["notas_cloze"]}, cartoes_cloze={cloze["cartoes_cloze"]}, total_cartoes={total}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
