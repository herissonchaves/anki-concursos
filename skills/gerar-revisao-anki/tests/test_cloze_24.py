"""Regression of format choice plumbing; not semantic certification."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile
from calibration_fixture import write_calibration
from recovery_fixture import write_review

ROOT = Path(__file__).resolve().parents[2]
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
exporter = module('export24', ROOT/'automacao-anki-python/scripts/exportar_anki.py')
validator = module('validate24', ROOT/'gerar-revisao-anki/scripts/validar_anki.py')

class ClozePolicyTests(unittest.TestCase):
    def test_lists_and_multiple_views_count(self):
        for text, expected in [
            ('Estados clássicos: {{c1::sólido, líquido e gasoso}}.', 1),
            ('Estados clássicos: {{c1::sólido}}, {{c1::líquido}}, {{c1::gasoso}}.', 1),
            ('{{c1::massa}} / {{c2::volume}}', 2),
        ]:
            errors = []
            result = validator.count_cloze_cards((text+'\tContexto.\tTeste::Sintetico::Topico Cloze\n').encode(), errors)
            self.assertEqual(result['cartoes_cloze'], expected)
            self.assertEqual(errors, [])

    def test_export_without_cloze_and_existing_guards(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            ce, cl, reports = p/'ce.tsv', p/'cl.tsv', p/'reports'
            reports.mkdir()
            for name in exporter.REQUIRED_REPORTS:
                (reports/name).write_text('Synthetic structural test fixture; no pedagogical approval.', encoding='utf8')
            cl.write_text('', encoding='utf8')
            quick='A unidade SI de força é o newton.\t✅ Certo<br><br>Newton mede força. 💡 Memorize: resumo sintético.\tTeste::Sintetico::Topico Rapida\n'
            hard='Uma força resultante de 6 N sobre 2 kg produz 3 m/s².\t✅ Certo<br><br>A aceleração é 6 dividido por 2. 💡 Memorize: resumo sintético.\tTeste::Sintetico::Topico Desafiadora\n'
            quick_false='Na física clássica, o newton é unidade SI de massa.\t❌ Errado<br><br>A unidade SI de massa é o quilograma; newton mede força. 💡 Memorize: resumo sintético.\tTeste::Sintetico::Topico Rapida\n'
            hard_false='Uma força resultante de 6 N sobre 2 kg produz 12 m/s².\t❌ Errado<br><br>Pela segunda lei de Newton, a aceleração é 6 dividido por 2, ou 3 m/s². 💡 Memorize: resumo sintético.\tTeste::Sintetico::Topico Desafiadora\n'
            balanced = quick + quick_false + hard + hard_false
            ce.write_text(balanced, encoding='utf8')
            write_calibration(ce,reports)
            write_review(ce,cl,reports)
            exporter.export(ce,cl,reports,p/'valid.zip')
            with zipfile.ZipFile(p/'valid.zip') as z:
                self.assertEqual(z.read('anki_cloze.tsv'),b'')
            ce.write_text(quick,encoding='utf8')
            with self.assertRaises(ValueError):
                exporter.export(ce,cl,reports,p/'invalid.zip')
            ce.write_text(balanced,encoding='utf8')
            cl.write_text('Unidade: {{c1::}}.\tContexto.\tTeste::Sintetico::Topico Cloze\n',encoding='utf8')
            with self.assertRaises(ValueError):
                exporter.export(ce,cl,reports,p/'malformed.zip')

if __name__ == '__main__':
    unittest.main()
