# -*- coding: utf-8 -*-

"""
Moduł obsługujący protokuł SSH.

Protokół ten jest dokładnie opisany w dokumentach RFC 4250, RFC 4251, RFC 4252 i RFC 4253.
Kod tego modułu został stworzony na podstawie kodu biblioteki paramiko (http://www.lag.net/paramiko/), 
napisanej przez Robey Pointera <robeypointer@gmail.com> i udostępnionej na licencji LGPL.
Klasy które zawierają kod biblioteki paramiko to: DHGroup1, Transport i Packet.
"""

import socket
import string
import types
import struct
import random

from services.service import ServiceException
from optparse import OptionGroup

from Crypto.Cipher import DES3
from Crypto.Hash import SHA, HMAC

SSH_MSG_SERVICE_REQUEST = 5
SSH_MSG_SERVICE_ACCEPT = 6
SSH_MSG_KEXINIT = 20
SSH_MSG_NEWKEYS = 21
SSH_MSG_KEXDH_INIT = 30
SSH_KEXDH_REPLY = 31
SSH_MSG_USERAUTH_REQUEST = 50
SSH_MSG_USERAUTH_FAILURE = 51
SSH_MSG_USERAUTH_SUCCESS = 52

P = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381FFFFFFFFFFFFFFFFL
"""Wartość P w protokole Diffie–Hellman."""
G = 2
"""Wartość G w protokole Diffie–Hellman."""


END = '\r\n'
"""Koniec wiersza."""

SSH_PORT = 22
"""Standardowy numer portu w protokole SSH."""

class SshServiceException(ServiceException):
    """Klasa błędu. Wyrzucana w przypadku błędu modułu Ssh"""
    pass

class Ssh:
    
    """Klasa implementująca protokuł POP3.
    
    Jej zadaniem jest wykonanie próby uwierzytelnienia.
    """
    
    def __init__(self, config):
        """Konstruktor.
        
        Argumenty:
        config -- słownik zawierający konfigurację 
        
        """
        self.hostname = config["hostname"]
        self.port = SSH_PORT
        if "port" in config:
            self.port = config["port"]
            
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
        
        t = Transport(s)
        r = t.run(username, password)
        
        self.__close(s)
        return r
        
def getOptionGroup(parser):
    """Zwraca pomoc dla grupy opcji."""
    group = OptionGroup(parser, _("Opcje dla modulu Ssh"),
                        _(""))
    return group

def parseOptionGroup(option):
    """Parsuje ciąg opcji dodatkowych, zwraca dict."""
    config = {}
    option = option.split(",")
    for x in option:
        x = x.split("=")
        config[x[0]] = x[1]
        
    return config

def get_bytes(size):
    """Generuje string zawierajacy losowe liczby, zwraca string.
    
    Argumenty:
    size -- określa ilość danych które mają być wygenerowane
    
    """
    return "".join(chr(random.randrange(0, 256)) for x in xrange(size))

def parse_to_long(s):
    """Parsuje do wartości long, zwraca long.
    
    Argumenty:
    s -- string do sparsowania
    
    """
    out = 0L
    negative = 0
    if (len(s) > 0) and (ord(s[0]) >= 0x80):
        negative = 1
    if len(s) % 4:
        filler = '\x00'
        if negative:
            filler = '\xff'
        s = filler * (4 - len(s) % 4) + s
    for i in range(0, len(s), 4):
        out = (out << 32) + struct.unpack('>I', s[i:i + 4])[0]
    if negative:
        out -= (1L << (8 * len(s)))
    return out

def parse_from_long(n):
    """Parsuje do stringa, zwraca string.
    
    Argumenty:
    n -- long do sparsowania
    
    """
    s = ''
    n = long(n)
    while (n != 0) and (n != -1):
        s = struct.pack('>I', n & 0xffffffffL) + s
        n = n >> 32
    for i in enumerate(s):
        if (n == 0) and (i[1] != '\000'):
            break
        if (n == -1) and (i[1] != '\xff'):
            break
    else:
        i = (0,)
        if n == 0:
            s = '\000'
        else:
            s = '\xff'
    s = s[i[0]:]
    if (n == 0) and (ord(s[0]) >= 0x80):
        s = '\x00' + s
    if (n == -1) and (ord(s[0]) < 0x80):
        s = '\xff' + s
    return s

