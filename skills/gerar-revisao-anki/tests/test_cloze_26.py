import importlib.util
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[1]/'scripts/validar_anki.py'
s=importlib.util.spec_from_file_location('validate26',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
class NewClozeTests(unittest.TestCase):
 def check(self,text,tags='Teste::Sintetico::Topico Cloze'):
  return self.check_extra(text,'Explicação específica.',tags)
 def check_extra(self,text,extra,tags='Teste::Sintetico::Topico Cloze'):
  errors=[];v.validate_new_cloze((text+'\t'+extra+'\t'+tags+'\n').encode(),errors);return errors
 def test_word(self): self.assertEqual(self.check('Alvo {{c1::palavra}}.'),[])
 def test_expression(self): self.assertEqual(self.check('Alvo {{c1::expressão de várias palavras}}.'),[])
 def test_repeated_c1_only_in_mnemonic(self):
  text = '{{c1::A}} e {{c1::B}}'
  self.assertTrue(any('mnemônico' in e for e in self.check(text)))
  mn = '<b>Mnemônico SM:</b><br>Partes do protocolo: S{{c1::ua}} M{{c1::ensagem}}.'
  origem = 'Explicação de cada termo.<div>📚 Origem do mnemônico Autoral: criado para este card.</div>'
  self.assertEqual(self.check_extra(mn, origem), [])
  self.assertTrue(any('Origem do mnemônico' in e for e in self.check_extra(mn, 'Explicação sem origem.')))
  # o caso reprovado pelo usuário (2.33): origem na frente e a lista inteira numa lacuna só
  self.assertTrue(self.check('Dica autoral SM: o protocolo tem {{c1::Sua Mensagem}}.'))
  self.assertTrue(self.check_extra('<b>Mnemônico SM:</b> protocolo: {{c1::Sua Mensagem}}.', origem))
  self.assertTrue(self.check_extra('<b>Mnemônico SM:</b> protocolo: {{c1::Sua}} {{c1::Mensagem}}.', origem))
  self.assertEqual(v.count_cloze_cards(f'{text}\tExtra\tTeste::Sintetico::Topico Cloze\n'.encode()),
                   {'notas_cloze': 1, 'cartoes_cloze': 1})
 def test_multiple_indices(self): self.assertTrue(self.check('{{c1::A}} e {{c2::B}}'))
 def test_c2_only(self): self.assertTrue(self.check('{{c2::A}}'))
 def test_four_independent_notes(self):
  data='\n'.join(f'Contexto {i}: {{{{c1::termo {i}}}}}.\tSignificado específico {i}.\tTeste::Sintetico::Topico Cloze' for i in range(4)).encode()
  errors=[];v.validate_new_cloze(data,errors)
  self.assertFalse(errors);self.assertEqual(v.count_cloze_cards(data),{'notas_cloze':4,'cartoes_cloze':4})
 def test_existing_indices_still_counted(self):
  errors=[];self.assertEqual(v.parse_cloze('{{c1::A}} {{c1::B}} {{c2::C}}',errors,'antiga'),{1,2});self.assertFalse(errors)
if __name__=='__main__':unittest.main()
