# -*- coding: utf-8 -*-

"""
Moduł obsługujący protokuł FILE.

Moduł ten zapewnia funkcjonalność zapisu zbioru wejściowego do pliku.
"""

from optparse import OptionGroup
import threading
from services.service import ServiceException

class FileServiceException(ServiceException):
    """Klasa błędu. Wyrzucana w przypadku błędu modułu File"""
    pass

class File:
    
    """Klasa implementująca protokuł FILE.
    
    Jej zadaniem jest zapisywania do pliku wyjściowego, znajdującego w zmiennej 
    config["hostname"] danych wejściowych przekazywanych poprzez funkcje auth().
    
    """
    
    lock = threading.Lock()
    """Blokada zapewniająca że tylko jeden wątek będzie zapisywał dane do pliku"""
    
    def __init__(self, config):
        """Konstruktor.
        
        Argumenty:
        config -- słownik zawierający konfigurację 
        
        """
        self.file = config["hostname"]
        
    def __open(self):
        """Otwiera plik."""
        return open(self.file, 'a')
    
    def __close(self, file):
        """Zamyka plik."""
        file.close()
    
    def auth(self, username, password):
        """Wykonuje próbę uwierzytelnienia.
        
        W przypadku tego modułu zapisuje ona do pliku hasło podane w danych wejściowych.
        
        """
        File.lock.acquire()
        
        try:
            file = self.__open()
            file.write(password + "\n")
            self.__close(file)
        except IOError as err:
            raise FileServiceException(_("Problem w dostępie do pliku: {0}".format(err)))
        
        File.lock.release()
        
        return False
    
def getOptionGroup(parser):
    """Zwraca pomoc dla grupy opcji."""
    group = OptionGroup(parser, _("Opcje dla modulu File"))
    return group

def parseOptionGroup(option):
    """Parsuje ciąg opcji dodatkowych, zwraca dict."""
    config = {}
    option = option.split(",")
    for x in option:
        x = x.split("=")
        config[x[0]] = x[1]
        
    return config
