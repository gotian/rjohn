# -*- coding: utf-8 -*-

"""
Główny moduł programu.

Przetwarza on argumenty programu, obsługuje uruchomienie wątków, 
pracę programu i jego zakończenie.
"""

import Queue
from utils.container import Container, FileContainer
from combinatorics.variation import RangeStringVariation
from utils.transition import Transition
import attack
import time
import pickle
import sys
import signal
from utils.configuration import Configuration
import threading
import logging
from datetime import datetime

def kill_handle(signum, frame):
    """Wymusza zakończenie programu, zwraca None.
    
    Funkcja obsługuje sygnały, po dostaniu których kończy działanie programu.
    Nie zapisuje ona sesji, ale czeka na jej zakończenie.
    
    """
    msg1 = _("Funkcja obsługi sygnałów wywołana z sygnałem: %d" % signum)
    msg2 = _("rjohn zakończył pracę")
    if verbose:
        print(msg1)
        print(datetime.today().isoformat(' ') + ": " + msg2)
        
    # czekanie na zapis sesji
    if event.is_set():
        wait_t = 60
        msg3 = _("Czekanie %d sekund na zapis sesji" % wait_t)
        print(msg3)
        for x in xrange(wait_t):
            time.sleep(1)
            if not event.is_set():
                break
    
    log.debug(msg1 + str(signum))
    log.info(datetime.today().isoformat(' ') + ": " + msg2)
    
    # po nacisnieciu ctrl+c zakanczenie programu bez zapisywania sesji
    sys.exit()

def save_handle(event):
    """Obsługuje wywołanie zapisania sesji, zwraca None.
    
    Funkcja sprawdza czy sesja jest zapisywana, jeżeli tak to czeka. Jeżeli nie to 
    zapisuje ją, a w przypadku powodzenia odzyskuje właśnie zapisaną.
    
    Argumenty:
    event -- Event informujący czy sesja jest zapisywana
    
    """
    global timer
    
    # jezeli jakis watek zapisuje juz sesje to zaczekac
    if event.is_set():
        wait_t = 60
        for x in xrange(wait_t):
            time.sleep(1)
            if not event.is_set():
                break    
    if event.is_set():
        return
    
    # blokowanie dostępu dla innych wątków
    event.set()
    
    # wyłączenie timera wypisującego status
    p_timer.cancel()
        
    r = save_session()
    if r == True:  
        restore_session()
    
    # ponowne ustawienie timera zapisujacego sesje
    timer = threading.Timer(config["save_time"], save_handle, [event])
    timer.setDaemon(True)
    timer.start() 
        
    event.clear()

def save_session():
    """Zapisuje sesje, zwraca boolean.
    
    Funkcja wykonuje zapis sesji, kończąc pracujące wątki, a następnie 
    zwrzucając do pliku dane programu. Jeżeli zapis się powiedzie to funkcja 
    zwraca True, w przeciwnym wypadku False.
    
    """
    msg1 = _("zapisanie sesji")
    if verbose:
        print(datetime.today().isoformat(' ') + ": " + msg1)
    log.debug(datetime.today().isoformat(' ') + ": " + msg1)
    
    p.stop()
    
    # sprawdzenie czy watki konsumentow sa aktywne
    flag = False
    for x in c_list:
        if x.is_alive():
            flag = True
    
    # jezeli sa to ich zatrzymanie
    if flag:
        try:
            p.stopChilds()
        except Queue.Full:
            msg2 = _("zapisanie sesji się nie powiodło")
            if verbose:
                print(datetime.today().isoformat(' ') + ": " + msg2)
            log.warning(datetime.today().isoformat(' ') + ": " + msg2)
            return False
    
    for x in c_list:
        while x.isActive():
            time.sleep(1)
    
    # Attack
    file = open(session_filename_1, 'wb')
    pickle.dump(p.getAttack(), file, pickle.HIGHEST_PROTOCOL)
    file.close()
    
    # Q1
    l_q = []
    while not Q1.empty():
        t = Q1.get()
        if not isinstance(t, bool):
            l_q.append(t)
        
    file = open(session_filename_2, 'wb')
    pickle.dump(l_q, file, pickle.HIGHEST_PROTOCOL)
    file.close()
        
    # Q2
    l_q = []
    while not Q2.empty():
        l_q.append(Q2.get())
        
    file = open(session_filename_3, 'wb')
    pickle.dump(l_q, file, pickle.HIGHEST_PROTOCOL)
    file.close()
    
    # config
    file = open(session_filename_4, 'wb')
    pickle.dump(config, file, pickle.HIGHEST_PROTOCOL)
    file.close()
    
    return True

