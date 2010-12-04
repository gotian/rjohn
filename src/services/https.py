# -*- coding: utf-8 -*-

"""
Moduł obsługujący protokuł HTTPS.

Protokół ten jest protokołem HTTP działającym w kanale SSL.
"""

from services.http import Http
import ssl
from optparse import OptionGroup
from services.service import ServiceException
import socket
import urlparse

class HttpsServiceException(ServiceException):
    """Klasa błędu. Wyrzucana w przypadku błędu modułu Https"""
    pass

HTTPS_PORT = 443
"""Standardowy numer portu HTTPS."""

class Https(Http):
    
    """Klasa implementująca protokuł HTTPS.
    
    Jej zadaniem jest wykonanie próby uwierzytelnienia.
    """

    def __init__(self, config):
        """Konstruktor.
        
        Argumenty:
        config -- słownik zawierający konfigurację 
        
        """
        o = urlparse.urlparse(config["hostname"])
        
        self.hostname = o.hostname
        self.path = o.path
        self.port = HTTPS_PORT
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
    group = OptionGroup(parser, _("Opcje dla modulu Https"),
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

        
