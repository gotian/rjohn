# -*- coding: utf-8 -*-

"""
Moduł udostępniający interfejs serializowalnych kontenerów.
"""

class Container:
	"""
	Klasa Kontenera.

	Iterator po elementach sekwencji.
	"""

	def __init__(self, seq):
		"""Konstruktor.

		Argumenty:
		seq -- sekwencja
	
		"""
		self.seq = seq

	def __iter__(self):
		"""Ustawia wartość początkową iteratora."""
		self.i = 0
		return self

	def next(self):
		"""Zwraca następną wartość iteratora."""
		self.i += 1
		if (self.i > len(self.seq)):
			raise StopIteration
		return self.seq[self.i - 1]

class FileContainer:

	"""
	Klasa Kontenera Plikowego.

	Iterator po wierszach pliku.
	"""

	def __init__(self, filename):
		"""Konstruktor.

		Argumenty:
		filename -- nazwa pliku
		
		"""
		self.filename = filename
		self.file = open(self.filename)
		self.cache = []

	def __iter__(self):
		"""Ustawia wartość początkową iteratora."""
		self.cache_index = 0
		return self

	def next(self):
		"""Zwraca następną wartość iteratora."""
		self.cache_index += 1
		if len(self.cache) >= self.cache_index:
			return self.cache[self.cache_index - 1]

		if self.file.closed:
			raise StopIteration

		line = self.file.readline()
		if not line:
			self.file.close()
			raise StopIteration

		line = line.rstrip().lstrip()

		self.cache.append(line)
		return line

	def __getstate__(self):
		"""Zwraca stan obiektu. Usuwa obiekty nieserializowalne."""
		state = self.__dict__.copy()
		del state['file']
		return state

	def __setstate__(self, state):
		"""Ustawia stan obiektu. Otwiera na nowo plik."""
		self.__dict__.update(state)
		file = open(self.filename)
		for _ in range(self.cache_index):
			file.readline()
		self.file = file

