"""Integração real das barreiras documentais; dados fictícios, não pedagógicos."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'automacao-anki-python/scripts'))
import exportar_anki
from calibration_fixture import write_calibration
from recovery_fixture import write_review


class ExportCalibrationRequiredTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.ce=self.root/'ce.tsv'; self.cl=self.root/'cl.tsv'
        self.reports=self.root/'reports'; self.reports.mkdir()
        self.out=self.root/'out.zip'
        self.ce.write_text('Condição sintética A.\t✅ Certo<br><br>Fundamento sintético A. 💡 Memorize: resumo sintético.\tTeste::Sintetico::Topico Desafiadora ceb-2024-fixture-001\nCondição sintética B.\t❌ Errado<br><br>Correção sintética B. 💡 Memorize: resumo sintético.\tTeste::Sintetico::Topico Desafiadora ceb-2024-fixture-001\n',encoding='utf-8')
        self.cl.write_text('',encoding='utf-8')
        for name in exportar_anki.REQUIRED_REPORTS:
            (self.reports/name).write_text('Fixture de teste, sem auditoria real de conteúdo.',encoding='utf-8')
        write_calibration(self.ce,self.reports)

    def export(self):
        write_review(self.ce,self.cl,self.reports)
        return exportar_anki.export(self.ce,self.cl,self.reports,self.out,profile='focused',exception_reason='Teste de calibração obrigatória')

    def test_missing_record_blocks_new_hard(self):
        (self.reports/'calibracao_cebraspe.json').unlink()
        before=self.ce.read_bytes()
        with self.assertRaisesRegex(ValueError,'calibração'): self.export()
        self.assertFalse(self.out.exists())
        self.assertEqual(self.ce.read_bytes(),before)

    def test_missing_or_failed_language_blocks_export(self):
        target=self.reports/'calibracao_cebraspe.json'
        original=json.loads(target.read_text(encoding='utf-8'))
        for status in (None,'FALHA','PENDENTE'):
            data=json.loads(json.dumps(original))
            if status is None:
                del data['cartoes'][0]['rubrica']['linguagem_didatica']
            else:
                data['cartoes'][0]['rubrica']['linguagem_didatica']['resultado']=status
            target.write_text(json.dumps(data),encoding='utf-8')
            with self.subTest(status=status):
                with self.assertRaisesRegex(ValueError,'linguagem_didatica'): self.export()
                self.assertFalse(self.out.exists())

    def test_empty_language_evidence_blocks_export(self):
        target=self.reports/'calibracao_cebraspe.json'
        data=json.loads(target.read_text(encoding='utf-8'))
        data['cartoes'][0]['rubrica']['linguagem_didatica']['evidencia']=' '
        target.write_text(json.dumps(data),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'linguagem_didatica'): self.export()

    def test_record_checked_in_directory_and_final_zip(self):
        original=exportar_anki.subprocess.run
        with patch.object(exportar_anki.subprocess,'run',wraps=original) as run:
            self.export()
        calls=[call.args[0] for call in run.call_args_list if any(str(x).endswith('validar_calibracao_cebraspe.py') for x in call.args[0])]
        self.assertEqual(len(calls),2)
        self.assertTrue(Path(calls[1][-1]).suffix=='.zip')
        self.assertTrue(self.out.is_file())

    def test_quick_only_needs_no_hard_record(self):
        text=self.ce.read_text(encoding='utf-8').replace('Teste::Sintetico::Topico Desafiadora ceb-2024-fixture-001','Teste::Sintetico::Topico Rapida')
        self.ce.write_text(text,encoding='utf-8')
        (self.reports/'calibracao_cebraspe.json').unlink()
        self.export()
        self.assertTrue(self.out.is_file())


if __name__=='__main__': unittest.main()
