# -*- coding: utf-8 -*-

"""
Moduł udostępniający interfejs do wykonywania przekształceń.
"""

class TransitionException(ValueError):
    """Klasa błędu. Wyrzucana w przypadku błędu w module Transition."""
    pass

UNKNOWN_RULE = _("Nieznana reguła")

class Transition:
    
    """
    Klasa Przekształceń.

	Zawiera ona metody implementujące przekształcenia.	
	"""
    
    def __init__(self):
        """Konstruktor."""
        pass
        
    def __checkClass(self, class_symbol, letter):
        """Sprawdza czy znak należy do klasy znaków, zwraca boolean.
	
	    Funkcja zwraca True jeżeli znak należy do klasy znaków, a 
	    False jeżeli nie należy.
	    W dokumentacja John The Ripper określone jako: character classes

	    Argumenty:
	    class_symbol -- symbol klasy
	    letter - znak do sprawdzenia

	    """
        if class_symbol == 'a':
            if letter.isalpha():
                return True
        elif class_symbol == 'd':
            if letter.isdigit():
                return True
        elif class_symbol == 'x':
            if letter.isalnum():
                return True
        elif class_symbol == 'w':
            if letter.isspace():
                return True
        elif class_symbol == 'l':
            if letter.islower():
                return True
        elif class_symbol == '?':
            if letter == '?':
                return True
        elif class_symbol == 'v':
            if letter in "aeiouAEIOU":
                return True
        elif class_symbol == 'c':
            if letter in "bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ":
                return True
        elif class_symbol == 'p':
            if letter in ".,:;'\"?!`":
                return True
        elif class_symbol == 's':
            if letter in "$%^&*()-_+=|\<>[]{}#@/~":
                return True
        elif class_symbol == 'u':
            if letter in "ABCDEFGHIJKLMNOPQRSTVWXYZ":
                return True
        elif class_symbol == 'z':
            return True
    
        return False 

    def __getInt(self, rule, string):
        """Zwraca wartość całkowitą.
    
    	Funkcja zwraca wartość całkowitą podanej reguły.
    
    	Argumenty:
    	rule -- reguła
    	string -- opcjonalnie łańcuch znaków
    	
    	"""
        if (rule >= '0') and (rule <= '9'):
            return eval(rule)
        elif (rule >= 'A') and (rule <= 'Z'):
            bytes = rule.encode()[0]
            bytes = ord(bytes)
            bytes -= 55
            return bytes
        elif (rule == 'l') or (rule == 'z'):
            return len(string)
    
    def __reverse(self, string):
        """Odwraca kolejność znaków w łańcuchu."""
        tmp = ""
        for x in range(len(string) - 1, -1, -1):
            tmp += string[x]
        return tmp
    
    def __rotateLeft(self, string):
        """Wykonuje rotację w lewo łańcucha znaków."""
        tmp = string[1:]
        return tmp + string[:1]
    
    def __rotateRight(self, string):
        """Wykonuje rotację w prawo łańcucha znaków."""
        tmp = string[:-1]
        return string[-1:] + tmp
    
    def __reflect(self, string):
        """Odbija łańcuch znaków."""
        return string + self.__reverse(string)
    
    def __replaceClass(self, class_symbol, char, string):
        """Zamienia wszystkie wystąpienia znaków należących do danej klasy na podany znak.

    	Argumenty:
    	class_symbol -- klasa znaków do zastąpnienia
    	char -- nowy znak
    	string -- łańcuch na którym będzie wykonywana operacja
    
    	"""
        lists = list(string)
        for x in range(len(lists)):
            if self.__checkClass(class_symbol, lists[x]):
                lists[x] = char
        return "".join(lists)
    
    def __checkContainsClass(self, class_symbol, string):
        """Sprawdza czy łańcuch zawiera znak należący do danej klasy.

    	Argumenty:
    	class_symbol -- klasa znaków do znalezienia
    	string -- łańcuch na którym będzie wykonywana operacja
    
    	"""
        for x in string:
            if self.__checkClass(class_symbol, x):
                return True
        return False
    
    def __countClass(self, class_symbol, string):
        """Zlicza ilość wystąpień znaków należących do danej klasy w łańcuchu.
	
    	Argumenty:
    	class_symbol -- klasa znaków do zliczenia
    	string -- łańcuch na którym będzie wykonywana operacja
    
    	"""
        c = 0
        for x in string:
            if self.__checkClass(class_symbol, x):
                c += 1
        return c
    
    def transform(self, rules, word):
        """Transformuje słowo w oparciu o reguły, zwraca str.

    	Argumenty:
    	rules -- reguły
    	word -- słowo do przetworzenia
    
    	"""
        if len(rules) < 1:
            return word
        
        # simple commands
        if rules[0] == ':':
            return self.transform(rules[1:], word)
        elif rules[0] == 'l':
            return self.transform(rules[1:], word.lower())
        elif rules[0] == 'u':
            return self.transform(rules[1:], word.upper())
        elif rules[0] == 'c':
            return self.transform(rules[1:], word.capitalize())
        elif rules[0] == 'C':
            return self.transform(rules[1:], word[0].lower() + word[1:].upper())
        elif rules[0] == 't':
            num = None
            if len(rules) > 1:
                num = self.__getInt(rules[1], word)
            if num is not None:
                return self.transform(rules[2:], word[:num] + word[num].swapcase() + word[num + 1:])
            return self.transform(rules[1:], word.swapcase())
        elif rules[0] == 'r':
            return self.transform(rules[1:], self.__reverse(word))
        elif rules[0] == 'd':
            return self.transform(rules[1:], word + word)
        elif rules[0] == '$':
            return self.transform(rules[2:], word + rules[1])
        elif rules[0] == '^':
            return self.transform(rules[2:], rules[1] + word)
        elif rules[0] == '{':
            return self.transform(rules[1:], self.__rotateLeft(word))
        elif rules[0] == '}':
            return self.transform(rules[1:], self.__rotateRight(word))
        elif rules[0] == 'f':
            return self.transform(rules[1:], self.__reflect(word))
        # end simple commands
        
        # character class commands
        elif rules[0] == 's':
            if rules[1] == '?':
                ch_class = rules[2]
                ch3 = rules[3]
                return self.transform(rules[4:], self.__replaceClass(ch_class, ch3, word))
            else:
                ch1 = rules[1]
                ch2 = rules[2]
                return self.transform(rules[3:], word.replace(ch1, ch2))
        elif rules[0] == '@':
            if rules[1] == '?':
                ch_class = rules[2]
                return self.transform(rules[3:], self.__replaceClass(ch_class, '', word))
            ch1 = rules[1]
            return self.transform(rules[2:], word.replace(ch1, ''))
        elif rules[0] == '!':
            if rules[1] == '?':
                if not self.__checkContainsClass(rules[2], word):
                    return self.transform(rules[3:], word)
                else:
                    return None
            if word.find(rules[1]) == -1:
                return self.transform(rules[2:], word)
            return None
        elif rules[0] == '/':
            if rules[1] == '?':
                if self.__checkContainsClass(rules[2], word):
                    return self.transform(rules[3:], word)
                return None
            if word.find(rules[1]) != -1:
                return self.transform(rules[2:], word)
            return None
        elif rules[0] == '=':
            num = self.__getInt(rules[1], word)
            if not num is None:
                if rules[2] == '?':
                    if self.__checkClass(rules[3], word[num]):
                        return self.transform(rules[4:], word)
                    return None
                else:
                    if word[num] == rules[2]:
                        return self.transform(rules[3:], word)
                    return None
            raise TransitionException(UNKNOWN_RULE)
        elif rules[0] == '(':
            if rules[1] == '?':
                if self.__checkClass(rules[2], word[0]):
                    return self.transform(rules[3:], word)
                return None
            else:
                if word[0] == rules[1]:
                    return self.transform(rules[2:], word)
                return None
        elif rules[0] == ')':
            if rules[1] == '?':
                if self.__checkClass(rules[2], word[len(word) - 1]):
                    return self.transform(rules[3:], word)
                return None
            else:
                if word[len(word) - 1] == rules[1]:
                    return self.transform(rules[2:], word)
                return None
        elif rules[0] == '%':
            num = self.__getInt(rules[1], word)
            if not num is None:
                if rules[2] == '?':
                    if self.__countClass(rules[3], word) >= num:
                        return self.transform(rules[4:], word)
                    return None
                else:
                    if word.count(rules[2]) >= num:
                        return self.transform(rules[3:], word)
                    return None
            raise TransitionException(UNKNOWN_RULE)
        # end character class commands
        
        # string commands
        elif rules[0] == 'A':
            num = self.__getInt(rules[1], word)
            if num is None:
                raise TransitionException(UNKNOWN_RULE)
            ch1 = rules[2]
            if ch1 != '\"':
                raise TransitionException(UNKNOWN_RULE)
            index2 = rules.find('\"', 3)
            if index2 == -1:
                raise TransitionException(UNKNOWN_RULE)
            s = rules[3:index2]
            return self.transform(rules[1 + index2:], word[:num] + s + word[num:])           
        # end string commands
        
        # length control commands
        elif rules[0] == '<':
            num = self.__getInt(rules[1], word)
            if num is not None:
                if len(word) < num:
                    return self.transform(rules[2:], word)
                return None
            raise TransitionException(UNKNOWN_RULE)
        elif rules[0] == '>':
            num = self.__getInt(rules[1], word)
            if num is not None:
                if len(word) > num:
                    return self.transform(rules[2:], word)
                return None
            raise TransitionException(UNKNOWN_RULE)
        elif rules[0] == '\'':
            num = self.__getInt(rules[1], word)
            if num is not None:
                if len(word) > num:
                    return self.transform(rules[2:], word[:num])
                return None
            raise TransitionException(UNKNOWN_RULE)
        # end length control commands
        
        # insert/delete commands
        elif rules[0] == '[':
            return self.transform(rules[1:], word[1:])
        elif rules[0] == ']':
            return self.transform(rules[1:], word[:-1])
        elif rules[0] == 'D':
            num = self.__getInt(rules[1], word)
            if num is not None:
                return self.transform(rules[2:], word[:num] + word[num + 1:])
            raise TransitionException(UNKNOWN_RULE)
        elif rules[0] == 'x':
            num = self.__getInt(rules[1], word)
            if num is not None:
                num2 = self.__getInt(rules[2], word)
                if num is not None:
                    return self.transform(rules[3:], word[num:num + num2])
            raise TransitionException(UNKNOWN_RULE)
        elif rules[0] == 'i':
            num = self.__getInt(rules[1], word)
            if num is not None:
                char = rules[2]
                return self.transform(rules[3:], word[:num] + char + word[num:])
            raise TransitionException(UNKNOWN_RULE)
        elif rules[0] == 'o':
            num = self.__getInt(rules[1], word)
            if num is not None:
                char = rules[2]
                return self.transform(rules[3:], word[:num] + char + word[num + 1:])
            raise TransitionException(UNKNOWN_RULE)
        # end insert/delete commands
        
        raise TransitionException(UNKNOWN_RULE)
        
