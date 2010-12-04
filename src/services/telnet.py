# -*- coding: utf-8 -*-

"""
Moduł obsługujący protokuł TELNET.

Protokół ten jest dokładnie opisany w dokumentach RFC 854 i RFC 855.
"""

import socket
import time

from services.service import ServiceException
from optparse import OptionGroup

class TelnetServiceException(ServiceException):
    """Klasa błędu. Wyrzucana w przypadku błędu modułu Telnet"""
    pass

IAC = chr(255)
DONT = chr(254)
DO = chr(253)
WONT = chr(252)
WILL = chr(251)
theNULL = chr(0)

TELNET_PORT = 23
"""Standardowy numer portu TELNET."""

class Telnet:
    
    """Klasa implementująca protokuł TELNET.
    
    Jej zadaniem jest wykonanie próby uwierzytelnienia.
    """
    
    def __init__(self, config):
        """Konstruktor.
        
        Argumenty:
        config -- słownik zawierający konfigurację 
        
        """
        self.hostname = config["hostname"]
        self.port = TELNET_PORT
        if "port" in config:
            self.port = config["port"]
        self.sleep = 0
        if "sleep" in config:
            self.sleep = config["sleep"]
            
        self.access = b"Last login"
        if "access" in config:
            self.access = bytes(config["access"], encoding='ascii')
        self.deny = b"Login incorrect"
        if "deny" in config:
            self.deny = bytes(config["deny"], encoding='ascii')
            
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
        
    def __getDataFromSocket(self, socket, buffor):
        """Pobiera dane z socketa i dopisuje do buufora.
        
        Argumenty:
        socket -- socket z którego zostaną pobrane dane
        buffor -- bufor do którego zostaną dopisane pobrane dane
        
        """
        data_r = socket.recv(1)
        return buffor + data_r

    def auth(self, username, password):
        """Wykonuje próbę uwierzytelnienia.
        
        W przypadku tego modułu wykonywane jest połączenie z serwerem i 
        wysłanie danych uwierzytelniających.
        
        """
        s = self.__open()
        time.sleep(float(self.sleep)) 
        
        buffor = ''
        data_buffor = ''
        index = 0
        
        login_flag = False
        pass_flag = False
        
        buffor = self.__getDataFromSocket(s, buffor)
        
        while buffor:
            if index >= len(buffor):
                buffor = self.__getDataFromSocket(s, buffor)
            
            if buffor[index] == IAC:
                index += 1
                continue
            
            if buffor[index] in (DO, DONT):
                buffor = self.__getDataFromSocket(s, buffor)
                opt = buffor[index + 1]
                res = IAC + WONT + opt
                s.sendall(res)
                index += 2
                continue
                
            if buffor[index] in (WILL, WONT):
                buffor = self.__getDataFromSocket(s, buffor)
                opt = buffor[index + 1]
                res = IAC + DONT + opt
                s.sendall(res)
                index += 2
                continue
            
            data_buffor += buffor[index]
            
            if pass_flag == True and login_flag == True and data_buffor.find(self.deny) != -1:
                self.__close(s)
                return False
            
            if pass_flag == True and login_flag == True and data_buffor.find(self.access) != -1:
                self.__close(s)
                return True
                
            if data_buffor.lower().find(b'password') != -1 and pass_flag == False:
                res = password + "\n"
                s.sendall(res)
                pass_flag = True
            
            if data_buffor.lower().find(b'login') != -1 and login_flag == False:
                res = username + "\n"
                s.sendall(res)
                login_flag = True
                
            index += 1
        
        self.__close(s)
        return False
        
def getOptionGroup(parser):
    """Zwraca pomoc dla grupy opcji."""
    group = OptionGroup(parser, _("Opcje dla modulu Telnet"),
                        _("sleep=CZAS - odczekanie po polaczeniu, "
                          "access=STRING - string identyfikujacy poprawne zalogowanie, "
                          "deny=STRING - string identyfikujacy niepoprawne zalogowanie"))   
    return group

def parseOptionGroup(option):
    """Parsuje ciąg opcji dodatkowych, zwraca dict."""
    config = {}
    option = option.split(",")
    for x in option:
        x = x.split("=")
        config[x[0]] = x[1]
        
    return config
