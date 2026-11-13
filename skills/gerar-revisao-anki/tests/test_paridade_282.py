import unittest
from test_gabaritos_rapidos import module, linha

class ParidadeTests(unittest.TestCase):
    def check(self, r, d):
        data=''.join(linha(True,v,i) for i,v in enumerate(r))
        data+=''.join(linha(False,v,100+i) for i,v in enumerate(d))
        return module.contar_modos(data.encode(),True)[1]
    def test_both_balanced(self):
        self.assertFalse(self.check([True,False],[False,True]))
    def test_global_balance_not_enough(self):
        self.assertTrue(self.check([True,True],[False,False]))
    def test_hard_unbalanced(self):
        self.assertTrue(self.check([True,False],[True,True]))
    def test_focused_balanced(self):
        self.assertFalse(self.check([],[True,False]))
    def test_odd_hard_rejected(self):
        self.assertTrue(self.check([],[True,False,True]))
    def test_one_new_rejected(self):
        self.assertTrue(self.check([True],[]))
    def test_empty_modes(self):
        self.assertFalse(self.check([],[]))
if __name__=='__main__':
    unittest.main()
