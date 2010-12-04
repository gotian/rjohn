# -*- coding: utf-8 -*-

"""
Moduł zawierający klasy realizujące wariacje.
"""

import itertools

class OutOfRangeException(ValueError):    
    """Klasa błędu. Wyrzucana w przypadku błędu zakresu danych wejściowych."""
    pass

class Variation:
    
    """Klasa implementująca wariacje.
    
    Zadaniem tej klasy jest dostarczenie iterowalnego interfejsu 
    do wykonywania wariacji. Elementy stanowiące wariacje są 
    liczbami.
    """

    def __init__(self, n, k):
        """Konstruktor.
        
        Argumenty:
        n -- liczba elementów zbioru
        k -- liczba wyrazów wariacji
        
        """
        self.n, self.k = n, k
        if (n < 1) or (k < 1):
            raise OutOfRangeException
        
    def __iter__(self):
        """Inicjalizacja generatora."""
        self.var = [elem * 0 for elem in range(self.k)]
        self.var[self.k - 1] = -1
        self.i = self.k - 1
        return self
        
    def next(self):
        """Zwraca kolejną wariację, obiekt list."""
        if self.var[self.i] != self.n - 1:
            self.var[self.i] += 1
            return self.var
        else:
            while self.var[self.i] == self.n - 1:
                self.var[self.i] = 0
                self.i -= 1
                if (self.i == -1):
                    raise StopIteration
            if (self.i == -1):
                raise StopIteration
            self.var[self.i] += 1
            self.i = self.k - 1
            return self.var
        
class StringVariation(Variation):
    
    """Klasa implementuje wariację operującą na elementach napisu.
    
    Zadaniem tej klasy jest dostarczenie iterowalnego interfejsu.
    Ilość elementów zbioru jest równa długości przetwarzanego łańcucha.
    """
    
    def __init__(self, string, k):
        """Konstruktor.
        
        Argumenty:
        string -- łańcucha znaków 
        k -- liczba wyrazów wariacji
        
        """
        Variation.__init__(self, len(string), k)
        self.string = string
        
    def __iter__(self):
        """Inicjalizacja generatora."""
        return Variation.__iter__(self)
    
    def next(self):
        """Zwraca kolejną wariację, obiekt str."""
        res = Variation.next(self)
        return "".join([self.string[elem] for elem in res])

class RangeStringVariation():
    
    """Klasa implementuje wariację zakresową operująca na elementach napisu.
    
    Zadaniem tej klasy jest dostarczenie iterowalnego interfejsu.
    Ilość elementów zbioru jest równa długości przetwarzanego łańcucha.
    Ilość wyrazów wariacji podana jest jako przedział.
    """
    
    def __init__(self, string, kmin, kmax):
        """Konstruktor.
        
        Inicjalizuje generator wariacji dla k=<kmin;kmax).
        
        Argumenty:
        string -- łańcuch znaków
        kmin -- minimalna wartość liczby wyrazów wariacji
        kmax -- maksymalna wartość liczby wyrazów wariacji
        
        """
        self.string, self.kmin, self.kmax = string, kmin, kmax
        if kmin >= kmax:
            raise OutOfRangeException
        
    def __iter__(self):
        """Inicjalizacja generatora."""
        self.svar = [StringVariation(self.string, elem) for elem in range(self.kmin, self.kmax)]
        self.i = 0
        self.iter = iter(self.svar[self.i])
        return self
    
    def next(self):
        """Zwraca kolejną wariację, obiekt str."""
        try:
            return next(self.iter)
        except StopIteration:
            self.i += 1
            if self.i >= len(self.svar):
                raise StopIteration
            self.iter = iter(self.svar[self.i])
            return next(self.iter)

"""
class RangeStringVariation():
    def __init__(self, string, kmin, kmax):
        self.string, self.kmin, self.kmax = string, kmin, kmax
        if kmin >= kmax:
            raise OutOfRangeException
        
    def __iter__(self):
        self.svar = [itertools.product(self.string, repeat=elem) for elem in range(self.kmin, self.kmax)]
        self.i = 0
        self.iter = iter(self.svar[self.i])
        return self
    
    def next(self):
        try:
            return "".join(next(self.iter))
        except StopIteration:
            self.i+=1
            if self.i >= len(self.svar):
                raise StopIteration
            self.iter = iter(self.svar[self.i])
            return "".join(next(self.iter))
"""
        
