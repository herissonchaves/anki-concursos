#!/usr/bin/env python3
"""Empacota cartões Anki com fotografias/diagramas reais já obtidos e auditados.

Não pesquisa, gera, redesenha nem baixa imagens. Não autentica licenças: exige
manifesto de proveniência para verificação humana. Impede cartões com img ausente.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import tempfile
import zipfile

from exportar_anki import (
    add_validation_options,
    check_recovery,
    deck_id,
    export as export_text,
    publish_packages,
    tsv_rows,
    validate_package_paths,
    validation_args,
)

COLS = ('arquivo', 'cartao_id', 'pagina_origem', 'arquivo_url', 'autor',
        'licenca', 'data_consulta', 'motivo_educacional', 'status')
NAME = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*\.(?:jpe?g|png|webp)$', re.I)
MAX_SIZE = 15_000_000


class Images(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.src = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'img':
            d = dict(attrs)
            self.src.append(d.get('src', ''))


def signature(data: bytes, suffix: str) -> bool:
    e = suffix.lower()
    if e in ('.jpg', '.jpeg'):
        return data.startswith(b'\xff\xd8\xff') and data.endswith(b'\xff\xd9')
    if e == '.png':
        return data.startswith(b'\x89PNG\r\n\x1a\n')
    if e == '.webp':
        return data.startswith(b'RIFF') and data[8:12] == b'WEBP'
    return False


def inspect_images(ce: Path, cloze: Path, folder: Path, reports: Path):
    references = set()
    for src in (ce, cloze):
        for n, (front, back, tags) in enumerate(tsv_rows(src), 1):
            for position, field in enumerate((front, back)):
                if '<img' in field.lower():
                    parsed = Images()
                    parsed.feed(field)
                    if position == 1 and parsed.src:
                        raise ValueError(f'{src.name}:{n}: imagem deve estar na FRENTE/Texto, não no verso/Extra')
                    if position == 0:
                        for filename in parsed.src:
                            if not NAME.fullmatch(filename):
                                raise ValueError(f'{src.name}:{n}: src não é nome seguro de mídia local: {filename}')
                            references.add(filename)
    if not references:
        raise ValueError('Nenhuma imagem referenciada nos campos de frente/Texto; use exportador de texto puro')
    if not folder.is_dir():
        raise ValueError('Pasta de mídia original ausente')
    files = {p.name: p for p in folder.iterdir() if p.is_file()}
    if any(p.is_dir() for p in folder.iterdir()):
        raise ValueError('Subpastas dentro de midia/ não são permitidas')
    if set(files) != references:
        raise ValueError(f'Mídias incoerentes; faltantes={sorted(references-set(files))}, sem uso={sorted(set(files)-references)}')
    digests = {}
    for name, p in files.items():
        if p.stat().st_size > MAX_SIZE or p.stat().st_size == 0:
            raise ValueError(f'Imagem vazia ou excessiva: {name}')
        blob = p.read_bytes()
        if not signature(blob, p.suffix):
            raise ValueError(f'Imagem não é arquivo JPG/PNG/WebP íntegro pelo cabeçalho/rodapé: {name}')
        digests[name] = hashlib.sha256(blob).hexdigest()
    manifest = reports / 'fontes_visuais.tsv'
    if not manifest.is_file():
        raise ValueError('Relatório fontes_visuais.tsv obrigatório para lote com imagem')
    with manifest.open('r', encoding='utf-8-sig', newline='') as f:
        rdr = csv.DictReader(f, delimiter='\t')
        if not set(COLS).issubset(rdr.fieldnames or ()):
            raise ValueError(f'fontes_visuais.tsv requer colunas: {COLS}')
        rows = list(rdr)
    described = set()
    for row in rows:
        name = row['arquivo'].strip()
        if name not in references:
            raise ValueError(f'Manifesto menciona mídia inexistente/não usada: {name}')
        if not all(row.get(key, '').strip() for key in COLS):
            raise ValueError(f'Proveniência incompleta no arquivo {name}')
        if not row['pagina_origem'].startswith(('https://', 'http://')):
            raise ValueError(f'URL de origem inválida em {name}')
        if not row['arquivo_url'].startswith(('https://', 'http://')):
            raise ValueError(f'URL original do arquivo inválida em {name}')
        if row.get('sha256', '').strip() and row['sha256'].strip().lower() != digests[name]:
            raise ValueError(f'Hash sha256 não corresponde à mídia de {name}')
        if row['licenca'].casefold() in {'desconhecida', 'não sei', 'indefinida', 'sem licenca', 'sem licença'}:
            raise ValueError(f'Licença sem comprovação declarada para {name}')
        if row['status'].strip().casefold() not in {'aprovada', 'aprovado'}:
            raise ValueError(f'Arquivo {name} não foi aprovado pela auditoria visual')
        described.add(name)
    if described != references:
        raise ValueError(f'Fontes ausentes para arquivos: {sorted(references-described)}')
    return files, digests


def make_apkg(ce, cloze, output: Path, deck: str, image_files: dict[str, Path]):
    try:
        import genanki
    except ImportError as exc:
        raise RuntimeError('APKG com imagem requer genanki; use ZIP/TSV + cópia manual da mídia') from exc
    basic = genanki.Model(1987052101, 'Anki-Concursos - C/E',
        fields=[{'name':'Frente'}, {'name':'Verso'}],
        templates=[{'name':'C/E','qfmt':'{{Frente}}','afmt':'{{FrontSide}}<hr id="answer">{{Verso}}'}])
    clz = genanki.Model(1987052102, 'Anki-Concursos - Cloze',
        fields=[{'name':'Texto'}, {'name':'Extra'}],
        templates=[{'name':'Cloze','qfmt':'{{cloze:Texto}}','afmt':'{{cloze:Texto}}<hr id="answer">{{Extra}}'}],
        model_type=genanki.Model.CLOZE)
    d = genanki.Deck(deck_id(deck), deck)
    for front, back, tags in tsv_rows(ce):
        d.add_note(genanki.Note(model=basic,fields=[front,back],tags=tags.split(),guid=genanki.guid_for(front,'C/E')))
    for txt, extra, tags in tsv_rows(cloze):
        d.add_note(genanki.Note(model=clz,fields=[txt,extra],tags=tags.split(),guid=genanki.guid_for(txt,'Cloze')))
    pkg = genanki.Package(d)
    pkg.media_files = [str(image_files[n]) for n in sorted(image_files)]
    output.parent.mkdir(parents=True,exist_ok=True)
    pkg.write_to_file(str(output))
    with zipfile.ZipFile(output) as z:
        if z.testzip() is not None:
            raise ValueError('CRC do APKG inválido')
        media_map = json.loads(z.read('media'))
        if set(media_map.values()) != set(image_files):
            raise ValueError('APKG não contém a lista correta de imagens')


def export(ce, cloze, reports, midia, output, apkg=None, deck='Anki-Concursos',profile='mixed',exception_reason='',balance_exception='',max_cards=None):
    ce, cloze, reports, midia, output = map(Path, (ce, cloze, reports, midia, output))
    apkg = Path(apkg) if apkg else None
    validate_package_paths(output, apkg)
    policy_args = validation_args(profile,exception_reason,balance_exception,max_cards)
    image_files, hashes = inspect_images(ce, cloze, midia, reports)
    with tempfile.TemporaryDirectory(prefix='anki_visual_') as tmp:
        base = Path(tmp) / 'base.zip'
        candidate = Path(tmp) / 'visual.zip'
        export_text(ce,cloze,reports,base,deck=deck,profile=profile,exception_reason=exception_reason,balance_exception=balance_exception,max_cards=max_cards)
        with zipfile.ZipFile(base) as zi, zipfile.ZipFile(candidate, 'w', zipfile.ZIP_DEFLATED) as zo:
            for name in zi.namelist():
                if name == 'LEIA-ME.txt':
                    continue
                zo.writestr(name, zi.read(name))
            for name, path in sorted(image_files.items()):
                zo.write(path, f'midia/{name}')
            zo.writestr('LEIA-ME.txt',
              'Anki-Concursos Visual — imagens originais e fontes em relatorios/fontes_visuais.tsv.\n' +
              zi.read('LEIA-ME.txt').decode('utf-8') + '\n' +
              'Para TSV: extraia ZIP, copie apenas ARQUIVOS de midia/ para collection.media do seu perfil Anki (SEM subpastas), e importe os TSVs com Permitir HTML nos campos.\n'
              'Para APKG: importe o pacote APKG com mídia incorporada quando disponível.\n'
              'Não houve instalação automática na sua coleção nem validação jurídica automática.\n')
        with zipfile.ZipFile(candidate) as z:
            if z.testzip() is not None:
                raise ValueError('ZIP de mídia falhou CRC')
            if set(f'midia/{n}' for n in image_files) - set(z.namelist()):
                raise ValueError('ZIP visual não incluiu toda mídia')
        # Validador tradicional: integridade, tags, Cloze e proporção.
        validator = Path(__file__).resolve().parents[2]/'gerar-revisao-anki'/'scripts'/'validar_anki.py'
        import subprocess
        chk = subprocess.run([sys.executable,'-X','utf8',str(validator),str(candidate)]+policy_args,
            capture_output=True,encoding='utf-8')
        if chk.returncode:
            raise ValueError('Validação tradicional falhou: '+(chk.stdout+chk.stderr)[-1200:])
        with zipfile.ZipFile(candidate) as archive:
            has_calibration = 'relatorios/calibracao_cebraspe.json' in archive.namelist()
        if has_calibration:
            chk = subprocess.run([sys.executable,'-X','utf8',str(validator.with_name('validar_calibracao_cebraspe.py')),str(candidate)],
                capture_output=True,encoding='utf-8')
            if chk.returncode:
                raise ValueError('Calibração do ZIP visual reprovada: '+(chk.stdout+chk.stderr)[-1200:])
        check_recovery(validator, candidate)
        packages = []
        if apkg is not None:
            package_apkg = Path(tmp) / 'visual.apkg'
            with zipfile.ZipFile(candidate) as archive:
                package_ce = Path(archive.extract('anki_certo_errado.tsv', tmp))
                package_cloze = Path(archive.extract('anki_cloze.tsv', tmp))
                package_images = {
                    name: Path(archive.extract(f'midia/{name}', tmp)) for name in image_files
                }
            make_apkg(package_ce, package_cloze, package_apkg, deck, package_images)
            packages.append((package_apkg, apkg))
        packages.append((candidate, output))
        publish_packages(packages)
    return {'zip':str(output),'apkg':str(apkg) if apkg else None,
            'imagens':len(image_files),'sha256':hashes,'midia_verificada':True,
            'auditoria_de_licenca_manual':True}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ce',type=Path,required=True)
    ap.add_argument('--cloze',type=Path,required=True)
    ap.add_argument('--relatorios',type=Path,required=True)
    ap.add_argument('--midia',type=Path,required=True)
    ap.add_argument('-o','--saida',type=Path,required=True)
    ap.add_argument('--apkg',type=Path)
    ap.add_argument('--baralho',default='Anki-Concursos')
    add_validation_options(ap)
    a=ap.parse_args(argv)
    try:
        print(json.dumps(export(a.ce,a.cloze,a.relatorios,a.midia,a.saida,a.apkg,a.baralho,a.profile,a.exception_reason,a.balance_exception,a.max_cards),ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f'ERRO: {exc}',file=sys.stderr)
        return 1


if __name__=='__main__':
    sys.exit(main())