class DHGroup1:
    
    """Klasa implementująca protokuł wymiany kluczy Diffiego–Hellmana.
    Napisana z użyciem kodu modułu paramiko.
    """
    
    def __init__(self, transport):
        """Konsturktor.
        
        Argumenty:
        transport -- obiekt klasy Transport
        
        """
        self.transport = transport

    def kexdh_init(self):
        """Pierwsza faza wymiany."""
        self.x = random.getrandbits(128)
        self.e = pow(G, self.x, P)
        m = Packet()
        m.add_byte(chr(SSH_MSG_KEXDH_INIT))
        m.add_mpint(self.e)
        self.transport.send_packet(m)

    def kexdh_reply(self, m):
        """Odebranie odpowiedzi i zakończenie wymiany kluczy."""
        host_key = m.get_string()
        self.f = m.get_mpint()
        if (self.f < 1) or (self.f > P - 1):
            raise SshServiceException(_('Wartość kex "f" serwera jest poza zasięgiem'))
        sig = m.get_string()
        K = pow(self.f, self.x, P)
        hm = Packet().add_string(self.transport.local_version).add_string(self.transport.remote_version)
        hm.add_string(self.transport.local_kex_init).add_string(self.transport.remote_kex_init).add_string(host_key)
        hm.add_number(self.e).add_number(self.f).add_number(K)
        self.transport.set_K_H(K, SHA.new(str(hm)).digest())
        self.transport.encryption_out_start()

