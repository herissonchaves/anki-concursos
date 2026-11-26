"""Teste de regressão da nova política de modalidades e de ausência de teto 30."""
from pathlib import Path
import importlib.util
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'validar_anki.py'
SPEC = importlib.util.spec_from_file_location('validador_anki_15', SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def ce(index, kind):
    front = f'A afirmação sobre o conceito administrativo {index} é precisa.'
    back = '✅ Certo<br><br>O conceito foi corretamente descrito.<br><br>💡 Memorize: verificar o fundamento.'
    tag = 'Teste::Sintetico::Topico Rapida' if kind == 'R' else 'Teste::Sintetico::Topico Desafiadora ceb-2024-fixture-001'
    return f'{front}\t{back}\tAdministrativo {tag}\n'


class TypeDistributionTests(unittest.TestCase):
    def test_more_than_thirty_without_old_cap(self):
        rows = ''.join(ce(i, 'D' if i < 40 else 'R') for i in range(80))
        errors = []
        self.assertEqual(validator.verify_tsvo('anki_certo_errado.tsv', rows.encode(), errors), 80)
        self.assertEqual(validator.validate_type_distribution(rows.encode(), errors, True)['desafiadores'], 40)
        self.assertEqual(errors, [])

    def test_more_rapid_than_challenging_is_allowed(self):
        rows = ''.join(ce(i, 'R' if i < 3 else 'D') for i in range(5))
        errors = []
        validator.validate_type_distribution(rows.encode(), errors, True, require_ratio=True)
        self.assertEqual(errors, [])

    def test_missing_tags_new_and_legacy_compatibility(self):
        rows = ce(1, 'D').replace('Teste::Sintetico::Topico Desafiadora ceb-2024-fixture-001', '').replace('Estilo_Cebraspe', '')
        legacy, new = [], []
        validator.validate_type_distribution(rows.encode(), legacy)
        validator.validate_type_distribution(rows.encode(), new, True)
        self.assertFalse(legacy)
        self.assertTrue(any('sem tag' in e for e in new), new)

    def test_dual_tag_rejected(self):
        rows = ce(1, 'D').replace('Teste::Sintetico::Topico Desafiadora ceb-2024-fixture-001', 'Teste::Sintetico::Topico Desafiadora Teste::Sintetico::Topico Rapida')
        errors = []
        validator.validate_type_distribution(rows.encode(), errors, True)
        self.assertTrue(any('simultaneamente' in e for e in errors), errors)

    def test_cloze_not_counted_for_ratio(self):
        rows = ce(1, 'D') + ce(2, 'R')
        errors=[]
        result=validator.validate_type_distribution(rows.encode(), errors, True)
        self.assertEqual((result['rapidos'],result['desafiadores']),(1,1))
        self.assertFalse(errors)

if __name__ == '__main__': unittest.main()