def restore_session():
    """Odzyskuje sesje, zwraca None.
    
    Funkcja odczytuje z plików zapisane przez program dane i tworzy z 
    nich obiekty w programie.
    
    """
    global p, c_list, Q1, Q2, config, verbose, log, p_timer
    
    # Attack
    file = open(session_filename_1, 'rb')
    att = pickle.load(file)
    file.close()
    
    # Kolejka Q1
    file = open(session_filename_2, 'rb')
    l_q1 = pickle.load(file)
    file.close()
    
    # Kolejka Q2
    file = open(session_filename_3, 'rb')
    l_q2 = pickle.load(file)
    file.close()
    
    # Config
    file = open(session_filename_4, 'rb')
    config = pickle.load(file)
    file.close()
    
    verbose = config["verbose"]
    logfilename = config["logfilename"]
    logging.basicConfig(filename=logfilename, level=config["log_level"])
    log = logging.getLogger("main")
    
    Q1 = Queue.Queue(config["thread_number"] * 2)
    Q2 = Queue.Queue()
    
    att.Q1 = Q1
    att.Q2 = Q2
    
    for x in l_q1:
        Q1.put(x)
        
    for x in l_q2:
        Q2.put(x)
    
    start_threads(att, False)

def start_threads(att, flag):
    """Startuje wątki konsumentów i producenta, zwraca None.
    
    Funkcja tworzy obiekty konieczne do ataku i startuje wątki producentów i 
    konsumentów. Jest ona wywoływana zarówno przy ozyskiwaniu sesji, jak i przy 
    nowym uruchomieniu programu.
    
    Argumenty:
    att -- obiekt klasy Attack
    flag -- informacja o tym czy rozpocząć atak od początku czy kontynuować poprzedni
    
    """
    global c_list, p, p_timer
    try:
        c_list = start_consumers(config)
    except ImportError:
        msg1 = _("Nie ma takiej usługi (modułu): ")
        log.error(msg1 + config["service"])
        parser.error(msg1 + config["service"])
        
    msg2 = _("Wątki konsumentów wystartowały")
    if verbose:
        print(msg2)
    log.debug(msg2)
        
    p_event = threading.Event()
    p_event.clear()
    p_timer = threading.Timer(config["info_time"], print_status, [p_event])
    p_timer.setDaemon(True)
    if config["info_time"] != 0:
        p_timer.start() 
    
    p = attack.Producer(att, p_event)
    p.setDaemon(True)
    
    # restore czy normalne uruchomienie
    if flag:
        p.reset()
    p.start()
    
    msg3 = _("Wątek producenta wystartował")
    if verbose:
        print(msg3)
    log.debug(msg3)

def get_service_class(config):
    """Zwraca klasę usługi.
    
    Funkcja wyszukuje w pakiecie nazwę modułu i zwraca jego klasę.
    
    Argymenty:
    config -- słownik zawierający konfigurację
    
    """
    module_name = config["service"].lower()
    protocol = __import__('services.' + module_name, globals={}, locals={}, fromlist='services')
    service_class = getattr(protocol, module_name.capitalize())
    
    return service_class(config)