class Transport:
    
    """Klasa implementująca warstwę transportową protokołu SSH.
    Napisana z użyciem kodu modułu paramiko.
    """
    
    __VERSION = '2.0'
    """Wersja protokołu."""
    __CLIENT_ID = 'rjohn'
    """Nazwa klienta."""

    preferred_ciphers = [ '3des-cbc' ]
    """Preferowane klucze symetryczne."""
    preferred_macs = [ 'hmac-sha1' ]
    """Preferowane funkcje hashujące."""
    preferred_keys = [ 'ssh-dss' ]
    """Preferowane klucze asymetryczne."""
    preferred_kex = [ 'diffie-hellman-group1-sha1' ]
    """Preferowane algorytmy wymiany kluczy."""

    cipher_info = {
        '3des-cbc': { 'class': DES3, 'mode': DES3.MODE_CBC, 'block-size': 8, 'key-size': 24 },
        }

    mac_info = {
        'hmac-sha1': { 'class': SHA, 'size': 20 },
        }

    kex_info = {
        'diffie-hellman-group1-sha1': DHGroup1,
        }

    def __init__(self, sock):
        """Konstruktor.
        
        Argumenty:
        sock -- socket
        
        """
        self.sock = sock
        self.sock.settimeout(0.1)
        self.local_version = 'SSH-' + self.__VERSION + '-' + self.__CLIENT_ID
        self.remote_version = ''
        self.block_size_out = 8
        self.block_size_in = 8
        self.local_mac_len = 0
        self.remote_mac_len = 0
        self.engine_in = None
        self.engine_out = None
        self.local_cipher = ''
        self.remote_cipher = ''
        self.sequence_number_in = 0L
        self.sequence_number_out = 0L
        self.local_kex_init = None
        self.remote_kex_init = None
        self.session_id = None
        self.active = 0

    def close(self):
        """Kończy transmisję."""
        self.active = 0
        self.engine_in = self.engine_out = None
        self.sequence_number_in = self.sequence_number_out = 0L

    def is_active(self):
        """Określa czy transmisja jest aktywna."""
        return self.active

    def read(self, n):
        """Czyta z socketa dane.
        
        Argumenty:
        n -- ilość bajtów do przeczytania
        
        """
        out = ''
        while n > 0:
            try:
                x = self.sock.recv(n)
                if len(x) == 0:
                    raise EOFError()
                out += x
                n -= len(x)
            except socket.timeout:
                if not self.active:
                    raise EOFError()
        return out

    def write(self, out):
        """Zapisuje dane do socketa
        
        Argumenty:
        out -- dane do wysłania
        
        """
        while len(out) > 0:
            n = self.sock.send(out)
            if n <= 0:
                raise EOFError()
            if n == len(out):
                return
            out = out[n:]
        return

    def make_packet(self, payload):
        """Tworzy pakiet SSH.
        
        Argumenty:
        payload -- zawartość pakietu (dane)
        
        """
        bsize = self.block_size_out
        padding = 3 + bsize - ((len(payload) + 8) % bsize)
        packet = struct.pack('>IB', len(payload) + padding + 1, padding)
        packet += payload
        packet += get_bytes(padding)
        return packet

    def send_packet(self, data):
        """Wysyła pakiet.
        
        Funkcja w zależności od fazy protokołu, szyfruje dane i dodaje odpowiednie wartości.
        
        Argumenty:
        data -- dane do wysłania
        
        """
        
        packet = self.make_packet(str(data))
        if self.engine_out != None:
            out = self.engine_out.encrypt(packet)
        else:
            out = packet

        if self.engine_out != None:
            payload = struct.pack('>I', self.sequence_number_out) + packet
            out += HMAC.HMAC(self.mac_key_out, payload, self.local_mac_engine).digest()[:self.local_mac_len]
        self.sequence_number_out += 1L
        self.sequence_number_out %= 0x100000000L
        self.write(out)

    def read_packet(self):
        """Odczytuje pakiet.
        
        Funkcja przetwarza pakiet, wyciągają z niego dane. Jeżeli jest potrzeba odszyfrowuje je.
        
        """
        header = self.read(self.block_size_in)
        if self.engine_in != None:
            header = self.engine_in.decrypt(header)
        packet_size = struct.unpack('>I', header[:4])[0]

        leftover = header[4:]
        if (packet_size - len(leftover)) % self.block_size_in != 0:
            raise SshServiceException(_('Nieprawidłowa wielkość bloku w pakiecie'))
        buffer = self.read(packet_size + self.remote_mac_len - len(leftover))
        packet = buffer[:packet_size - len(leftover)]
        post_packet = buffer[packet_size - len(leftover):]
        if self.engine_in != None:
            packet = self.engine_in.decrypt(packet)
        packet = leftover + packet
        if self.remote_mac_len > 0:
            mac = post_packet[:self.remote_mac_len]
            mac_payload = struct.pack('>II', self.sequence_number_in, packet_size) + packet
            my_mac = HMAC.HMAC(self.mac_key_in, mac_payload, self.remote_mac_engine).digest()[:self.remote_mac_len]
            if my_mac != mac:
                raise SshServiceException(_('Nieprawidłowy MAC'))
        padding = ord(packet[0])
        payload = packet[1:packet_size - padding + 1]

        msg = Packet(payload[1:])
        msg.seqno = self.sequence_number_in
        self.sequence_number_in = (self.sequence_number_in + 1) & 0xffffffffL
                
        return ord(payload[0]), msg

    def set_K_H(self, k, h):
        """Ustawia wartości K i H."""
        self.K = k
        self.H = h
        if self.session_id == None:
            self.session_id = h

    def compute_key(self, id, nbytes):
        """Oblicza klucz."""
        m = Packet()
        m.add_mpint(self.K)
        m.add_bytes(self.H)
        m.add_byte(id)
        m.add_bytes(self.session_id)
        out = sofar = SHA.new(str(m)).digest()
        while len(out) < nbytes:
            m = Packet()
            m.add_mpint(self.K)
            m.add_bytes(self.H)
            m.add_bytes(sofar)
            hash = SHA.new(str(m)).digest()
            out += hash
            sofar += hash
        return out[:nbytes]
    
    def userauth_request(self, username, password):
        """Wysyła żądanie uwierzytelnienia."""
        self.username = username
        self.password = password
        m = Packet()
        m.add_byte(chr(SSH_MSG_SERVICE_REQUEST))
        m.add_string('ssh-userauth')
        self.send_packet(m)
    
    def parse_service_accept(self, m):
        """Obsługuje akceptacje żądania usługi."""
        service = m.get_string()
        if service == 'ssh-userauth':
            m = Packet()
            m.add_byte(chr(SSH_MSG_USERAUTH_REQUEST))
            m.add_string(self.username)
            m.add_string('ssh-connection')
            m.add_string('password')
            m.add_boolean(0)
            m.add_string(self.password.encode('UTF-8'))
            self.send_packet(m)
        else:
            raise SshServiceException("Niepoprawna odpowiedz na zadanie")

    def run(self, username, password):
        """Główna funkcja.
        
        Funkcja ta wykonuje poszczególne kroki protokołu w celu uwierzytelnienia.
        
        Argumenty:
        username -- nazwa użytkownika
        password -- hasło użytkownika
        
        """
        self.active = 1
        self.write(self.local_version + END)
        self.check_banner()
        self.send_kex_init()

        e_msg = _("Blad w protokole")

        ptype, m = self.read_packet()
        if ptype == SSH_MSG_KEXINIT:
            self.parse_kex_init(m)
            self.kex_engine.kexdh_init()
        else:
            raise SshServiceException(e_msg)

        ptype, m = self.read_packet()
        if ptype == SSH_KEXDH_REPLY:
            self.kex_engine.kexdh_reply(m)
        else:
            raise SshServiceException(e_msg)

        ptype, m = self.read_packet()
        if ptype == SSH_MSG_NEWKEYS:
            self.encryption_in_start()
        else:
            raise SshServiceException(e_msg)

        self.userauth_request(username, password)
            
        ptype, m = self.read_packet()
        if ptype == SSH_MSG_SERVICE_ACCEPT:
            self.parse_service_accept(m)
        else:
            raise SshServiceException(e_msg)
            
        ptype, m = self.read_packet()
        if ptype == SSH_MSG_USERAUTH_SUCCESS:
            self.close()
            return True
        else:
            self.close()
            return False

    def check_banner(self):
        """Funkcja ta sprawdza czy dane banera uzyskane od serwera są poprawne."""
        flag = False
        # 5 razy pobieram z serwera
        # 10 razy czekam na timeout przy polaczeniu
        for x in xrange(5):
            for y in xrange(10):
                try:
                    data_r = self.sock.recv(1024)
                    break
                except socket.timeout:
                    continue
                
            if data_r[:4] == 'SSH-':
                flag = True
                break

        msg_error = _('Nieprawidlowy protokol')

        if flag == False:
            raise SshServiceException(msg_error)

        data_r = data_r[:-2]
        self.remote_version = data_r

        index = data_r.find('-', 4)
        if index == -1:
            raise SshServiceException(msg_error)

        ver = data_r[4:index]
        if ver != "2.0":
            raise SshServiceException(_('Nieprawidłowa wersja'))

    def send_kex_init(self):
        """Funkcja wysyła pakiet inicjalizujący wymianę kluczy."""
        p = Packet()
        p.add_byte(chr(SSH_MSG_KEXINIT))
        p.add_bytes(get_bytes(16))
        p.add_list(self.preferred_kex)
        p.add_list(self.preferred_keys)
        p.add_list(self.preferred_ciphers)
        p.add_list(self.preferred_ciphers)
        p.add_list(self.preferred_macs)
        p.add_list(self.preferred_macs)
        p.add_list(['none'])
        p.add_list(['none'])
        p.add_string('')
        p.add_string('')
        p.add_boolean(0)
        p.add_int(0)

        self.local_kex_init = str(p)
        self.send_packet(p)

    def parse_kex_init(self, packet):
        """Funkcja parsuje pakiet inicjalizujący wymianę kluczy."""
        cookie = packet.get_bytes(16)
        kex_algo_list = packet.get_list()
        server_key_algo_list = packet.get_list()
        client_encrypt_algo_list = packet.get_list()
        server_encrypt_algo_list = packet.get_list()
        client_mac_algo_list = packet.get_list()
        server_mac_algo_list = packet.get_list()
        client_compress_algo_list = packet.get_list()
        server_compress_algo_list = packet.get_list()
        client_lang_list = packet.get_list()
        server_lang_list = packet.get_list()
        kex_follows = packet.get_boolean()
        unused = packet.get_int()

        error = _('Blad negocjacji kluczy')

        if (not('none' in client_compress_algo_list) or
            not('none' in server_compress_algo_list)):
            raise SshServiceException(error)

        self.kex_engine = self.preferred_kex[0]
        if not self.kex_engine in kex_algo_list:
            raise SshServiceException(error)
        self.kex_engine = self.kex_info[self.kex_engine](self)

        self.host_key_type = self.preferred_keys[0]
        if not self.host_key_type in server_key_algo_list:
            raise SshServiceException(error)

        self.local_cipher = self.preferred_ciphers[0]
        self.remote_cipher = self.preferred_ciphers[0]
        if not self.local_cipher in client_encrypt_algo_list:
            raise SshServiceException(error)
        if not self.remote_cipher in server_encrypt_algo_list:
            raise SshServiceException(error)

        self.local_mac = self.preferred_macs[0]
        self.remote_mac = self.preferred_macs[0]
        if not self.local_mac in client_mac_algo_list:
            raise SshServiceException(error)
        if not self.remote_mac in server_mac_algo_list:
            raise SshServiceException(error)

        self.remote_kex_init = chr(SSH_MSG_KEXINIT) + packet.get_so_far()

    def encryption_in_start(self):
        """Funkcja inicjalizuje algorytmy szyfrowania dla danych wejściowych."""
        self.block_size_in = self.cipher_info[self.remote_cipher]['block-size']
        IV_in = self.compute_key('B', self.block_size_in)
        key_in = self.compute_key('D', self.cipher_info[self.remote_cipher]['key-size'])
        self.engine_in = self.cipher_info[self.remote_cipher]['class'].new(key_in, self.cipher_info[self.remote_cipher]['mode'], IV_in)
        self.remote_mac_len = self.mac_info[self.remote_mac]['size']
        self.remote_mac_engine = self.mac_info[self.remote_mac]['class']
        self.mac_key_in = self.compute_key('F', self.remote_mac_engine.digest_size)

    def encryption_out_start(self):
        """Funkcja inicjalizuje algorytmy szyfrowania dla danych wyjściowych."""
        m = Packet()
        m.add_byte(chr(SSH_MSG_NEWKEYS))
        self.send_packet(m)
        
        self.block_size_out = self.cipher_info[self.local_cipher]['block-size']
        IV_out = self.compute_key('A', self.block_size_out)
        key_out = self.compute_key('C', self.cipher_info[self.local_cipher]['key-size'])
        self.engine_out = self.cipher_info[self.local_cipher]['class'].new(key_out, self.cipher_info[self.local_cipher]['mode'], IV_out)
        self.local_mac_len = self.mac_info[self.local_mac]['size']
        self.local_mac_engine = self.mac_info[self.local_mac]['class']
        self.mac_key_out = self.compute_key('E', self.local_mac_engine.digest_size)

