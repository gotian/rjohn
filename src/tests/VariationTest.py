
"""
Modul testujacy modul variation.
"""

import unittest
from combinatorics.variation import OutOfRangeException, StringVariation, \
    RangeStringVariation
import itertools

class Test(unittest.TestCase):
    """Klasa testow jednostkowych."""

    def testInit(self):
        """Test warunkow poczatkowych."""
        self.assertRaises(OutOfRangeException, StringVariation, ('a', 'b', 'c'), -2)
        self.assertRaises(OutOfRangeException, StringVariation, ('a', 'b', 'c'), -1)
        
    def testIter(self):
        """Test iteratora."""
        w = StringVariation(('a', 'b', 'c'), 2)
        try:
            i = iter(w)
        except TypeError:
            self.fail("Exception raisen")
        
    def testStop(self):
        """Test ilosci iteracji."""
        n = 6
        k = 4
        w = StringVariation("".join([str(elem) for elem in range(n)]), k)
        i = iter(w)
        ww = n ** k
        for x in range(ww):
            next(i)
        try:
            next(i)
        except StopIteration:
            return
        self.fail("No exception raisen")
        
    def testValue(self):
        """Test uzyskiwanych wartosci."""
        str = "abc"
        k = 1
        w = RangeStringVariation(str, k, k + 1)
        ref = ['a', 'b', 'c']
        
        y = 0
        for x in w:
            self.assertEqual(x, ref[y])
            y += 1
            
        k = 2
        w = RangeStringVariation(str, k, k + 1)
        ref = ['aa', 'ab', 'ac', 'ba', 'bb', 'bc', 'ca', 'cb', 'cc']
        
        y = 0
        for x in w:
            self.assertEqual(x, ref[y])
            y += 1
            
        k = 3
        w = RangeStringVariation(str, k, k + 1)
        ref = ['aaa', 'aab', 'aac', 'aba', 'abb', 'abc', 'aca', 'acb', 'acc', 'baa', 'bab', 'bac',
               'bba', 'bbb', 'bbc', 'bca', 'bcb', 'bcc', 'caa', 'cab', 'cac', 'cba', 'cbb', 'cbc',
               'cca', 'ccb', 'ccc']
        
        y = 0
        for x in w:
            self.assertEqual(x, ref[y])
            y += 1
            
    def testZakresowaInit(self):
        """Test warunkow poczatkowych dla wariacji zakresowej."""
        self.assertRaises(OutOfRangeException, RangeStringVariation, ('a', 'b', 'c'), 3, 3)
        self.assertRaises(OutOfRangeException, RangeStringVariation, ('a', 'b', 'c'), 3, 2)
        
    def testZakresowaCount(self):
        """Test ilosci generowanych danych dla wariacji zakresowej."""
        kmin = 1
        kmax = 4
        c = 0
        str = "abc"
        w = RangeStringVariation(str, kmin, kmax)
        for x in range(kmin, kmax):
            c += len(str) ** x
            
        i = iter(w)
        for x in range(c):
            next(i)
        try:
            next(i)
        except StopIteration:
            return
        self.fail("No exception raisen")  
     
    def testPerformance1(self):
        """Test wydajnosci algorytmu."""
        w = RangeStringVariation("abcdefg", 7, 8)
        for x in w:
            pass
    
    def testPerformance2(self):
        """Test wydajnosci wbudowanego algorytmu."""
        w = itertools.product("abcdefg", repeat=7)
        for x in w:
            "".join(x)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
