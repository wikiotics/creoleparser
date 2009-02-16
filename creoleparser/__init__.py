# __init__.py
#
# Copyright (c) 2009 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

from core import Parser
from dialects import Creole10

__docformat__ = 'restructuredtext en'

creole2html = Parser(dialect=Creole10(use_additions=False,no_wiki_monospace=True),method='html')
"""This is a pure Creole 1.0 parser created for convenience"""

text2html = Parser(dialect=Creole10(use_additions=True,no_wiki_monospace=False),method='html')
"""This is a Creole 1.0 parser (+ additions) created for convenience"""

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
