"""End-to-end export and validator policy regressions; synthetic test data only."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'automacao-anki-python/scripts'))
from calibration_fixture import write_calibration
from recovery_fixture import write_review
from exportar_anki import export
from exportar_anki_visual import export as export_visual, COLS

class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.ce=self.root/'ce.tsv'; self.cl=self.root/'cl.tsv'
        self.reports=self.root/'reports'; self.reports.mkdir(); self.out=self.root/'out.zip'
        for name in ['selecao_e_fontes.txt','economia_de_revisao.txt','auditoria_pedagogica.txt']:
            (self.reports/name).write_text('Fixture sintética: somente teste estrutural, não conteúdo aprovado.',encoding='utf-8')
        self.cl.write_text('',encoding='utf-8')
    def rows(self, quick, hard=0):
        lines=[]
        for i,good in enumerate(quick):
            lines.append(f'Proposição sintética {i}.\t'+('✅ Certo' if good else '❌ Errado')+'<br><br>Motivo sintético. 💡 Memorize: resumo sintético.\tTipo_Revisao_Rapida')
        for i in range(hard):
            lines.append(f'Aplicação sintética {i}.\t'+('✅ Certo' if i % 2 == 0 else '❌ Errado')+'<br><br>Motivo sintético. 💡 Memorize: resumo sintético.\tTipo_Desafiadora_Cebraspe Estilo_Cebraspe')
        self.ce.write_text('\n'.join(lines)+ ('\n' if lines else ''),encoding='utf-8')
        write_calibration(self.ce,self.reports)
    def run_export(self,**kw):
        write_review(self.ce,self.cl,self.reports)
        return export(self.ce,self.cl,self.reports,self.out,**kw)
    def test_mixed_balanced(self):
        self.rows([True,False],2); self.run_export(max_cards=4)
    def test_mixed_unbalanced_rejected(self):
        self.rows([True,True],2)
        with self.assertRaisesRegex(ValueError,'Distribuição incorreta'): self.run_export()
    def test_single_quick_requires_explicit_focus(self):
        self.rows([True])
        with self.assertRaises(ValueError): self.run_export()
        with self.assertRaises(ValueError): self.run_export(profile='focused')
        with self.assertRaisesRegex(ValueError,'50%'):
            self.run_export(profile='focused',exception_reason='Usuário pediu um cartão',max_cards=1)
        self.rows([True,False])
        self.run_export(profile='focused',exception_reason='Par útil de rápidos',max_cards=2)
        with zipfile.ZipFile(self.out) as z:
            policy=json.loads(z.read('relatorios/politica_validacao.json'))
            self.assertEqual(policy['profile'],'focused')
            self.assertEqual(policy['max_cards'],2)
    def test_cloze_and_challenges_real_card_count(self):
        self.rows([], 2)
        self.cl.write_text('Alfa {{c1::beta}} e {{c1::gama}}.\tConceitos beta e gama. 💡 Memorize: resumo sintético.\tTeste Mnemonico\n',
                           encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Teto'):
            self.run_export(profile='focused', exception_reason='Cloze com desafiadores', max_cards=2)
        self.run_export(profile='focused', exception_reason='Cloze com desafiadores', max_cards=3)
    def test_focused_still_rejects_syntax(self):
        self.rows([]); self.cl.write_text('Alfa {{c1::}}.\tFixture.\tTeste\n',encoding='utf-8')
        with self.assertRaises(ValueError): self.run_export(profile='focused',exception_reason='Somente Cloze')
    def test_balance_exception_is_separate(self):
        self.rows([True,True])
        with self.assertRaisesRegex(ValueError,'Distribuição incorreta'): self.run_export(profile='focused',exception_reason='Somente rápidos')
        with self.assertRaisesRegex(ValueError,'não é permitido'):
            self.run_export(profile='focused',exception_reason='Somente rápidos',balance_exception='Pedido explícito de duas afirmações corretas')
    def test_empty_rejected(self):
        self.rows([])
        with self.assertRaises(ValueError): self.run_export(profile='focused',exception_reason='Um cartão')
    def test_focused_hard_only(self):
        self.rows([],2); self.run_export(profile='focused',exception_reason='Par de desafios')
    def test_odd_balance(self):
        self.rows([True,False,True],3)
        with self.assertRaisesRegex(ValueError,'50%'): self.run_export()
    def test_old_collection_not_rebalanced(self):
        self.rows([True,True])
        with zipfile.ZipFile(self.out,'w') as archive:
            archive.writestr('anki_certo_errado.tsv',self.ce.read_bytes())
            archive.writestr('anki_cloze.tsv',b'')
            archive.writestr('LEIA-ME.txt','Fixture legada; não importar no Anki.')
            for name in ('selecao_e_fontes.txt','economia_de_revisao.txt','auditoria_pedagogica.txt'):
                archive.writestr('relatorios/'+name,'Fixture legada; sem exportação de notas novas.')
        validator=ROOT/'gerar-revisao-anki/scripts/validar_anki.py'
        result=subprocess.run([sys.executable,'-X','utf8',str(validator),str(self.out)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_visual_focused_and_limit(self):
        self.rows([True,False]); self.ce.write_text(self.ce.read_text(encoding='utf-8').replace('Proposição','<img src="test.png"> Proposição'),encoding='utf-8')
        media=self.root/'media';media.mkdir()
        import base64
        (media/'test.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aRZkAAAAASUVORK5CYII='))
        vals=['test.png','1','https://example.org/test','https://example.org/test.png','Fixture','CC0 fixture','2026-11-03','Somente teste','aprovada']
        (self.reports/'fontes_visuais.tsv').write_text('\t'.join(COLS)+'\n'+'\t'.join(vals)+'\n',encoding='utf-8')
        with self.assertRaises(ValueError): export_visual(self.ce,self.cl,self.reports,media,self.out,profile='focused',exception_reason='Um visual',max_cards=0)
        write_review(self.ce,self.cl,self.reports)
        export_visual(self.ce,self.cl,self.reports,media,self.out,profile='focused',exception_reason='Par de visuais',max_cards=2)
        with zipfile.ZipFile(self.out) as z: self.assertIn('midia/test.png',z.namelist())

if __name__=='__main__': unittest.main()
