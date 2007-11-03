# __init__.py
#
# Copyright (c) 2007 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
"""
This is a Python implementation of a parser for the Creole wiki markup language.
The specification of that can be found at http://wikicreole.org/wiki/Creole1.0

Basic Usage
===========
>>> from creoleparser import creole_to_xhtml

Simply call the creole_to_xhtml() function with one argument (the text to be parsed):

>>> print creole_to_xhtml("Some real **simple** mark-up"),
<p>Some real <strong>simple</strong> mark-up</p>

To customize things a little, create your own dialect and parser:

>>> from creoleparser.dialects import Creole10
>>> from creoleparser.core import Parser

>>> my_dialect=Creole10(wiki_links_base_url='http://www.mysite.net/',
... interwiki_links_base_urls=dict(wikicreole='http://wikicreole.org/wiki/'))

>>> my_parser = Parser(dialect=my_dialect)

>>> print my_parser("[[Home]] and [[wikicreole:Home]]"),
<p><a href="http://www.mysite.net/Home">Home</a> and <a href="http://wikicreole.org/wiki/Home">wikicreole:Home</a></p>

TODO
====
 - Add (a lot) more docstrings (done)
 - Package this module properly and make it easy_install'able (done)
 - Add a 'use_additions' option to the Creole class (and implement them!)
 - Move the tests to a separate file (done)
 - Compile the re's used for preprocessing (done)
"""

from core import Parser
from dialects import Creole10

__docformat__ = 'restructuredtext en'


creole_to_xhtml = Parser(dialect=Creole10(wiki_links_base_url='http://www.wikicreole.org/wiki/',
                             interwiki_links_base_urls={'Ohana':'http://wikiohana.net/cgi-bin/wiki.pl/'}))
"""This is a parser created for convenience"""


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