class Packet:
    
    """Klasa definiująca pakiet w protokole SSH.
    Napisana z użyciem kodu modułu paramiko.
    """
    
    def __init__(self, content=''):
        """Konstruktor.
        
        Argumenty:
        content -- zawartość pakietu
        
        """
        self.packet = content
        self.idx = 0
        self.seqno = -1

    def __str__(self):
        """Zwraca zawartość pakietu."""
        return self.packet

    def get_so_far(self):
        """Zwraca wszystkie bajty."""
        return self.packet[:self.idx]

    def get_bytes(self, n):
        """Zwraca określoną liczbę bajtów.
        
        Argumenty:
        n -- liczba bajtów do zwrócenia
        
        """
        if self.idx + n > len(self.packet):
            return '\x00' * n
        b = self.packet[self.idx:self.idx + n]
        self.idx = self.idx + n
        return b
    
    def get_byte(self):
        """Zwraca bajt."""
        return self.get_bytes(1)

    def get_boolean(self):
        """Zwraca wartość logiczną."""
        b = self.get_bytes(1)
        if b == '\x00':
            return 0
        else:
            return 1

    def get_int(self):
        """Zwraca wartość całkowitą."""
        x = self.packet
        i = self.idx
        if i + 4 > len(x):
            return 0
        n = struct.unpack('>I', x[i:i + 4])[0]
        self.idx = i + 4
        return n

    def get_mpint(self):
        """Zwraca wartość long."""
        return parse_to_long(self.get_string())

    def get_string(self):
        """Zwraca string."""
        l = self.get_int()
        if self.idx + l > len(self.packet):
            return ''
        str = self.packet[self.idx:self.idx + l]
        self.idx = self.idx + l
        return str

    def get_list(self):
        """Zwraca listę."""
        str = self.get_string()
        l = string.split(str, ',')
        return l

    def add_bytes(self, b):
        """Dodaje bajty."""
        self.packet = self.packet + b
        return self

    def add_byte(self, b):
        """Dodaje bajt."""
        self.packet = self.packet + b
        return self

    def add_boolean(self, b):
        """Dodaje wartość logiczną."""
        if b:
            self.add_byte('\x01')
        else:
            self.add_byte('\x00')
        return self
            
    def add_int(self, n):
        """Dodaje wartość całkowitą."""
        self.packet = self.packet + struct.pack('>I', n)
        return self

    def add_mpint(self, z):
        """Dodaje wartość long."""
        self.add_string(parse_from_long(z))
        return self

    def add_string(self, s):
        """Dodaje string."""
        self.add_int(len(s))
        self.packet = self.packet + s
        return self

    def add_list(self, l):
        """Dodaje listę."""
        out = string.join(l, ',')
        self.add_int(len(out))
        self.packet = self.packet + out
        return self

    def add_number(self, n):
        """Dodaje liczbę."""
        if type(n) == types.LongType:
            if n > 0xffffffffL:
                return self.add_mpint(n)
            else:
                return self.add_int(n)
        else:
            self.add_int(n)
            
            
