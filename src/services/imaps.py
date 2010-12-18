# -*- coding: utf-8 -*-

"""
Moduł obsługujący protokuł IMAPS.

Protokół ten jest protokołem IMAP działającym w kanale SSL.
"""

import socket
from services.service import ServiceException
from optparse import OptionGroup
import ssl
from services.imap import Imap

class ImapsServiceException(ServiceException):
    """Klasa błędu. Wyrzucana w przypadku błędu modułu Imaps"""
    pass

IMAPS_PORT = 993
"""Standardowy numer portu IMAPS."""

class Imaps(Imap):
    
    """Klasa implementująca protokuł IMAP.
    
    Jej zadaniem jest wykonanie próby uwierzytelnienia.
    """
    
    def __init__(self, config):
        """Konstruktor.
        
        Argumenty:
        config -- słownik zawierający konfigurację 
        
        """
        self.hostname = config["hostname"]
        self.port = IMAPS_PORT
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
            
        self.auth_info = "0"
        if "auth-info" in config:
            self.auth_info = config["auth-info"]
            
    def create_socket(self):
        """Zwraca stworzony ssl socket."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return ssl.wrap_socket(sock, self.keyfile, self.certfile)
        
def getOptionGroup(parser):
    """Zwraca pomoc dla grupy opcji."""
    group = OptionGroup(parser, _("Opcje dla modulu Imaps"),
                        _("sleep=CZAS - odczekanie po polaczeniu, "
                          "certfile=PLIK - certyfikat dla ssl, " 
                          "keyfile=PLIK - klucz dla ssl, " 
                          "auth-info=0/1 - wyswietla informacje dodatkowe przy uwierzytelnieniu"))
    return group

def parseOptionGroup(option):
    """Parsuje ciąg opcji dodatkowych, zwraca dict."""
    config = {}
    option = option.split(",")
    for x in option:
        x = x.split("=")
        config[x[0]] = x[1]
        
    return config
