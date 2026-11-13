"""Regressão Anki v1.6: metarreferência, Cloze flexível, índices e contagem real."""
import importlib.util
import pathlib
import tempfile
import unittest
import zipfile

HERE = pathlib.Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('anki_validator', HERE/'scripts'/'validar_anki.py')
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

CE_FRONT = ('Em uma atividade, os alunos observam resultados e ajustam hipóteses. '
            'A professora atribui a conclusão à perspectiva empirista de Locke, '
            'porque o raciocínio crítico também é necessário.')
CE_BACK = ('❌ Errado<br><br>A combinação proposta articula observação e racionalização; '
           'não é adequadamente explicada pela ênfase empirista isolada.'
           '<br><br>💡 Memorize: diferencie experiência sensorial e sua elaboração racional.')
TAGS = 'Fundamentos_da_Educacao Teorias_Pedagogicas Estilo_Cebraspe'
EXTRA = 'As autarquias são pessoas jurídicas da administração indireta.<br><br>💡 Memorize: autarquia tem personalidade.'


def check(text):
    errors = []
    n = validator.verify_tsvo('anki_cloze.tsv', f'{text}\t{EXTRA}\tAdministrativo Autarquias'.encode('utf-8'), errors)
    return n, errors


class StaticTests(unittest.TestCase):
    def test_ce_valido(self):
        errors=[]
        self.assertEqual(validator.verify_tsvo('anki_certo_errado.tsv',
            f'{CE_FRONT}\t{CE_BACK}\t{TAGS}'.encode(), errors), 1)
        self.assertEqual(errors, [])

    def test_metarreferencias_reais_bloqueadas(self):
        cases = [
            'Segundo a comparação apresentada no material, a classificação é correta.',
            'Segundo o material, Descartes defende a razão.',
            'Para Piaget, conforme o PDF, a interação importa.',
            'Segundo a concepção democrática estudada, há equidade.',
            'Segundo a distinção feita na aula, a proposta é inclusão.',
            'A visão de Rousseau apresentada no material está correta.',
            'Na instrução programada descrita no PDF, há correção.',
            'De acordo com a apostila, a resposta é X.',
            'Como vimos anteriormente, a educação demanda reflexão.',
        ]
        for front in cases:
            with self.subTest(front=front):
                errors=[]
                validator.verify_tsvo('anki_certo_errado.tsv',
                    f'{front}\t{CE_BACK}\t{TAGS}'.encode(), errors)
                self.assertTrue(any('menção à fonte proibida' in e for e in errors), errors)

    def test_fontes_intrinsecas_permitidas(self):
        for front in [
            'Segundo Rousseau, a infância possui características próprias.',
            'Em uma aula experimental, os alunos investigam a força de atrito.',
            'O professor selecionou material didático acessível para a turma.',
            'Conforme o art. 5º da Constituição, há direitos fundamentais.',
        ]:
            with self.subTest(front=front):
                errors=[]
                validator.verify_tsvo('anki_certo_errado.tsv',
                    f'{front}\t{CE_BACK}\t{TAGS}'.encode(), errors)
                self.assertFalse(any('menção à fonte proibida' in e for e in errors),errors)

    def test_cloze_qualquer_posicao_e_pontuacao(self):
        for text in [
            '{{c1::Autarquias}} possuem personalidade jurídica própria.',
            'Uma autarquia é uma {{c1::pessoa jurídica de direito público}}.',
            'Na posição estatal, ministérios são órgãos {{c1::autônomos}}.',
            'Na posição estatal, ministérios são {{c1::órgãos autônomos}}!',
            'A lei exige {{c1::30 dias}} para o prazo hipotético.',
            'O princípio fundamental é a {{c1::legalidade::nome do princípio}}, em sentido administrativo.',
        ]:
            with self.subTest(text=text):
                n, errors=check(text)
                self.assertEqual(n,1)
                self.assertEqual(errors,[])

    def test_multiplos_indices_contagem_real(self):
        txt='A {{c1::desconcentração}} age dentro da mesma pessoa; {{c2::descentralização}} envolve outra.'
        n,e=check(txt)
        self.assertEqual((n,e),(1,[]))
        counted=validator.count_cloze_cards(f'{txt}\t{EXTRA}\tAdministrativo'.encode())
        self.assertEqual(counted, {'notas_cloze':1, 'cartoes_cloze':2})

    def test_grupo_mesmo_indice_conta_um(self):
        txt='Uma {{c1::lei específica}} {{c1::cria a autarquia}}.'
        self.assertEqual(check(txt), (1,[]))
        self.assertEqual(validator.count_cloze_cards(f'{txt}\t{EXTRA}\tAdministrativo'.encode())['cartoes_cloze'],1)

    def test_invalidos_sintaxe_e_indice(self):
        cases=[
            'Não há lacuna aqui.',
            'O {{c1::}} é relevante.',
            'O {{c1::palavra} está mal fechado.',
            'O {{c2::autônomo}} está sem c1.',
            'O {{c1::palavra::}} tem dica vazia.',
            'O {{c1::palavra::palavra}} tem dica igual.',
            'O {{c1::palavra}}}} tem chave sobrando.',
            'O {{c1::palavra {{c2::outra}}}} aninhado não é suportado.',
        ]
        for text in cases:
            with self.subTest(text=text):
                _,errors=check(text)
                self.assertTrue(errors, f'{text} deve ser inválido')

    def test_zip_integridade(self):
        with tempfile.TemporaryDirectory() as d:
            path=pathlib.Path(d)/'modelo.zip'
            with zipfile.ZipFile(path,'w') as z:
                for file in validator.REQUIRED:
                    if file=='anki_certo_errado.tsv':
                        txt=f'{CE_FRONT}\t{CE_BACK}\t{TAGS}\n'
                    elif file=='anki_cloze.tsv': txt=''
                    else: txt='Relatório de auditoria do pacote.'
                    z.writestr(file,txt)
            self.assertIsNone(zipfile.ZipFile(path).testzip())
            self.assertEqual(set(validator.REQUIRED),set(zipfile.ZipFile(path).namelist()))

if __name__=='__main__': unittest.main()

