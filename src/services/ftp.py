# -*- coding: utf-8 -*-

"""
Moduł obsługujący protokuł FTP.

Protokół ten jest dokładnie opisany w dokumencie RFC 959.
"""

import socket
import re
import time
from services.service import ServiceException
from optparse import OptionGroup

class FtpServiceException(ServiceException):
    """Klasa błędu. Wyrzucana w przypadku błędu modułu Ftp"""
    pass

FTP_PORT = 21
"""Standardowy numer portu FTP."""

class Ftp:
    
    """Klasa implementująca protokuł FTP.
    
    Jej zadaniem jest wykonanie próby uwierzytelnienia.
    """
    
    def __init__(self, config):
        """Konstruktor.
        
        Argumenty:
        config -- słownik zawierający konfigurację 
        
        """
        self.hostname = config["hostname"]
        self.port = FTP_PORT
        if "port" in config:
            self.port = config["port"]
        self.sleep = 0
        if "sleep" in config:
            self.sleep = config["sleep"]
            
    def __create_socket(self):
        """Zwraca stworzony socket."""
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def __open(self):
        """Otwiera socket."""
        sock = self.__create_socket()
        sock.connect((self.hostname, self.port))
        return sock
        
    def __close(self, sock):
        """Zamyka socket."""
        sock.close()
        
    def auth(self, username, password):
        """Wykonuje próbę uwierzytelnienia.
        
        W przypadku tego modułu wykonywane jest połączenie z serwerem i 
        wysłanie danych uwierzytelniających.
        
        """
        s = self.__open()
        
        time.sleep(float(self.sleep)) 
        
        data_r = s.recv(1024)
        
        statusPattern = re.compile(r'^(\d{3})*')
        data_r = data_r.decode()
        status = statusPattern.search(data_r).groups()[0]
        
        if (status != '220'):
            raise FtpServiceException(_("Niepoprawna komunikacja z serwerem"))
            
        username = "USER " + username + '\r\n'
        s.send(username)
        data_r = s.recv(1024)
        
        data_r = data_r.decode()
        status = statusPattern.search(data_r).groups()[0]
        
        if (status != '331'):
            raise FtpServiceException(_("Niepoprawna komunikacja z serwerem"))
        
        password = "PASS " + password + '\r\n'
        s.send(password)
        data_r = s.recv(1024)
        
        data_r = data_r.decode()
        status = statusPattern.search(data_r).groups()[0] 
        
        if (status == '230'):
            self.__close(s)
            return True
        else:
            self.__close(s)
            return False
        
def getOptionGroup(parser):
    """Zwraca pomoc dla grupy opcji."""
    group = OptionGroup(parser, _("Opcje dla modulu Ftp"),
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