def get_opts_from_service(module_name_in):
    """Zwraca funkcję getOptionGroup modułu.
    
    Funkcja wyszukuje w pakiecie nazwę modułu i zwraca funkcję, która zawiera 
    informacje o pomocy klasy zawartej w tym module.
    
    Argumenty:
    module_name_in -- nazwa modułu z którego ma być pobrana funkcja
    
    """
    module_name = module_name_in.lower()
    protocol = __import__('services.' + module_name, globals={}, locals={}, fromlist='services')
    service_m = getattr(protocol, "getOptionGroup")
    return service_m

def parse_opts_by_service(module_name_in):
    """Zwraca funkcję parseOptionGroup modułu.
    
    Funkcja wyszukuje w pakiecie nazwę modułu i zwraca funkcję, która służy 
    do parsowania argumentów programu dla klasy zawartej w tym module.
    
    Argumenty:
    module_name_in -- nazwa modułu z którego ma być pobrana funkcja    
    
    """
    module_name = module_name_in.lower()
    protocol = __import__('services.' + module_name, globals={}, locals={}, fromlist='services')
    service_m = getattr(protocol, "parseOptionGroup")
    return service_m
    
def start_consumers(config):
    """Startuje wątki konsumentów, zwraca list.
    
    Funkcja startuje wątki konsumentów i zwraca listę tych wątków.
    
    Argumenty:
    config -- słownik zawierający konfigurację
    
    """
    c_list = []
    for x in range(config["thread_number"]):
        s = get_service_class(config)
        c = attack.Consumer(s, Q1, Q2, config)
        c.setDaemon(True)
        c.start()
        c_list.append(c)
        
    return c_list

def main():
    """Obsługuje pętlę czekającą na zakończenie ataku, zwraca None.
    
    Funkcja czeka w pętlia na zkończenie wątków, a następnie pobiera dane o 
    wynikach ataku i zapisuje je do pliku.
    
    """
    global timer, p, c_list, Q1, Q2, event
    
    signal.signal(signal.SIGINT, kill_handle)
    event = threading.Event()
    event.clear()
    timer = threading.Timer(config["save_time"], save_handle, [event])
    timer.setDaemon(True)
    timer.start() 
    
    while True:
        flag = False
        for x in c_list:
            if x.isActive():
                flag = True
                
        if not event.is_set() and not p.isAlive():
            break
        
        if not event.is_set() and flag == False:
            break
        
        time.sleep(1)
        
    timer.cancel()
    
    # sprawdzenie czy watki konsumentow sa aktywne
    flag = False
    for x in c_list:
        if x.is_alive():
            flag = True
    
    # jezeli sa to ich zatrzymanie
    if flag:
        try:
            p.stopChilds()
        except Queue.Full:
            pass
        
    for x in c_list:
        while x.is_alive():
            time.sleep(1)
     
    result = p.getAttack().getResult()
        
    while True:
        try:
            a, b = Q2.get_nowait()
        except:
            break
        result[a] = b
        
    writeResultToFile(result)
    
    if len(result) == 0:
        print _("Wyniki:"), "brak"
    else:
        print(_("Wyniki:"))
    for x in result:
        print(x, result[x])

def writeResultToFile(result):
    """Zapisuje wyniki do pliku, zwraca None.
    
    Funkcja zapisuje w odpowiednim formacie informacje o wykonaniu ataku do pliku.
    
    Argumenty:
    result -- lista zawierająca wyniki ataku
    
    """
    out_file = open(config["result_file"], 'a')
    if not "port" in config:
        port = "STANDARD"
    else:
        port = str(config["port"])
    
    for x in result:
        out_file.write(datetime.today().isoformat(' ') + ": " + config["service"] + " " + 
                        config["hostname"] + ":" + port + " " + x + " " + result[x] + "\n")
    out_file.close()
 
def print_status(event):
    """Wypisuje aktualnie przetwarzaną przez program parę login i hasło, zwraca None.
    
    Argumenty:
    event -- zdarzenie informujące moduł attack o wypisaniu informacji
    
    """
    event.set()
    
    p_timer = threading.Timer(config["info_time"], print_status, [event])
    p_timer.setDaemon(True)
    if config["info_time"] != 0:
        p_timer.start() 

