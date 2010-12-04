# -*- coding: utf-8 -*-

"""
Moduł wykonujący atak.

Zawiera on klasy Ataku, Producenta i Konsumenta.
"""

import threading
import logging
import time
from services.service import ServiceException

class Producer(threading.Thread):
    
    """Producent w modelu współbierznym.
    
    Zadaniem tej klasy jest iteracja klasy Attack.
    """
    
    def __init__(self, att, event):
        """Konstruktor.
        
        Argumenty:
        att -- obiekt Attack
        event -- zdarzenie informujące o konieczności wypisania statusu
        
        """
        threading.Thread.__init__(self)
        self.__alive = True
        self.__att = att
        self.__event = event
        self.__log = logging.getLogger("Producer")
        
    def reset(self):
        """Resetuje obiekt Attack."""
        self.__att = iter(self.__att)
        
    def run(self):
        """Wykonuje działanie w wątku.
        
        Iteruje po obiekcie Attack, a w przypadku ustawienia zdarzenia 
        wypisuje status.
        
        """
        while self.__alive:
            try:
                next(self.__att)
                if self.__event.is_set():
                    print(self.__att.a + " " + self.__att.c_t)
                    self.__event.clear()
            except StopIteration:
                break
            except:
                msg = _("Błąd w wątku producenta")
                print(msg)
                self.__log.error(msg)
                break
    
    def stop(self):
        """Zatrzymuje wątek."""
        self.__log.debug(_("Wątek producenta zakończył pracę"))
        self.__alive = False
    
    def stopChilds(self):
        """Zatrzymuje wątki konsumentów."""
        self.__att.Q1.put(True, timeout=10.0)
        
    def getAttack(self):
        """Zwraca obiekt Attack."""
        return self.__att
        
class Consumer(threading.Thread):
    
    """Konsument w modelu współbierznym.
    
    Klasa ta wykonuje próbę uwierzytelnienia. Obsługuje ona zdefiniowane 
    ograniczenia czasowe i błędy w transmisji.
    """
    
    def __init__(self, service, queue1, queue2, config={}):
        """Konstruktor.
        
        Argumenty:
        service -- obiekt usługi
        queue1 -- kolejka synchronizowana do odbierania par (login i hasło)
        queue2 -- kolejka synchronizowana do zapisywania poprawnych danych uwierzytelniających
        config -- słownik zawierający konfigurację
        
        """
        threading.Thread.__init__(self)
        self.__log = logging.getLogger("Consumer")
        self.__service = service
        self.__queue1 = queue1
        self.__queue2 = queue2
        self.__verbose = config.get("verbose", False)
        self.__bsleep = config.get("between_time", 0)
        self.__rsleep = config.get("retry_time", 0)
        self.__rtrials = config.get("retry_trials", 0)
        self.__alive = True
        
    def isActive(self): 
        """Zwraca czy wątek działa"""
        return self.__alive
            
    def run(self):
        """Wykonuje działanie w wątku.
        
        Pobiera dane z kolejki, wykonuje uwierzytelnienie oraz sprawdza warunki i błędy.
        
        """
        while True:
            g = self.__queue1.get()
            if isinstance(g, bool):
                msg = _("Wątek konsumenta zakończył pracę")
                if self.__verbose:
                    print(msg)
                self.__log.debug(msg)
                self.__queue1.put(g)
                self.__alive = False
                break
            a, b = g
            flag = True
            counter = 0
            while flag:
                flag = False
                result = False
                try:
                    time.sleep(self.__bsleep)
                    result = self.__service.auth(a, b)
                    
                    msg = "AUTH: " + a + " " + b + " " + str(result)
                    if self.__verbose:
                        print(msg)
                    self.__log.debug(msg)
                except ServiceException as err:
                    msg = _("Błąd usługi w wątku konsumenta: {0}".format(err))
                    print(msg)
                    self.__log.error(msg)
                    if self.__rsleep == 0:
                        self.__alive = False
                        return
                    else:
                        counter += 1
                        if counter > self.__rtrials:
                            self.__alive = False
                            return
                        flag = True
                        time.sleep(self.__rsleep)
                        continue
                except:
                    msg = _("Błąd w wątku konsumenta")
                    print(msg)
                    self.__log.error(msg)
                    if self.__rsleep == 0:
                        self.__alive = False
                        return
                    else:
                        counter += 1
                        if counter > self.__rtrials:
                            self.__alive = False
                            return
                        flag = True
                        time.sleep(self.__rsleep)
                        continue
                    
            if result == True:
                self.__log.info("HIT: " + a + " " + b)
                self.__queue2.put((a, b))
        
