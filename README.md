# rjohn

rjohn jest oprogramowaniem umożliwiającym przeprowadzanie ataków słownikowych i siłowych.

## Wymagania

* python 2.x (testowane na 2.6.5)
* biblioteka [PyCrypto][1] z gałęzi 2.x (testowane na 2.1.0)

[1]:http://www.dlitz.net/software/pycrypto/

## Instalacja

### Linux

Program dostarczany jest w postaci kodu źródłowego wykonywanego na interpreterze języka Python dlatego też nie potrzebuje on bezpośredniej instalacji.

### Windows

Program dostarczany jest albo jakoś źródła albo jako binaria. Żadna z tych wersji nie potrzebuje bezpośredniej instalacji.

## Uruchomienie

### Linux

Program można uruchomić na wiele sposobów poniżej przedstawione są dwa z nich.

Pierwszy, polega na ręcznym wywołaniu interpretera i składa się z kolejnych kroków:

* przekopiować pliki programu w dowolne miejsce
* ustawić zmienną PYTHONPATH, na sciezka/rjohn/src gdzie sciezka to ścieżka do katalogu w którym znajduje się rjohn
* wywołać interpreter python (lub python2) w celu uruchomienia rjohn/src/main.py

przykład:
	katalog rjohn znajduje sie w /home/marcin
	export PYTHONPATH=/home/marcin/rjohn/src
	/usr/bin/python /home/marcin/rjohn/src/main.py
	
Drugi stanowi uproszczenie i wykorzystuje skrypt bash-a:

* przekopiować pliki programu w dowolne miejsce
* uruchomić program poprzez uruchomienie skryptu bash-a rjohn, znajdującego się w katalogu programu

przykład:
	[marcin@laptop rjohn]$ ./rjohn
	
### Windows

Program można uruchomić albo poprzez wywołanie interpretera, albo za pomocą dostarczony binarów.

Pierwszy sposób składa się z następujących kroków:

* przekopiować pliki programu w dowolne miejsce
* ustawić zmienną środowiskową PYTHONPATH na sciezka\rjohn\src gdzie sciezka to ścieżka do katalogu w którym znajduje się rjohn
* wywołać interpreter python (lub python2) w celu uruchomienia rjohn\src\main.py

Najprościej ustawić zmienne środowiskowe poprzez zakładkę zaawansowane w Moim Komputerze.
Wywołanie programu w konsoli można sobie uprościć przeciągając nazwy plików (lub katalogów) z Eksplorera Windows.

Drugi sposób dotyczy wywołania binarnej wersji programu. Nie trzeba wówczas posiadać zainstalowanego interpretera języka Python.

* wywołać w konsoli dist\main.exe

Dodatkowo w systemie muszą znajdować się następujące biblioteki DLL

* WS2_32.dll - C:\WINDOWS\system32\WS2_32.dll
* SHELL32.dll - C:\WINDOWS\system32\SHELL32.dll
* USER32.dll - C:\WINDOWS\system32\USER32.dll
* ADVAPI32.dll - C:\WINDOWS\system32\ADVAPI32.dll
* KERNEL32.dll - C:\WINDOWS\system32\KERNEL32.dll 

Wersja binarna została zbudowana w systemie Windows XP (32 bit) i nie gwarantuje się że będzie działać na innej wersji systemu Windows.

## Pliki dodatkowe

Razem z programem dostarczane są dodatkowe pliki, domyślnie używane przez program w przypadku braku innych.

* wordlist.txt - zawiera zbiór 3157 haseł udostępnionych na stronie [openwall][2]
* wordrules.txt - zawiera zbiór reguł przetwarzania słów
* userlist.txt - zawiera zbiór użytkowników którzy mają być używaniu do uwierzytelnienia podczas ataku

[2]:http://www.openwall.com/wordlists/
