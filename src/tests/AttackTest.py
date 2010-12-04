
"""
Modul testujacy modul attack.
"""

import unittest
from main.attack import Attack
import Queue

class Tran:
    """Klasa testowej transformacji."""
    def transform(self, a, b):
        return b
    
class Serv:
    """Klasa testowej uslugi."""
    def auth(self, a, b):
        if a == b:
            return True
        else:
            return False

class Test(unittest.TestCase):
    """Klasa testow jednostkowych."""

    def testValue(self):
        """Test wartosci.
        
        Funkcja testuje czy atak znajduje poprawne rozwiazania.
        
        """
        k_u = ["marcin", "tom", "test"]
        k_s = ["marcin", "tom"]
        k_r_s = [":"]
        
        t = Tran()
        s = Serv()
        
        Q1 = Queue.Queue()
        Q2 = Queue.Queue()
        
        g = Attack(k_u, k_s, k_r_s, t, Q1, Q2)
        for x in g:
            pass
        
        r = {}
        while True:
            try:
                a, b = Q1.get_nowait()
                if s.auth(a, b):
                    r[a] = b
            except:
                break
        
        self.assertEquals(r, {"marcin" : "marcin", "tom": "tom"})
        
    def testNoneResult(self):
        """Test braku wyniku.
        
        Funkcja testuje czy atak poprawnie sie zachowuje w przypadku braku wyniku.        
        
        """
        k_u = ["marcin", "tom", "test"]
        k_s = [""]
        k_r_s = [":"]
        
        t = Tran()
        s = Serv()
        
        Q1 = Queue.Queue()
        Q2 = Queue.Queue()
        
        g = Attack(k_u, k_s, k_r_s, t, Q1, Q2)
        for x in g:
            pass
        
        r = {}
        while True:
            try:
                a, b = Q1.get_nowait()
                if s.auth(a, b):
                    r[a] = b
            except:
                break
        self.assertEquals(r, {})
        
    def testNull(self):
        """Test pustych danych wejsciowych.
        
        Funkcja testuje czy atak poprawnie sie zachowuje w przypadku braku danych wejsciowych.
        
        """
        k_u = []
        k_s = []
        k_r_s = []
        
        t = Tran()
        s = Serv()
        
        Q1 = Queue.Queue()
        Q2 = Queue.Queue()
        
        g = Attack(k_u, k_s, k_r_s, t, Q1, Q2)
        for x in g:
            pass
        
        r = {}
        while True:
            try:
                a, b = Q1.get_nowait()
                if s.auth(a, b):
                    r[a] = b
            except:
                break
        self.assertEquals(r, {})

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testValue']
    unittest.main()
