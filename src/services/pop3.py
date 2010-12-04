# -*- coding: utf-8 -*-

"""
Moduł obsługujący protokuł POP3.

Protokół ten jest dokładnie opisany w dokumencie RFC 1939.
"""

import socket
import time
from services.service import ServiceException
from optparse import OptionGroup

class Pop3ServiceException(ServiceException):
    """Klasa błędu. Wyrzucana w przypadku błędu modułu Pop3"""
    pass

POP3_PORT = 110
"""Standardowy numer portu POP3."""

class Pop3:
    
    """Klasa implementująca protokuł POP3.
    
    Jej zadaniem jest wykonanie próby uwierzytelnienia.
    """
    
    def __init__(self, config):
        """Konstruktor.
        
        Argumenty:
        config -- słownik zawierający konfigurację 
        
        """
        self.hostname = config["hostname"]
        self.port = POP3_PORT
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
        typ uwierzytelnienia bazujący na komendach USER i PASS.
        
        """
        s = self.__open()
        
        time.sleep(float(self.sleep))
        
        data_r = s.recv(1024)
        welcome = data_r
        
        data_r = data_r.decode().split()[0]
        if (data_r == '-ERR'):
            print(welcome[:len(welcome) - 1])	    
            raise Pop3ServiceException(_("Serwer nie jest gotowy"))
        
        username = "USER " + username + '\r\n'
        s.send(username)
        data_r = s.recv(1024)
        
        data_r = data_r.decode().split()[0]
        if (data_r == '-ERR'):
            raise Pop3ServiceException(_("Komunikacja nie przebiega prawidłowo"))
        
        password = "PASS " + password + '\r\n'
        s.send(password)
        data_r = s.recv(1024)
        
        data_r = data_r.decode().split()[0]
        if (data_r == '-ERR'):
            self.__close(s)
            return False
        else:
            self.__close(s)
            return True
        
def getOptionGroup(parser):
    """Zwraca pomoc dla grupy opcji."""
    group = OptionGroup(parser, _("Opcje dla modulu Pop3"),
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
