# rjohn

rjohn jest oprogramowaniem umożliwiającym przeprowadzanie ataków słownikowych i siłowych.

## Wymagania

* python 2.x (testowane na 2.6.5)
* biblioteka PyCrypto (http://www.dlitz.net/software/pycrypto/) z gałęzi 2.x (testowane na 2.1.0)

## Instalacja

Program dostarczany jest w postaci kodu źródłowego wykonywanego na interpreterze języka Python dlatego też nie potrzebuje on bezpośredniej instalacji.

## Uruchomienie

Program można uruchomić na wiele sposobów poniżej przedstawione są dwa z nich. Oba dotyczą instalacji w systemie operacyjnym Linux.

Pierwszy, polega na ręcznym wywołaniu interpretera i składa się z kolejnych kroków:

* przekopiować pliki programu w dowolne miejsce
* ustawić zmienną PYTHONPATH, na sciezka/rjohn/src gdzie sciezka to ścieżka do katalogu w którym znajduje się rjohn
* wywołać interpreter python (lub python2) w celu uruchomienia rjohn/src/main/main.py

przykład:
	katalog rjohn znajduje sie w /home/marcin
	export PYTHONPATH=/home/marcin/rjohn/src
	/usr/bin/python2 /home/marcin/rjohn/src/main/main.py
	
Drugi stanowi uproszczenie i wykorzystuje skrypt bash-a:

* przekopiować pliki programu w dowolne miejsce
* uruchomić program poprzez uruchomienie skryptu bash-a rjohn, znajdującego się w katalogu src

przykład:
	[marcin@laptop src]$ ./rjohn