if __name__ == '__main__':    
    configUtils = Configuration()
    parser = configUtils.getOpt()
    
    session_filename_1 = configUtils.getConfig()["session_attack"]
    session_filename_2 = configUtils.getConfig()["session_queue1"]
    session_filename_3 = configUtils.getConfig()["session_queue2"]
    session_filename_4 = configUtils.getConfig()["session_config"]
    
    (options, args) = parser.parse_args()
    if options.restore == True:
        restore_session()
        msg = _("Odzyskanie sesji")
        if verbose:
            print(datetime.today().isoformat(' ') + ": " + msg)
        log.info(datetime.today().isoformat(' ') + ": " + msg)
        main()
        sys.exit()
    
    if not options.service_help is None:
        s = get_opts_from_service(options.service_help)
        group = s(parser)
        parser.add_option_group(group)
        parser.print_help(sys.stdout)
        sys.exit()
    
    if len(args) < 2:
        parser.error(_("Niepoprawna liczba argumentów"))
        
    msg = _("Niepoprawny tryb")
    if not options.wordlist is None and options.incremental == True:
        parser.error(msg) 
        
    if not options.wordrules is None and options.incremental == True:
        parser.error(msg)
        
    if not options.username is None and not options.userlist is None:
        parser.error(msg) 
        
    config = configUtils.parseOpt(options)
    config["service"] = args[0]
    config["hostname"] = args[1]
    if len(args) == 3:
        config["port"] = eval(args[2])
        
    verbose = config["verbose"]
        
    logfilename = config["logfilename"]
    logging.basicConfig(filename=logfilename, level=config["log_level"])
    log = logging.getLogger("main")
    
    msg = _("rjohn rozpoczął pracę")
    msg2 = _("Cel ataku: ")
    if verbose:
        print(datetime.today().isoformat(' ') + ": " + msg)
        print(msg2 + config["service"] + " " + config["hostname"])
    log.info(datetime.today().isoformat(' ') + ": " + msg)
    log.info(msg2 + config["service"] + " " + config["hostname"])

    if not config["wordrules"] is None:
        try:
            wcr = FileContainer(config["wordrules"])
        except IOError:
            msg = _("Nieprawidłowy plik z zestawem reguł dla słów: ")
            log.error(msg + config["wordrules"])
            parser.error(msg + config["wordrules"])
    else:
        wcr = Container([":"])

    if not config["username"] is None:
        uc = Container([config["username"]])
    else:
        try:
            uc = FileContainer(config["userlist"])
        except IOError:
            msg = _("Nieprawidłowy plik z listą użytkowników: ")
            log.error(msg + config["userlist"])
            parser.error(msg + config["userlist"])
        
    if "wordlist" in config:
        try:
            wc = FileContainer(config["wordlist"])
        except IOError:
            msg = _("Nieprawidłowy plik z listą słów: ")
            log.error(msg + config["wordlist"])
            parser.error(msg + config["wordlist"])
    else:
        if config["chars_min"] > config["chars_max"]:
            msg = _("Nieprawidłowe dane: ")
            log.error(msg + str(config["chars_min"]) + ">" + str(config["chars_max"]))
            parser.error(msg + str(config["chars_min"]) + ">" + str(config["chars_max"]))
        wc = RangeStringVariation(config["chars_list"], config["chars_min"], config["chars_max"] + 1)
     
    try:   
        s = parse_opts_by_service(config["service"])
    except ImportError:
        msg = _("Nie ma takiej usługi (modułu): ")
        log.error(msg + config["service"])
        parser.error(msg + config["service"])
        
    if not options.service_options is None:
        group_config = s(options.service_options)
        for x in group_config:
            config[x] = group_config[x]
    
    log.debug(config)
          
    Q1 = Queue.Queue(config["thread_number"] * 2)
    Q2 = Queue.Queue()
    t = Transition()
    att = attack.Attack(uc, wc, wcr, t, Q1, Q2)
    
    start_threads(att, True)    
    main()
    sys.exit()
