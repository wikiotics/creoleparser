# __init__.py
#
# Copyright (c) 2007 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

from core import Parser
from dialects import Creole10

__docformat__ = 'restructuredtext en'

creole2html = Parser(dialect=Creole10(use_additions=False,no_wiki_monospace=True))
"""This is a pure Creole 1.0 parser created for convenience"""

creole_to_xhtml = creole2html
"""Same as creole2html"""

text2html = Parser(dialect=Creole10(use_additions=True,no_wiki_monospace=False))
"""This is a Creole 1.0 parser (+ additions) created for convenience"""

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
