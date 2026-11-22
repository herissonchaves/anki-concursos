"""Testes documentais com fontes FICTÍCIAS; não constituem lote pedagógico."""
import copy
from recovery_fixture import write_review
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check = load(ROOT / 'scripts/validar_calibracao_cebraspe.py', 'calibracao')


def fixture():
    row = ['Considere P implica Q e Q falso. Nessas condições, P é falso.',
           '✅ Certo<br><br>Se P fosse verdadeiro, Q teria de ser verdadeiro. Isso contradiz a premissa de Q falso. 💡 Memorize: resumo sintético.',
           'Teste::Sintetico::Topico Desafiadora ref-2021-teste-001']
    ref = dict(id='ref-2021-teste-001', concurso='FICTICIO', cargo='Teste', ano=2021,
               caderno='Fixture', item='1', url='https://example.test/prova',
               consulta='2026-11-03', operacao_observada='Contraposição sintética',
               gabarito_status='definitivo', gabarito_url='https://example.test/gabarito')
    record = dict(id='D01', linha=1, sha256=check.fingerprint(row), gabarito='C',
                  alvo='Inferência condicional', operacao_autoral='Aplicar modus tollens',
                  regra='P implica Q', dado_decisivo='Q falso', solucao='P verdadeiro contradiz Q falso.',
                  erro_plausivel='Tomar Q falso como insuficiente para excluir P.',
                  leitura_concorrente='A hipótese P verdadeiro contradiz as premissas.',
                  originalidade='Formulação simbólica sintética exclusiva do teste.',
                  fontes_conteudo=['https://example.test/logica'], referencias=['ref-2021-teste-001'],
                  fidelidade='comparada', comparacao='Mesma operação formal na fixture.',
                  segunda_conferencia=True, decisao='APROVAR',
                  rubrica={key: dict(resultado='PASSA', evidencia=f'Evidência sintética de {key}') for key in check.CRITERIA})
    return row, dict(schema_version=1, referencias=[ref], cartoes=[record])


def fixture_v2():
    """Schema 2: referência Cebraspe C/E e questão de outra banca, ambas fictícias."""
    row, data = fixture()
    data['schema_version'] = 2
    data['referencias'][0].update(banca='Cebraspe', formato='certo_errado')
    data['referencias'].append(dict(
        id='REF-FGV', concurso='FICTICIO 2', cargo='Teste', ano=2022, caderno='Fixture B', item='7',
        url='https://example.test/prova-fgv', consulta='2026-11-03',
        operacao_observada='Múltipla escolha sintética sobre contraposição', banca='FGV',
        formato='multipla_escolha', gabarito_status='definitivo', gabarito_url='https://example.test/gab-fgv'))
    data['cartoes'][0]['referencias'] = ['ref-2021-teste-001', 'REF-FGV']
    row[2] += ' REF-FGV'  # 2.31: questões de origem viram tags do D
    data['cartoes'][0]['sha256'] = check.fingerprint(row)
    return row, data


def evaluate(row, data):
    return check.validate(('\t'.join(row)+'\n').encode(), json.dumps(data).encode())