class Attack:
    
    """Klasa Ataku.
    
    Generuje ona za każdą iteracją kolejną parę login, hasło.
    """
    
    def __init__(self, user_container, word_container, word_rule_container,
                 transition, queue1, queue2):
        """Konstruktor.
        
        Argumenty:
        user_container -- kontener nazwa użytkowników
        word_container -- kontener słów
        word_rule_container -- kontener reguł transformacji
        transition -- klasa transformacji
        queue1 -- kolejka synchronizowana do zapisywania par (login i hasło)
        queue2 -- kolejka synchronizowana do odbierania poprawnych danych uwierzytelniających
        
        """
        self.uc = user_container
        self.wc, self.wrc = word_container, word_rule_container
        self.transition = transition
        
        self.__result = {}
        
        self.__iters()
        
        self.Q1 = queue1
        self.Q2 = queue2
        
    def getResult(self):
        """Zwraca listę wyników."""
        return self.__result
        
    def __iters(self):
        self.i1 = iter(self.uc)
        self.i3 = iter(self.wc)
        self.i4 = iter(self.wrc)
        
    def __next(self):
        """Pobiera następne wartości."""
        self.a = next(self.i1)
        self.c = next(self.i3)
        self.d = next(self.i4)
        
    def __iter__(self):
        """Ustawia iteratory."""
        self.__flag = False
        self.__iters()
        try:
            self.__next()
        except StopIteration:
            self.__flag = True
        
        return self

    def next(self):
        """Wykonuje krok iteracji, zwraca None."""
        if self.__flag == True:
            raise StopIteration
        try:
            self.c_t = self.transition.transform(self.d, self.c)
            
            taken = []
            while True:
                try:
                    taken.append(self.Q2.get_nowait())
                except:
                    break
                
            hit = False
            for x in taken:
                tt_a, tt_b = x
                self.__result[tt_a] = tt_b
                if tt_a == self.a:
                    hit = True
            
            if hit == True:
                try:
                    self.a = next(self.i1)
                except StopIteration:
                    self.__flag = True
                self.i3 = iter(self.wc)
                self.i4 = iter(self.wrc)
                self.c = next(self.i3)
                self.d = next(self.i4)
                return
            
            self.Q1.put((self.a, self.c_t))
                
            self.d = next(self.i4)
        except StopIteration:
            self.i4 = iter(self.wrc)
            self.d = next(self.i4)
            try:
                self.c = next(self.i3)
            except StopIteration:
                self.i3 = iter(self.wc)
                self.c = next(self.i3)
                try:
                    self.a = next(self.i1)
                except StopIteration:
                    self.__flag = True
        return
    
    def __getstate__(self):
        """Zwraca stan obiektu.
        
        Funkcja usuwa z obiektu Q1 i Q2 bo nie można ich zapisać łatwo do pliku.
        
        """
        state = self.__dict__.copy()
        del state['Q1']
        del state['Q2']
        return state

    def __setstate__(self, state):
        """Ustawia stan obiektu.
        
        Funkcja ustawia na None wartości Q1 i Q2.
        
        """
        self.__dict__.update(state)
        
        self.Q1 = None
        self.Q2 = None  
