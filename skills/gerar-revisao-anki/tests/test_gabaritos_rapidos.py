"""Testes da distribuição 50% Certo / 50% Errado para Teste::Sintetico::Topico Rapida."""
from pathlib import Path
import importlib.util
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'validar_gabaritos_rapidos.py'
SPEC = importlib.util.spec_from_file_location('quick_balance', SCRIPT)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def linha(rapido: bool, certo: bool, indice: int) -> str:
    tag = 'Teste::Sintetico::Topico Rapida' if rapido else 'Teste::Sintetico::Topico Desafiadora ceb-2024-fixture-001'
    gabarito = '✅ Certo' if certo else '❌ Errado'
    return f'Proposição nova e verificável número {indice}.\t{gabarito}<br><br>Fundamento verificável.<br><br>💡 Memorize: conceito.\t{tag}\n'


class QuickBalanceTests(unittest.TestCase):
    def contar(self, gs_rapidos, gs_desafiadores=()):
        data = ''.join(linha(True, a, i) for i, a in enumerate(gs_rapidos))
        data += ''.join(linha(False, a, i + 100) for i, a in enumerate(gs_desafiadores))
        return module.contar_rapidos(data.encode('utf-8'), strict_balance=True)

    def test_exact_5_and_5(self):
        r, e = self.contar([True] * 5 + [False] * 5, [True] * 50)
        self.assertEqual((r['certos'], r['errados'], r['rapidos']), (5, 5, 10))
        self.assertEqual((r['percentual_certos'], r['percentual_errados']), (50.0, 50.0))
        self.assertFalse(r['excecao_impar'])
        self.assertFalse(e)

    def test_even_unbalanced_rejected(self):
        _, e = self.contar([True] * 7 + [False] * 3)
        self.assertTrue(any('Distribuição incorreta' in s for s in e), e)

    def test_odd_one_difference_accepted(self):
        r, e = self.contar([True] * 3 + [False] * 2)
        self.assertEqual(r['rapidos'], 5)
        self.assertTrue(r['excecao_impar'])
        self.assertFalse(e)

    def test_odd_three_difference_rejected(self):
        _, e = self.contar([True] * 4 + [False])
        self.assertTrue(e)

    def test_no_rapid_cards(self):
        r, e = self.contar([], [False] * 8)
        self.assertEqual(r['rapidos'], 0)
        self.assertFalse(e)

    def test_wrong_answer_prefix_rejected(self):
        raw = 'Uma proposição.\tErrado: exemplo.\tTeste::Sintetico::Topico Rapida\n'
        _, e = module.contar_rapidos(raw.encode())
        self.assertTrue(any('sem gabarito' in s for s in e), e)

    def test_text_in_head_does_not_count_as_gabarito(self):
        raw = '✅ Certo é uma expressão textual aqui.\t❌ Errado<br><br>Motivo.\tTeste::Sintetico::Topico Rapida\n'
        r, e = module.contar_rapidos(raw.encode())
        self.assertEqual((r['certos'], r['errados']), (0, 1))
        self.assertFalse(e)

    def test_mixed_tags_rejected(self):
        raw = 'Frase.\t✅ Certo<br><br>Motivo.\tRapida Desafiadora\n'
        _, e = module.contar_rapidos(raw.encode())
        self.assertTrue(any('contraditórias' in s for s in e), e)


if __name__ == '__main__':
    unittest.main()
