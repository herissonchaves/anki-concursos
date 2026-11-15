"""Testes do lint heurístico sem substituir revisão humana."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

SCRIPT=Path(__file__).resolve().parents[1]/'scripts'/'auditar_clareza.py'
spec=importlib.util.spec_from_file_location('auditar_clareza',SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LintTest(unittest.TestCase):
    def test_cloze_text_normalization(self):
        self.assertIn('garantidor',module.folded('O pai é {{c1::garantidor}} da criança.'))

    def test_exposed_cloze_answers_have_distinct_gap_diagnostics(self):
        row = {
            'id': 'anki_cloze.tsv:1',
            'tipo': 'cloze',
            'front': 'Inércia e resultante. I → {{c1::inércia}} e R → {{c1::resultante}}.',
            'back': 'Extra sintético para testar os avisos de resposta exposta.',
            'tags': '',
        }
        details = [issue['detalhes'] for issue in module.scan([row])
                   if issue['sinal'] == 'RESPOSTA_CLOZE_VISIVEL']
        self.assertEqual(len(details), 2)
        self.assertIn('lacuna 1', details[0])
        self.assertIn('lacuna 2', details[1])

    def test_warning_on_absolute_and_meta(self):
        cards=[{'id':'anki_certo_errado.tsv:1','tipo':'desafiadora','front':'Segundo o material, todo espectador sempre responde por homicídio omissivo.','back':'❌ Errado<br><br>A posição de garantidor é especial.<br><br>💡 Memorize: Socorro não é garantia.','tags':''}]
        problems=module.scan(cards)
        self.assertTrue(any(x['sinal']=='ABSOLUTO_PISTA_POSSIVEL' for x in problems))
        self.assertTrue(any(x['sinal']=='REFERENCIA_EXTERNA' for x in problems))

    def test_zip_and_cross_modal_similarity(self):
        ce='A tentativa perfeita esgota os atos executórios.\t✅ Certo<br><br>Todos os atos são executados.<br><br>💡 Memorize: execução completa.\tTipo_Revisao_Rapida\n'
        cl='A tentativa {{c1::perfeita}} esgota os atos executórios.\tExecução concluída.<br><br>💡 Memorize: atuação completa.\tTema_Penal\n'
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'batch.zip'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('anki_certo_errado.tsv',ce)
                z.writestr('anki_cloze.tsv',cl)
            cards=module.load_cards(p)
            self.assertEqual(len(cards),2)
            self.assertTrue(any(x['sinal']=='SEMELHANCA_LEXICAL' for x in module.scan(cards)))

    def test_report_header_and_count(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'report.tsv'
            module.save_report([],p)
            self.assertIn('decisao_humana',p.read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()

