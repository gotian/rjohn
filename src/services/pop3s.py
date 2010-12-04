# -*- coding: utf-8 -*-

"""
Moduł obsługujący protokuł POP3S.

Protokół ten jest protokołem POP3 działającym w kanale SSL.
"""

import ssl
from optparse import OptionGroup
from services.service import ServiceException
import socket
from services.pop3 import Pop3

class Pop3sServiceException(ServiceException):
    """Klasa błędu. Wyrzucana w przypadku błędu modułu Pop3s"""
    pass

POP3S_PORT = 995
"""Standardowy numer portu POP3S."""

class Pop3s(Pop3):
    
    """Klasa implementująca protokuł POP3S.
    
    Jej zadaniem jest wykonanie próby uwierzytelnienia.
    """

    def __init__(self, config):
        """Konstruktor.
        
        Argumenty:
        config -- słownik zawierający konfigurację 
        
        """
        self.hostname = config["hostname"]
        self.port = POP3S_PORT
        if "port" in config:
            self.port = config["port"]
        self.sleep = 0
        if "sleep" in config:
            self.sleep = config["sleep"]
        
        self.keyfile = None
        self.certfile = None
        if "keyfile" in config:
            self.keyfile = config["keyfile"]
        if "certfile" in config:
            self.certfile = config["certfile"]
        
    def create_socket(self):
        """Zwraca stworzony ssl socket."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return ssl.wrap_socket(sock, self.keyfile, self.certfile)
    
def getOptionGroup(parser):
    """Zwraca pomoc dla grupy opcji."""
    group = OptionGroup(parser, _("Opcje dla modulu Pop3s"),
                        _("sleep=CZAS - odczekanie po polaczeniu, "
                          "certfile=PLIK - certyfikat dla ssl, " 
                          "keyfile=PLIK - klucz dla ssl"))
    return group

def parseOptionGroup(option):
    """Parsuje ciąg opcji dodatkowych, zwraca dict."""
    config = {}
    option = option.split(",")
    for x in option:
        x = x.split("=")
        config[x[0]] = x[1]
        
    return config
