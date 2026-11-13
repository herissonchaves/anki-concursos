#!/usr/bin/env python3
"""Extract page-level PDF text for subsequent HUMAN/AI pedagogical selection.

Do not assert scanned PDF pages were read; no OCR is performed. Image/layout
inspection remains necessary for formulas, tables, charts and scanned pages.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys


def extract(pdf: Path, minimum_chars=40):
    pdf = Path(pdf)
    if not pdf.is_file() or pdf.suffix.lower() != '.pdf':
        raise ValueError('Informe um PDF existente')
    pages=[]
    try:
        import fitz
    except ImportError:
        fitz=None
    if fitz is not None:
        engine='PyMuPDF'
        with fitz.open(pdf) as doc:
            if doc.needs_pass:
                raise ValueError('PDF protegido por senha')
            total=len(doc)
            for idx,page in enumerate(doc):
                content=page.get_text('text',sort=True).strip()
                pages.append(_row(idx+1,content,minimum_chars))
    else:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError('Instale pymupdf ou pypdf para extrair PDFs') from exc
        engine='pypdf'
        reader=PdfReader(str(pdf))
        total=len(reader.pages)
        for idx,page in enumerate(reader.pages):
            content=(page.extract_text() or '').strip()
            pages.append(_row(idx+1,content,minimum_chars))
    return {
        'arquivo':pdf.name, 'motor':engine,'total_paginas':total,
        'paginas_com_alerta':[p['pagina'] for p in pages if p['revisao_visual_obrigatoria']],
        'aviso':'Texto extraído automaticamente. Diagramas, imagens, fórmulas e tabelas devem ser verificados visualmente; páginas com pouco texto podem ser escaneadas. Não executou OCR.',
        'paginas':pages
    }


def _row(n,text,minimum_chars):
    return {'pagina':n,'caracteres':len(text),'revisao_visual_obrigatoria':len(text)<minimum_chars,'texto':text}


def main(argv=None):
    p=argparse.ArgumentParser(description='Extrair PDF em JSON por página sem OCR')
    p.add_argument('pdf',type=Path)
    p.add_argument('-o','--saida',type=Path,required=True)
    p.add_argument('--min-chars',type=int,default=40)
    a=p.parse_args(argv)
    result=extract(a.pdf,a.min_chars)
    a.saida.parent.mkdir(parents=True,exist_ok=True)
    a.saida.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'paginas':result['total_paginas'],'alertas_visuais':result['paginas_com_alerta'],'saida':str(a.saida)},ensure_ascii=False))
    return 0

if __name__=='__main__':
    try: sys.exit(main())
    except Exception as exc: print(f'ERRO: {exc}',file=sys.stderr);sys.exit(1)

