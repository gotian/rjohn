# -*- coding: utf-8 -*-

"""
Moduł obsługujący protokuł HTTP.

Protokół ten jest dokładnie opisany w dokumencie RFC 2616.
"""

import socket
import time
import re
import base64

from services.service import ServiceException
from optparse import OptionGroup
import urlparse

class HttpServiceException(ServiceException):
    """Klasa błędu. Wyrzucana w przypadku błędu modułu Http"""
    pass

HTTP_PORT = 80
"""Standardowy numer portu HTTP."""

class Http:
    
    """Klasa implementująca protokuł HTTP.
    
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
        self.port = HTTP_PORT
        if "port" in config:
            self.port = config["port"]
        self.sleep = 0
        if "sleep" in config:
            self.sleep = config["sleep"]
            
    def create_socket(self):
        """Zwraca stworzony socket."""
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def __open(self):
        """Otwiera socket."""
        sock = self.create_socket()
        sock.connect((self.hostname, self.port))
        return sock
        
    def __close(self, sock):
        """Zamyka socket."""
        sock.close()

    def auth(self, username, password):
        """Wykonuje próbę uwierzytelnienia.
        
        W przypadku tego modułu wykonywane jest połączenie z serwerem i 
        wysłanie danych uwierzytelniających. Zaimplementowany jest 
        typ uwierzytelnienia BASIC.
        
        """
        s = self.__open()
        time.sleep(float(self.sleep)) 
        
        request = 'GET ' + self.path + ' HTTP/1.0' + ' \r\n\n'
        s.send(request)
        
        data_r = s.recv(1024)
        data_r = data_r.decode()
        
        self.__close(s)
        
        authlines = data_r.lower().splitlines()
        authline = None
        for x in authlines:
            if x.startswith("www-authenticate"):
                authline = x
                break
            
        if authline is None:
            raise HttpServiceException(_("Serwer nie zwrócił nagłówka autoryzacyjnego"))
            
        authobj = re.compile(r'''(?:\s*www-authenticate\s*:)?\s*(\w*)\s+realm=['"]([^'"]+)['"]''', re.IGNORECASE)
        matchobj = authobj.match(authline)
        
        if not matchobj:
            raise HttpServiceException(_("Nagłówek autoryzacyjny niepoprawny"))
        
        scheme = matchobj.group(1)
        realm = matchobj.group(2)
        
        if scheme.lower() == 'basic':
            b64 = username + ":" + password
        
            base64string = base64.b64encode(b64)
            authheader = "Authorization: Basic %s" % base64string.decode()
        
            request = 'GET ' + self.path + ' HTTP/1.0' + ' \r\n'
            request += authheader + '\r\n\n'
        
            s = self.__open()
            time.sleep(float(self.sleep))
            
            s.send(request)
        
            data_r = s.recv(1024)
            data_r = data_r.decode().lower()  
        
            res = data_r.find("401 authorization required")
            if res == -1:
                self.__close(s)
                return True
            else:
                self.__close(s)
                return False
        
        self.__close(s)
        return False
        
def getOptionGroup(parser):
    """Zwraca pomoc dla grupy opcji."""
    group = OptionGroup(parser, _("Opcje dla modulu Http"),
                        _("sleep=CZAS - odczekanie po polaczeniu"))
    return group

def parseOptionGroup(option):
    """Parsuje ciąg opcji dodatkowych, zwraca dict."""
    config = {}
    option = option.split(",")
    for x in option:
        x = x.split("=")
        config[x[0]] = x[1]
        
    return config
