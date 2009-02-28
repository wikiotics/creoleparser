# __init__.py
#
# Copyright (c) 2009 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

from core import Parser
from dialects import create_dialect, Creole10

__docformat__ = 'restructuredtext en'

creole2html = Parser(dialect=create_dialect(use_additions=False), method='html')
"""This is a pure Creole 1.0 parser created for convenience"""

text2html = Parser(dialect=create_dialect(), method='html')
"""This is a Creole 1.0 parser (+ additions) created for convenience"""

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
