# -*- coding: utf-8 -*-

"""
Moduł zawierający podstawowe definicje dla modułów usług.
"""

class ServiceException(Exception):
    
    """Klasa błędu.
    
    Jest ona podstawą dla błędów w konkretnych modułach implementujących protokoły.
    """

    def __init__(self, msg):
        """Konstruktor."""
        Exception.__init__(self, msg)
