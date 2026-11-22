#!/usr/bin/env python3
"""Validate already audited Anki TSVs and package them. Never generate content.

Requires existing pedagogical audit reports; does not manufacture them or claim
quality merely because tests pass. Optional .apkg depends on genanki.
"""
from __future__ import annotations
import argparse
from contextlib import ExitStack
import csv
import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

REQUIRED_REPORTS=('selecao_e_fontes.txt','economia_de_revisao.txt','auditoria_pedagogica.txt')


def tsv_rows(path):
    with Path(path).open('r',encoding='utf-8-sig',newline='') as source:
        for n,line in enumerate(csv.reader(source,delimiter='\t',quoting=csv.QUOTE_NONE),1):
            if not line: continue
            if len(line)!=3:
                raise ValueError(f'{path.name}, linha {n}: esperados 3 campos')
            if n==1 and line[0].strip().lower() in ('frente','texto'):
                continue
            yield line


def deck_id(deck_name):
    if deck_name == 'Anki-Concursos':
        return 1987052180  # Preserve legacy default deck identity.
    return 1_000_000_000 + int.from_bytes(hashlib.sha256(('anki-concursos:deck:'+deck_name).encode('utf-8')).digest()[:4], 'big')


def modelos(genanki):
    """Tipos de nota C/E e Cloze com o CSS padrão (estilo_anki.py); IDs fixos para não duplicar tipos."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'gerar-revisao-anki' / 'scripts'))
    from estilo_anki import CSS_BASE, CSS_CLOZE, MODELO_CE, MODELO_CLOZE  # padrão único de formatação
    basic=genanki.Model(MODELO_CE[0],MODELO_CE[1],fields=[{'name':'Frente'},{'name':'Verso'}],
           templates=[{'name':'C/E','qfmt':'{{Frente}}','afmt':'{{FrontSide}}<hr id="answer">{{Verso}}'}],css=CSS_BASE)
    clz=genanki.Model(MODELO_CLOZE[0],MODELO_CLOZE[1],fields=[{'name':'Texto'},{'name':'Extra'}],
           templates=[{'name':'Cloze','qfmt':'{{cloze:Texto}}','afmt':'{{cloze:Texto}}<hr id="answer">{{Extra}}'}],
           model_type=genanki.Model.CLOZE,css=CSS_CLOZE)
    return basic,clz


def check_coverage(validator, target):
    """Lote de PDF (com relatorios/cobertura_pdf.json): exige a cobertura por prioridade (Alta e Média); demais lotes passam."""
    target = Path(target)
    if target.is_dir():
        present = (target/'relatorios'/'cobertura_pdf.json').is_file()
    else:
        with zipfile.ZipFile(target) as z:
            present = 'relatorios/cobertura_pdf.json' in z.namelist()
    if not present:
        return
    coverage = validator.with_name('validar_cobertura_pdf.py')
    if not coverage.is_file():
        raise RuntimeError('Verificador de cobertura do PDF indisponível')
    result = subprocess.run([sys.executable,'-X','utf8',str(coverage),str(target)],capture_output=True,encoding='utf-8')
    if result.returncode:
        raise ValueError('Cobertura do PDF reprovada: '+(result.stdout+result.stderr)[-1400:])


def generate_apkg(ce,cloze,out,deck_name):
    try:import genanki
    except ImportError as e:
        raise RuntimeError('Exportação .apkg indisponível: instale genanki; ZIP/TSV não exigem essa biblioteca') from e
    basic,clz=modelos(genanki)
    deck=genanki.Deck(deck_id(deck_name),deck_name)
    for front,back,tags in tsv_rows(ce):
        deck.add_note(genanki.Note(model=basic,fields=[front,back],tags=tags.split(),guid=genanki.guid_for(front,'C/E')))
    for text,extra,tags in tsv_rows(cloze):
        deck.add_note(genanki.Note(model=clz,fields=[text,extra],tags=tags.split(),guid=genanki.guid_for(text,'Cloze')))
    genanki.Package(deck).write_to_file(str(out))
    with zipfile.ZipFile(out) as z:
        if z.testzip() is not None:raise ValueError('Falha de integridade .apkg')


def validation_args(profile='mixed', exception_reason='', balance_exception='', max_cards=None):
    if profile not in {'mixed', 'focused'}:
        raise ValueError('Perfil desconhecido')
    if profile == 'focused' and not exception_reason.strip():
        raise ValueError('Perfil focado requer justificativa')
    if profile == 'mixed' and exception_reason.strip():
        raise ValueError('Justificativa de perfil exige focused')
    if balance_exception.strip():
        raise ValueError('Lotes novos exigem 50/50 por modo; --balance-exception não é permitido')
    args = ['--new', '--profile', profile]
    if exception_reason.strip(): args += ['--exception-reason', exception_reason.strip()]
    if max_cards is not None: args += ['--max-cards', str(max_cards)]
    return args


def add_validation_options(parser):
    parser.add_argument('--profile', choices=('mixed', 'focused'), default='mixed')
    parser.add_argument('--exception-reason', default='')
    parser.add_argument('--balance-exception', default='', help=argparse.SUPPRESS)
    parser.add_argument('--max-cards', type=int)


def check_recovery(validator, package):
    review = validator.with_name('validar_revisao_pedagogica.py')
    if not review.is_file():
        raise RuntimeError('Verificador de revisão de recuperação indisponível: exportação bloqueada')
    result = subprocess.run([sys.executable, '-X', 'utf8', str(review), str(package)],
                            capture_output=True, encoding='utf-8')
    if result.returncode:
        raise ValueError('Revisão de recuperação reprovada: '+(result.stdout+result.stderr)[-4000:])


def validate_package_paths(output: Path, apkg: Path | None):
    if output.suffix.lower() != '.zip':
        raise ValueError('Saída deve ser .zip')
    if apkg is not None and apkg.suffix.lower() != '.apkg':
        raise ValueError('Exportação Anki deve terminar com .apkg')
    for destination in (output, apkg):
        if destination is not None and destination.is_dir():
            raise ValueError(f'O destino da exportação é um diretório: {destination}')


def publish_packages(packages: list[tuple[Path, Path]]):
    with ExitStack() as stack:
        staged = []
        for source, destination in packages:
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Stage on the destination filesystem so replacement is atomic per file.
            folder = Path(stack.enter_context(tempfile.TemporaryDirectory(
                prefix='.anki_export_', dir=destination.parent)))
            candidate = folder / destination.name
            shutil.copy2(source, candidate)
            staged.append((candidate, destination))
        for candidate, destination in staged:
            candidate.replace(destination)


def export(ce,cloze,reports_dir,output,apkg=None,deck='Anki-Concursos',profile='mixed',exception_reason='',balance_exception='',max_cards=None):
    policy_args=validation_args(profile,exception_reason,balance_exception,max_cards)
    ce,cloze,reports_dir,output=map(Path,(ce,cloze,reports_dir,output))
    apkg = Path(apkg) if apkg else None
    validate_package_paths(output, apkg)
    if not ce.is_file() or not cloze.is_file():raise ValueError('Ambos TSVs são obrigatórios, mesmo quando um formato estiver vazio')
    if not reports_dir.is_dir():raise ValueError('Diretório de relatórios de auditoria não encontrado')
    for name in REQUIRED_REPORTS:
        if not (reports_dir/name).is_file() or (reports_dir/name).stat().st_size==0:
            raise ValueError(f'Relatório obrigatório ausente ou vazio: {name}; não fabricar auditoria')
    if (reports_dir/'triagem_previa_pdf.txt').is_file() and (reports_dir/'triagem_previa_pdf.txt').stat().st_size==0:
        raise ValueError('Triagem de PDF vazia')
    validator=Path(__file__).resolve().parents[2]/'gerar-revisao-anki'/'scripts'/'validar_anki.py'
    if not validator.is_file():
        raise RuntimeError('Validador central validar_anki.py indisponível: exportação bloqueada')
    with tempfile.TemporaryDirectory(prefix='anki_export_') as tmp:
        root=Path(tmp)
        package_ce = root / 'anki_certo_errado.tsv'
        package_cloze = root / 'anki_cloze.tsv'
        shutil.copy2(ce, package_ce)
        shutil.copy2(cloze, package_cloze)
        (root/'relatorios').mkdir()
        for src in reports_dir.iterdir():
            if not src.is_file() or (src.suffix not in {'.txt', '.tsv'} and src.name not in {'calibracao_cebraspe.json', 'revisao_recuperacao.json', 'cobertura_pdf.json'}):
                continue
            shutil.copy2(src,root/'relatorios'/src.name)
        (root/'LEIA-ME.txt').write_text('Anki-Concursos - extraia o ZIP. Importe C/E como Básico sem cartão inverso e Cloze como Cloze. Mapeie colunas 1/2 aos campos e 3 a Tags; separador TAB, UTF-8 e HTML permitido. Ignore TSV vazio. Confira a prévia e as opções de duplicatas antes de importar.\nUse APKG OU TSV, não ambos. Alterar frente pode gerar nova nota; não há garantia de preservar histórico em reimportações. Faça backup antes de substituir notas existentes.\nO ZIP é tecnicamente validado, mas não certifica exatidão pedagógica nem importação no aplicativo.\n',encoding='utf-8')
        check=subprocess.run([sys.executable,'-X','utf8',str(validator),str(root)]+policy_args,capture_output=True,encoding='utf-8')
        if check.returncode!=0:
            raise ValueError('Validador central REPROVOU a exportação: '+(check.stderr or check.stdout)[-1400:])
        # Este exportador sempre valida notas novas (--new). D novos exigem
        # calibração; a leitura de coleções antigas usa os fluxos de análise.
        calibration = validator.with_name('validar_calibracao_cebraspe.py')
        has_calibration = (root/'relatorios'/'calibracao_cebraspe.json').is_file()
        has_hard = any({'Desafiadora', 'Tipo_Desafiadora_Cebraspe'} & set(row[2].split()) for row in tsv_rows(package_ce))
        check_calibration = has_hard or has_calibration
        if check_calibration:
            if not calibration.is_file():
                raise RuntimeError('Verificador de calibração indisponível')
            result = subprocess.run([sys.executable,'-X','utf8',str(calibration),str(root)],capture_output=True,encoding='utf-8')
            if result.returncode:
                raise ValueError('Registro de calibração reprovado: '+(result.stdout+result.stderr)[-1400:])
        check_recovery(validator, root)
        check_coverage(validator, root)
        (root/'relatorios'/'politica_validacao.json').write_text(json.dumps({'profile':profile,'exception_reason':exception_reason,'balance_exception':balance_exception,'max_cards':max_cards},ensure_ascii=False,indent=2),encoding='utf-8')
        # Add no raw .colpkg, sources, notebooks, scan images or personal data.
        tmpzip=root/'package.zip'
        with zipfile.ZipFile(tmpzip,'w',zipfile.ZIP_DEFLATED) as zout:
            for candidate in sorted(root.rglob('*')):
                if candidate.is_file() and candidate!=tmpzip:
                    zout.write(candidate,candidate.relative_to(root).as_posix())
        with zipfile.ZipFile(tmpzip) as z:
            if z.testzip() is not None:raise ValueError('Erro CRC no ZIP')
        # Zip output must also pass original validation.
        check=subprocess.run([sys.executable,'-X','utf8',str(validator),str(tmpzip)]+policy_args,capture_output=True,encoding='utf-8')
        if check.returncode!=0:
            raise ValueError('ZIP reprovado pelo validador: '+(check.stderr or check.stdout)[-1400:])
        if check_calibration:
            result = subprocess.run([sys.executable,'-X','utf8',str(calibration),str(tmpzip)],capture_output=True,encoding='utf-8')
            if result.returncode:
                raise ValueError('Registro de calibração do ZIP reprovado: '+(result.stdout+result.stderr)[-1400:])
        check_recovery(validator, tmpzip)
        check_coverage(validator, tmpzip)
        ce_count = sum(1 for _ in tsv_rows(package_ce))
        cloze_count = sum(1 for _ in tsv_rows(package_cloze))
        packages = []
        if apkg is not None:
            package_apkg = root / 'package.apkg'
            generate_apkg(package_ce, package_cloze, package_apkg, deck)
            packages.append((package_apkg, apkg))
        packages.append((tmpzip, output))
        publish_packages(packages)
    return {'zip':str(output),'ce':ce_count,'cloze':cloze_count,'apkg':str(apkg) if apkg else None,'validador_executado':True}


def main(argv=None):
    p=argparse.ArgumentParser(description='Validar e exportar ZIP e opcional .apkg sem alterar coleção existente')
    p.add_argument('--ce',type=Path,required=True)
    p.add_argument('--cloze',type=Path,required=True)
    p.add_argument('--relatorios',type=Path,required=True)
    p.add_argument('-o','--saida',type=Path,required=True)
    p.add_argument('--apkg',type=Path)
    p.add_argument('--baralho',default='Anki-Concursos')
    add_validation_options(p)
    a=p.parse_args(argv)
    print(json.dumps(export(a.ce,a.cloze,a.relatorios,a.saida,a.apkg,a.baralho,a.profile,a.exception_reason,a.balance_exception,a.max_cards),ensure_ascii=False))
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:print(f'ERRO: {exc}',file=sys.stderr);sys.exit(1)
