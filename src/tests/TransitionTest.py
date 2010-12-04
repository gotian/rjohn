
"""
Modul testujacy modul transition.
"""

import unittest
from utils.transition import Transition

class Test(unittest.TestCase):
    """Klasa testow jednostkowych."""

    def testSimpleCommands(self):
        """Test prostych komend."""
        word = "aLaMakota123"
        t = Transition()
        
        rules = ':'
        self.assertEquals(t.transform(rules, word), word)
        
        rules = 'c'
        self.assertEquals(t.transform(rules, word), "Alamakota123")
        
        rules = 'l'
        self.assertEquals(t.transform(rules, word), "alamakota123")
        
        rules = 'u'
        self.assertEquals(t.transform(rules, word), "ALAMAKOTA123")
        
        rules = 'C'
        self.assertEquals(t.transform(rules, word), "aLAMAKOTA123")
        
        rules = 't'
        self.assertEquals(t.transform(rules, word), "AlAmAKOTA123")
        
        rules = 't0'
        self.assertEquals(t.transform(rules, word), "ALaMakota123")
        
        rules = 'r'
        self.assertEquals(t.transform(rules, word), "321atokaMaLa")
        
        rules = 'd'
        self.assertEquals(t.transform(rules, word), "aLaMakota123aLaMakota123")
        
        rules = '$q'
        self.assertEquals(t.transform(rules, word), "aLaMakota123q")
        
        rules = '^q'
        self.assertEquals(t.transform(rules, word), "qaLaMakota123")
        
        rules = '{'
        self.assertEquals(t.transform(rules, word), "LaMakota123a")
        
        rules = '}'
        self.assertEquals(t.transform(rules, word), "3aLaMakota12")
        
        rules = 'f'
        self.assertEquals(t.transform(rules, word), "aLaMakota123321atokaMaLa")
        
    def testNoRule(self):
        """Test braku regul."""
        word = "aLaMakota123"
        t = Transition()
        
        rules = 'H'
        try:
            t.transform(rules, word)
        except ValueError:
            return
        self.fail("Exception raisen")
        
    def testCharacterClassCommands(self):
        """Test komend bazujacych na klasach znakow."""
        word = "aLaMakota123"
        t = Transition()
        
        rules = 'sab'
        self.assertEquals(t.transform(rules, word), "bLbMbkotb123")
        
        rules = 's?vH'
        self.assertEquals(t.transform(rules, word), "HLHMHkHtH123")
        
        rules = '@M'
        self.assertEquals(t.transform(rules, word), "aLaakota123")
        
        rules = '@?c'
        self.assertEquals(t.transform(rules, word), "aaaoa123")
        
        rules = '!1'
        self.assertEqual(t.transform(rules, word), None)
        
        rules = '!?v'
        self.assertEqual(t.transform(rules, word), None)
        
        rules = '/1'
        self.assertEquals(t.transform(rules, word), "aLaMakota123")
        
        rules = '/?v'
        self.assertEquals(t.transform(rules, word), "aLaMakota123")
        
        rules = '=0a'
        self.assertEquals(t.transform(rules, word), "aLaMakota123")
        
        rules = '=A?d'
        self.assertEquals(t.transform(rules, word), "aLaMakota123")
        
        rules = '(b'
        self.assertEqual(t.transform(rules, word), None)
        
        rules = '(?d'
        self.assertEqual(t.transform(rules, word), None)
        
        rules = ')H'
        self.assertEqual(t.transform(rules, word), None)
        
        rules = ')?v'
        self.assertEqual(t.transform(rules, word), None)
        
        rules = '%4a'
        self.assertEquals(t.transform(rules, word), "aLaMakota123")
        
        rules = '%3?d'
        self.assertEquals(t.transform(rules, word), "aLaMakota123")
        
    def testStringCommands(self):
        """Test komend pracujacych na stringach."""
        word = "aLaMakota123"
        t = Transition()
        
        rules = "A0\"testowe pole\""
        self.assertEquals(t.transform(rules, word), "testowe poleaLaMakota123")
        
        rules = "Az\"testowe pole\""
        self.assertEquals(t.transform(rules, word), "aLaMakota123testowe pole")
        
    def testLengthControlCommands(self):
        """Test komend kontroli dlugosci."""
        word = "aLaMakota123"
        t = Transition()
        
        rules = '<5'
        self.assertEqual(t.transform(rules, word), None)
        
        rules = '<Z'
        self.assertEquals(t.transform(rules, word), "aLaMakota123")
        
        rules = '>Z'
        self.assertEqual(t.transform(rules, word), None)
        
        rules = '>5'
        self.assertEquals(t.transform(rules, word), "aLaMakota123")
        
        rules = '\'9'
        self.assertEquals(t.transform(rules, word), "aLaMakota")
        
    def testIDCommands(self):
        """Test komend wykonujacych operacje insert i delete."""
        word = "aLaMakota123"
        t = Transition()
        
        rules = '['
        self.assertEquals(t.transform(rules, word), "LaMakota123")
        
        rules = ']'
        self.assertEquals(t.transform(rules, word), "aLaMakota12")
        
        rules = 'D5'
        self.assertEquals(t.transform(rules, word), "aLaMaota123")
        
        rules = 'x43'
        self.assertEquals(t.transform(rules, word), "ako")
        
        rules = 'i7H'
        self.assertEquals(t.transform(rules, word), "aLaMakoHta123")
        
        rules = 'o8Q'
        self.assertEquals(t.transform(rules, word), "aLaMakotQ123")
        
    def testCharacterClasses(self):
        """Test klas znakow."""
        t = Transition()
        
        rules = '(??'
        word = "?"
        self.assertEquals(t.transform(rules, word), "?")
        
        rules = '(?v'
        word = "a"
        self.assertEquals(t.transform(rules, word), "a")
        
        rules = '(?c'
        word = "b"
        self.assertEquals(t.transform(rules, word), "b")
        
        rules = '(?w'
        word = " "
        self.assertEquals(t.transform(rules, word), " ")
        
        rules = '(?p'
        word = ";"
        self.assertEquals(t.transform(rules, word), ";")
        
        rules = '(?s'
        word = "*"
        self.assertEquals(t.transform(rules, word), "*")
        
        rules = '(?l'
        word = "v"
        self.assertEquals(t.transform(rules, word), "v")
        
        rules = '(?u'
        word = "P"
        self.assertEquals(t.transform(rules, word), "P")
        
        rules = '(?d'
        word = "6"
        self.assertEquals(t.transform(rules, word), "6")
        
        rules = '(?a'
        word = "s"
        self.assertEquals(t.transform(rules, word), "s")
        
        rules = '(?x'
        word = "3"
        self.assertEquals(t.transform(rules, word), "3")
        
        rules = '(?z'
        word = " "
        self.assertEquals(t.transform(rules, word), " ")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCharacterClasses']
    unittest.main()
