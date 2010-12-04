# -*- coding: utf-8 -*-

"""
Moduł obsługujący protokuł SMTP.

Protokół ten jest dokładnie opisany w dokumencie RFC 5321.
"""

import socket
import time
import re
import base64

from services.service import ServiceException
from optparse import OptionGroup

class SmtpServiceException(ServiceException):
    """Klasa błędu. Wyrzucana w przypadku błędu modułu Smtp"""
    pass

SMTP_PORT = 25
"""Standardowy numer portu SMTP."""

class Smtp:
    
    """Klasa implementująca protokuł SMTP.
    
    Jej zadaniem jest wykonanie próby uwierzytelnienia.
    """
    
    def __init__(self, config):
        """Konstruktor.
        
        Argumenty:
        config -- słownik zawierający konfigurację 
        
        """
        self.hostname = config["hostname"]
        self.port = SMTP_PORT
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
        typ uwierzytelnienia bazujący na komendach AUTH PLAIN.
        
        """
        s = self.__open()
        
        time.sleep(float(self.sleep)) 
        
        data_r = s.recv(1024)
        status = data_r.decode().split()[0]
        
        if (status != '220'):
            raise SmtpServiceException(_("Serwer nie jest gotowy"))
        
        my_hostname = 'EHLO ' + 'next' + ' \r\n'
        s.send(my_hostname)
        
        data_r = s.recv(1024)
        data_r = data_r.decode()
        
        statusPattern = re.compile(r'250-AUTH (\D*)')
        status = statusPattern.search(data_r)
        if (status == None):
            raise SmtpServiceException(_("Komunikacja nie przebiega prawidłowo"))
        
        auth_list = status.groups()[0]
        auth_list = auth_list.split()
        
        if ('PLAIN' in auth_list):
            enc_str = username + '\0' + username + '\0' + password
            
            enc = base64.standard_b64encode(enc_str)
            send_str = 'AUTH PLAIN ' + enc.decode() + ' \r\n'
            s.send(send_str)
     
            data_r = s.recv(1024)
            data_r = data_r.decode().split()[0]
            if (data_r != '235'):
                self.__close(s)
                return False
            else:
                self.__close(s)
                return True
        else:
            raise SmtpServiceException(_("Nie zaimplementowano tego typu uwierzytelnienia"))
        
        self.__close(s)
        return False
        
def getOptionGroup(parser):
    """Zwraca pomoc dla grupy opcji."""
    group = OptionGroup(parser, _("Opcje dla modulu Smtp"),
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
