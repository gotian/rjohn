# -*- coding: utf-8 -*-

"""
Moduł obsługujący protokuł IMAP.

Protokół ten jest dokładnie opisany w dokumencie RFC 3501.
"""

import socket
import time
from services.service import ServiceException
from optparse import OptionGroup
import re

class ImapServiceException(ServiceException):
    """Klasa błędu. Wyrzucana w przypadku błędu modułu Imap"""
    pass

CRLF = '\r\n'
"""Koniec linii."""

IMAP_PORT = 143
"""Standardowy numer portu IMAP."""

class Imap:
    
    """Klasa implementująca protokuł IMAP.
    
    Jej zadaniem jest wykonanie próby uwierzytelnienia.
    """
    
    def __init__(self, config):
        """Konstruktor.
        
        Argumenty:
        config -- słownik zawierający konfigurację 
        
        """
        self.hostname = config["hostname"]
        self.port = IMAP_PORT
        if "port" in config:
            self.port = config["port"]
        self.sleep = 0
        if "sleep" in config:
            self.sleep = config["sleep"]
        self.auth_info = 0
        if "auth-info" in config:
            self.auth_info = 1
            
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
        typ uwierzytelnienia bazujący na komendzie LOGIN.
        
        """
        s = self.__open()
        time.sleep(float(self.sleep))
        
        data_r = s.recv(1024)
        
        data_r = data_r.decode().split()[1]
        if (data_r != "OK"):
            raise ImapServiceException(_("Serwer nie jest gotowy"))
        
        data_r = 'A0001 LOGIN ' + username + ' ' + password + CRLF
        s.send(data_r)
        
        data_r = s.recv(1024)
        data_r = data_r.decode()
        statusPattern = re.compile(r'.*A0001 ([okno]{2}).*', re.IGNORECASE)
        status = statusPattern.search(data_r)
        if (status == None):
            raise ImapServiceException(_("Komunikacja nie przebiega prawidłowo"))
        
        if self.auth_info == "1":
            print data_r[:-2]
        
        res = status.groups()[0]
        if res == "OK":
            self.__close(s)
            return True
        else:
            self.__close(s)
            return False
        
        return False
        
def getOptionGroup(parser):
    """Zwraca pomoc dla grupy opcji."""
    group = OptionGroup(parser, _("Opcje dla modulu Imap"),
                        _("sleep=CZAS - odczekanie po polaczeniu, "
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
