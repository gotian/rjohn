
"""
Modul testujacy moduly z pakietu services.
"""

import unittest
from services.imaps import Imaps
from services.ftp import Ftp
from services.pop3 import Pop3
from services.pop3s import Pop3s
from services.smtp import Smtp
from services.smtps import Smtps
from services.telnet import Telnet
from services.http import Http
from services.https import Https
from services.ssh import Ssh

class Test(unittest.TestCase):
    """Klasa testow jednostkowych."""

    def testImaps(self):
        "Test protokolu IMAP."
        s = Imaps({"hostname" : "imap.gmail.com"})
        
        result = s.auth("testprogramu1", "testprogramu")
        self.assertTrue(result)
        
        result = s.auth("testprogramu1", "testprogramu1")
        self.assertFalse(result)
        
    def testFtp(self):
        "Test protokolu FTP."
        s = Ftp({"hostname" : "ftp.belnet.be", "sleep" : 3})
        
        result = s.auth("anonymous", "wp@wp.pl")
        self.assertTrue(result)
        
        result = s.auth("alamakota", "wp@wp.pl")
        self.assertFalse(result)
        
    def testPop3(self):
        "Test protokolu POP3."
        s = Pop3({"hostname" : "poczta.o2.pl"})
        
        result = s.auth("testprogramu1", "testprogramu")
        self.assertTrue(result)
        
        result = s.auth("testprogramu1", "testprogramu1")
        self.assertFalse(result)
        
    def testPop3s(self):
        "Test protokolu POP3S."
        s = Pop3s({"hostname" : "poczta.o2.pl"})
        
        result = s.auth("testprogramu1", "testprogramu")
        self.assertTrue(result)
        
        result = s.auth("testprogramu1", "testprogramu1")
        self.assertFalse(result)
        
    def testSmtp(self):
        "Test protokolu SMTP."
        s = Smtp({"hostname" : "poczta.o2.pl"})
        
        result = s.auth("testprogramu1", "testprogramu")
        self.assertTrue(result)
        
        result = s.auth("testprogramu1", "testprogramu1")
        self.assertFalse(result)
        
    def testSmtps(self):
        "Test protokolu SMTPS."
        s = Smtps({"hostname" : "poczta.o2.pl"})
        
        result = s.auth("testprogramu1", "testprogramu")
        self.assertTrue(result)
        
        result = s.auth("testprogramu1", "testprogramu1")
        self.assertFalse(result)
        
    def testTelnet(self):
        "Test protokolu TELNET."
        s = Telnet({"hostname" : "localhost"})
        
        result = s.auth("test", "test")
        self.assertTrue(result)
        
        result = s.auth("testprogramu1", "testprogramu1")
        self.assertFalse(result)
        
    def testHttp(self):
        "Test protokolu HTTP."
        s = Http({"hostname" : "http://localhost/test"})
        
        result = s.auth("marcin", "marcin")
        self.assertTrue(result)
        
        result = s.auth("testprogramu1", "testprogramu1")
        self.assertFalse(result)
        
    def testHttps(self):
        "Test protokolu HTTPS."
        s = Https({"hostname" : "http://localhost/test"})
        
        result = s.auth("marcin", "marcin")
        self.assertTrue(result)
        
        result = s.auth("testprogramu1", "testprogramu1")
        self.assertFalse(result)
        
    def testSsh(self):
        "Test protokolu SSH."
        s = Ssh({"hostname" : "localhost"})
        
        result = s.auth("test", "test")
        self.assertTrue(result)
        
        result = s.auth("testprogramu1", "testprogramu1")
        self.assertFalse(result)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testImaps']
    unittest.main()