class CalibrationTest(unittest.TestCase):
    def test_complete_record(self):
        self.assertEqual(evaluate(*fixture()), [])

    def test_missing_record_and_no_d(self):
        row, _ = fixture()
        self.assertTrue(check.validate('\t'.join(row).encode(), None))
        row[2] = 'Teste::Sintetico::Topico Rapida'
        self.assertEqual(check.validate('\t'.join(row).encode(), None), [])

    def test_stale_front_back_or_tags(self):
        row, data = fixture()
        for field in range(3):
            edited = row.copy()
            edited[field] += ' alterado'
            self.assertTrue(any('SHA256' in error for error in evaluate(edited, data)))

    def test_incomplete_coverage(self):
        row, data = fixture()
        ce = ('\t'.join(row)+'\n') * 2
        self.assertTrue(any('linha 2' in x for x in check.validate(ce.encode(), json.dumps(data).encode())))

    def test_duplicate_and_unknown_line(self):
        row, data = fixture()
        data['cartoes'].append(copy.deepcopy(data['cartoes'][0]))
        self.assertTrue(any('duplicad' in x for x in evaluate(row, data)))
        data['cartoes'][1]['linha'] = 99
        self.assertTrue(any('não corresponde' in x for x in evaluate(row, data)))

    def test_missing_analysis_and_review(self):
        for key in (*check.ANALYSIS, 'segunda_conferencia', 'decisao'):
            row, data = fixture()
            del data['cartoes'][0][key]
            self.assertTrue(evaluate(row, data), key)

    def test_mismatched_answer(self):
        row, data = fixture()
        data['cartoes'][0]['gabarito'] = 'E'
        self.assertTrue(any('gabarito declarado' in x for x in evaluate(row, data)))

    def test_unknown_or_annulled_reference(self):
        row, data = fixture()
        data['cartoes'][0]['referencias'] = ['AUSENTE']
        self.assertTrue(any('desconhecida' in x for x in evaluate(row, data)))
        row, data = fixture()
        data['referencias'][0]['gabarito_status'] = 'anulado'
        self.assertTrue(any('anulada' in x for x in evaluate(row, data)))

    def test_general_inspiration_requires_disclosure(self):
        row, data = fixture()
        card = data['cartoes'][0]
        card.update(fidelidade='inspiracao_geral', referencias=[])
        card['rubrica']['comparacao']['resultado'] = 'PENDENTE'
        self.assertTrue(any('limitação' in x for x in evaluate(row, data)))
        card['limitacao'] = 'Referência de forma não localizada neste teste.'
        self.assertEqual(evaluate(row, data), [])

    def test_failed_rubric(self):
        row, data = fixture()
        data['cartoes'][0]['rubrica']['correcao']['resultado'] = 'FALHA'
        self.assertTrue(evaluate(row, data))

    def test_short_rubric_evidence_optional_only_for_secondary_criteria(self):
        row, data = fixture()
        for key in ('autoria', 'feedback', 'utilidade'):
            data['cartoes'][0]['rubrica'][key]['evidencia'] = ''
        self.assertEqual(evaluate(row, data), [])
        data['cartoes'][0]['rubrica']['utilidade']['resultado'] = 'FALHA'
        self.assertTrue(evaluate(row, data))
        row, data = fixture()
        data['cartoes'][0]['rubrica']['correcao']['evidencia'] = ''
        self.assertTrue(any('correcao' in e for e in evaluate(row, data)))

    def test_language_and_didactics_required(self):
        row, data = fixture()
        del data['cartoes'][0]['rubrica']['linguagem_didatica']
        self.assertTrue(any('linguagem_didatica' in e for e in evaluate(row,data)))
        row, data = fixture()
        data['cartoes'][0]['rubrica']['linguagem_didatica']['resultado']='FALHA'
        self.assertTrue(evaluate(row,data))

    def test_bad_json_types_dates_urls(self):
        for value in (b'[]', b'{', b'{"schema_version":true}', b'{"schema_version":1,"referencias":null,"cartoes":[]}'):
            row, _ = fixture()
            self.assertTrue(check.validate('\t'.join(row).encode(), value))
        row, data = fixture()
        data['referencias'][0].update(consulta='2026-02-30', url='https://[bad')
        self.assertTrue(evaluate(row, data))

    def test_semantic_limit_false_answer_can_pass_complete_record(self):
        row, data = fixture()
        row[0] = 'Se P então Q. Q é verdadeiro. Portanto P é verdadeiro.'
        row[1] = '✅ Certo<br><br>A ocorrência do consequente comprova a ocorrência do antecedente. 💡 Memorize: resumo sintético.'
        data['cartoes'][0]['sha256'] = check.fingerprint(row)
        # Contraexemplo formal: ambas as premissas verdadeiras e conclusão falsa.
        p_value, q_value = False, True
        self.assertTrue((not p_value) or q_value)
        self.assertTrue(q_value)
        self.assertFalse(p_value)
        # O auditor de conteúdo deve rejeitar; a checagem documental não o faz.
        self.assertEqual(evaluate(row, data), [])

    def test_semantic_limit_definition_tagged_d(self):
        row, data = fixture()
        row[0] = 'Uma proposição lógica admite valor de verdade.'
        data['cartoes'][0]['sha256'] = check.fingerprint(row)
        self.assertEqual(evaluate(row, data), [])

    def test_export_preserves_json_and_zip_revalidation(self):
        exporter = load(ROOT.parent / 'automacao-anki-python/scripts/exportar_anki.py', 'export_calibracao')
        row, data = fixture()
        # O exportador aplica 50/50 também ao perfil focado: dois D, C e E.
        wrong = ['Considere P implica Q e Q falso. Nessas condições, P é verdadeiro.',
                 '❌ Errado<br><br>Se P fosse verdadeiro, a implicação exigiria Q verdadeiro, contrariando a premissa. 💡 Memorize: resumo sintético.',
                 row[2]]
        wrong_record = copy.deepcopy(data['cartoes'][0])
        wrong_record.update(id='D02', linha=2, sha256=check.fingerprint(wrong), gabarito='E',
                            solucao='P deve ser falso: P verdadeiro contradiz Q falso.',
                            erro_plausivel='Afirmar P apesar da negação de Q.')
        data['cartoes'].append(wrong_record)
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            ce, cloze = base/'anki_certo_errado.tsv', base/'anki_cloze.tsv'
            ce.write_text('\t'.join(row)+'\n'+'\t'.join(wrong)+'\n', encoding='utf-8')
            cloze.write_text('', encoding='utf-8')
            reports = base/'relatorios'
            reports.mkdir()
            for name in exporter.REQUIRED_REPORTS:
                (reports/name).write_text('Fixture sintética; não é auditoria de conteúdo.', encoding='utf-8')
            body = json.dumps(data).encode()
            (base/check.REPORT).write_bytes(body)
            self.assertEqual(check.validate(*check.read_package(base)), [])
            write_review(ce,cloze,reports)
            out = base/'out.zip'
            exporter.export(ce, cloze, reports, out, profile='focused', exception_reason='Teste sintético D')
            with zipfile.ZipFile(out) as archive:
                self.assertEqual(archive.read(check.REPORT), body)
            self.assertEqual(check.validate(*check.read_package(out)), [])
            row[0] += ' Revisado.'
            ce.write_text('\t'.join(row)+'\n'+'\t'.join(wrong)+'\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'calibração'):
                exporter.export(ce, cloze, reports, base/'stale.zip', profile='focused', exception_reason='Teste sintético D')

    def test_v2_complete_record(self):
        self.assertEqual(evaluate(*fixture_v2()), [])

    def test_v2_references_require_bank_and_format(self):
        for key in ('banca', 'formato'):
            row, data = fixture_v2()
            del data['referencias'][1][key]
            self.assertTrue(any(key in e for e in evaluate(row, data)), key)

    def test_v2_compared_needs_cebraspe_true_false_reference(self):
        row, data = fixture_v2()
        data['cartoes'][0]['referencias'] = ['REF-FGV']
        self.assertTrue(any('CESPE/Cebraspe Certo/Errado' in e for e in evaluate(row, data)))
        row, data = fixture_v2()
        data['referencias'][0]['formato'] = 'multipla_escolha'
        self.assertTrue(any('CESPE/Cebraspe Certo/Errado' in e for e in evaluate(row, data)))

    def test_v2_other_banks_linked_or_pending(self):
        row, data = fixture_v2()
        data['cartoes'][0]['referencias'] = ['ref-2021-teste-001']
        self.assertTrue(any('outra banca' in e for e in evaluate(row, data)))
        data['cartoes'][0]['outras_bancas_pendencia'] = 'Buscas por FGV/FCC/Vunesp sobre o tema sem item acessível.'
        self.assertEqual(evaluate(row, data), [])

    def test_v2_general_inspiration_may_use_other_bank_only(self):
        row, data = fixture_v2()
        card = data['cartoes'][0]
        card.update(fidelidade='inspiracao_geral', referencias=['REF-FGV'],
                    limitacao='Nenhum item Cebraspe C/E acessível sobre o alvo.')
        card['rubrica']['comparacao']['resultado'] = 'PENDENTE'
        self.assertEqual(evaluate(row, data), [])

    def test_v2_origin_questions_must_be_tags_2_31(self):
        row, data = fixture_v2()
        row[2] = row[2].replace(' REF-FGV', '')
        data['cartoes'][0]['sha256'] = check.fingerprint(row)
        self.assertIn('D01: tag da questão de origem REF-FGV ausente', evaluate(row, data))
        row, data = fixture()  # schema 1 (legado) não exige a tag
        row[2] = row[2].replace(' ref-2021-teste-001', '')
        data['cartoes'][0]['sha256'] = check.fingerprint(row)
        self.assertEqual(evaluate(row, data), [])

    def test_v1_remains_accepted_without_bank_fields(self):
        row, data = fixture()
        self.assertEqual(data['schema_version'], 1)
        self.assertEqual(evaluate(row, data), [])


if __name__ == '__main__':
    unittest.main()
