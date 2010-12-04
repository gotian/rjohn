
"""
Modul zarzadzajacy konfiguracja.
"""

import optparse

digit = "0123456789"
alnum = "abcdefghijklmnoprstuwzxqABCDEFGHIJKLMNOPRSTUWZXQ0123456789"
alpha = "abcdefghijklmnoprstuwzxqABCDEFGHIJKLMNOPRSTUWZXQ"

class Configuration:
    
    """Klasa konfiguracji.

    Zawiera ona metody parsujace dane z wiesza polecen. 
    """

    def __init__(self):
        """Konstruktor."""
        self.__config = {}
        
        self.__config["session_attack"] = 'session_attack.dump'
        self.__config["session_queue1"] = 'session_queue1.dump'
        self.__config["session_queue2"] = 'session_queue2.dump'
        self.__config["session_config"] = 'session_config.dump'
        self.__config["logfilename"] = 'rjohn.log'
    
    def parseOpt(self, options):
        """Przetwarza argumenty wiersza polecen, zwraca slownik zawierajacy konfiguracje.

        Funkcja ta sprawdza jakie zostaly podane dane wejsciowe, ustawia odpowienia wartosci domyslne i 
        zwraca odpowiednie wartosci w slowniku.
		
        Argumenty:
        options -- opcje przetworzone przez standardowe narzedzia

        """
        self.__config["thread_number"] = options.thread_number
        self.__config["verbose"] = options.verbose
        self.__config["log_level"] = options.log_level
        self.__config["info_time"] = options.info_time
        self.__config["between_time"] = options.between_time
        self.__config["retry_time"] = options.retry_time
        self.__config["username"] = options.username
        self.__config["userlist"] = options.userlist
        self.__config["wordrules"] = options.wordrules
        self.__config["retry_trials"] = options.retry_trials
        self.__config["save_time"] = options.session_save
        
        if options.result_file is None:
            self.__config["result_file"] = "result-file.txt"
        else:
            self.__config["result_file"] = options.result_file
            
        if options.between_time != 0:
            self.__config["thread_number"] = 1
        
        if options.wordlist is None and options.incremental == False:
            self.__config["wordlist"] = "wordlist.txt"
            if options.wordrules is None:
                self.__config["wordrules"] = "wordrules.txt"
            if options.username is None:
                self.__config["username"] = None
            if options.userlist is None:
                self.__config["userlist"] = "userlist.txt"
            return self.__config
            
        if options.username is None and options.userlist is None:
            self.__config["userlist"] = "userlist.txt"
            
        if not options.wordlist is None:
            self.__config["wordlist"] = options.wordlist
        else:
            self.__config["chars_min"] = options.chars_min
            self.__config["chars_max"] = options.chars_max
            if options.chars_list is None:
                self.__config["chars_list"] = alnum
            else:
                self.__config["chars_list"] = options.chars_list
            
        return self.__config     
        
    def getOpt(self):
        """Zwraca obiekt ktory bedzie wyswietlany jako pomoc programu.
    
    	Funkcja ta korzystajac ze standardowych mechanizmow tworzy pomoc programu.
    	
    	"""
        parser = optparse.OptionParser()
        usage_raw = _("[opcje] usluga nazwa_hosta [port]")
        usage = "%prog " + usage_raw
        parser.usage = usage
        
        msg1 = _("USLUGA")
        msg2 = _("PLIK")
        msg3 = _("LANCUCH")
        msg4 = _("LICZBA")
        msg5 = _("SEKUNDY")
        msg6 = _("domyslnie")
        msg7 = " [" + msg6 + ": %default]"
        
        parser.add_option("-m", "--service-help", action="store", metavar=msg1,
                          help=_("wypisuje dodatkowe informacja na temat uslugi"))
        parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                          default=False, help=_("tryb gadatliwy") + msg7)
        parser.add_option("-q", "--quiet", action="store_false", dest="verbose",
                          help=_("tryb cichy"))
        parser.add_option("-w", "--wordlist", metavar=msg2,
                          help=_("plik wejsciowy z lista slow (tryb slownikowy)"))
        parser.add_option("-r", "--wordrules", metavar=msg2,
                          help=_("plik wejsciowy z lista regul dla slow"))
        parser.add_option("-u", "--username", metavar=msg3,
                          help=_("pojedyncza nazwa uzytkownika dla ktorego bedzie przeprowadzany atak"))
        parser.add_option("-l", "--userlist", metavar=msg2,
                          help=_("plik wejsciowy z lista uzytkownikow"))
        parser.add_option("-i", "--incremental", action="store_true",
                          default=False, help=_("tryb silowy") + msg7)
        parser.add_option("-c", "--chars-list", metavar=msg3,
                          help=_("lista znakow dla trybu silowego"))
        parser.add_option("-n", "--chars-min", type="int", default=1, metavar=msg4,
                          help=_("definiuje minimalna liczbe znakow dla trybu silowego") + msg7)
        parser.add_option("-x", "--chars-max", type="int", default=8, metavar=msg4,
                          help=_("definiuje maksymalna liczbe znakow dla trybu silowego") + msg7)
        parser.add_option("-t", "--thread-number", type="int", default=2, metavar=msg4,
                          help=_("liczba pracujacych watkow") + msg7)
        parser.add_option("-e", "--restore", action="store_true",
                          default=False, help=_("odzyskiwanie sesji") + msg7)
        parser.add_option("-o", "--service-options", metavar=msg3,
                          help=_("definiuje dodatkowe opcje dla uslugi"))
        parser.add_option("-g", "--log-level", type="int", default=20, metavar=msg4,
                          dest="log_level", help=_("definiuje poziom logowania") + msg7)
        parser.add_option("-f", "--info-time", metavar=msg5, type="float", default=0.0,
                          help=_("czas po ktorym status zostanie wypisany na stdout") + msg7)
        parser.add_option("-b", "--between-time", metavar=msg5, type="float", default=0.0,
                          help=_("czas pomiedzy kolejnymi probami uwierzytelnienia, "
                          "wymusza liczbe watkow rowna 1") + msg7)
        parser.add_option("-y", "--retry-time", metavar=msg5, type="float", default=0.0,
                          help=_("czas pomiedzy kolejnymi probami uwierzytelnienia, "
                          "w przypadku bledu") + msg7)
        parser.add_option("-s", "--retry-trials", metavar=msg4, type="int", default=3,
                          help=_("liczba prob w przypadku bledu") + msg7)
        parser.add_option("-d", "--result-file", metavar=msg2,
                          help=_("nazwa pliku z wynikami"))
        parser.add_option("-j", "--session-save", metavar=msg5, type="float", default=30.0,
                          help=_("czas po ktorym sesja zostanie automatycznie zapisana") + msg7)
        
        return parser
    
    def getConfig(self):
        """Zwraca slownik z konfiguracja."""
        return self.__config
    

