# core.py
#
# Copyright (c) 2007 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

import re

import genshi.builder as bldr

__docformat__ = 'restructuredtext en'

escape_char = '~'
esc_neg_look = '(?<!' + re.escape(escape_char) + ')'
esc_to_remove = re.compile(''.join([r'(?<!',re.escape(escape_char),')',re.escape(escape_char),r'(?!([ \n]|$))']))
place_holder_re = re.compile(r'<<<(-?\d+?)>>>')

def fill_from_store(text,element_store):
    frags = []
    mo = place_holder_re.search(text)
    if mo:
        if mo.start():
            frags.append(text[:mo.start()])
        #print mo.group(1), element_store.d.get(mo.group(1),'Empty')
        frags.append(element_store.get(mo.group(1),
                       mo.group(1).join(['<<<','>>>'])))
        if mo.end() < len(text):
            frags.extend(fill_from_store(text[mo.end():],element_store))
    else:
        frags = [text]
    return frags

def fragmentize(text,wiki_elements, element_store,remove_escapes=True):

    """Takes a string of wiki markup and outputs a list of genshi
    Fragments (Elements and strings).

    This recursive function, with help from the WikiElement objects,
    does almost all the parsing.

    When no WikiElement objects are supplied, escapes are removed from
    ``text`` (except if called from ``no_wiki`` or ``pre``)  and it is
    returned as-is. This is the only way for recursion to stop.

    :parameters:
      text
        the text to be parsed
      wiki_elements
        list of WikiElement objects to be searched for
      remove_escapes
        If False, escapes will not be removed
    
    """

    # remove escape characters 
    if not wiki_elements:
        if remove_escapes:
            text = esc_to_remove.sub('',text)
        frags = fill_from_store(text,element_store)
        return frags

    # If the first supplied wiki_element is actually a list of elements, \
    # search for all of them and match the closest one only.
    if isinstance(wiki_elements[0],(list,tuple)):
        x = None
        mo = None
        for element in wiki_elements[0]:
            m = element.regexp.search(text)
            if m:
                if x is None:
                    x,wiki_element,mo = m.start(),element,m
                elif m.start() < x:
                    x,wiki_element,mo = m.start(),element,m
 
    else:
        wiki_element = wiki_elements[0]
        mo = wiki_element.regexp.search(text)
         
    frags = []
    if mo:
        frags = wiki_element._process(mo, text, wiki_elements, element_store)
    else:
        frags = fragmentize(text,wiki_elements[1:],element_store)

    return frags


class Parser(object):

    """Instantiates a parser with specified behaviour"""
    
    def __init__(self,dialect, method='xhtml', strip_whitespace=False, encoding='utf-8'):
        """Constructor for Parser objects.

        :parameters:
          dialect
            A Creole instance
          method
            This value is passed to genshies Steam.render(). Possible values
            include ``xhtml``, ``html``, and ``xml``.
          strip_whitespace
            This value is passed Genshies Steam.render().
          encoding
            This value is passed Genshies Steam.render().
        """
        self.dialect = dialect
        self.method = method
        self.strip_whitespace = strip_whitespace
        self.encoding=encoding

    def generate(self,text,element_store=None):
        """Returns a Genshi Stream."""
        if element_store is None:
            element_store = {}
        text = preprocess(text,self.dialect)
        return bldr.tag(fragmentize(text,self.dialect.parse_order,element_store)).generate()

    def render(self,text,element_store=None,**kwargs):
        """Returns final output string (e.g., xhtml)

        :parameters:
          See Genshi documentation for additional keyword arguments.
        """
        if element_store is None:
            element_store = {}
        return self.generate(text,element_store).render(method=self.method,strip_whitespace=self.strip_whitespace,
                                          encoding=self.encoding,**kwargs)

    def __call__(self,text,element_store=None):
        """Wrapper for the render method. Returns final output string."""
        if element_store is None:
            element_store = {}
        return self.render(text,element_store)

def preprocess(text, dialect):
    """This should generally be called before fragmentize().

    :parameters:
      text
        text to be processsed.
      dialect
        a ``Creole`` object.
    """
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = ''.join([text.rstrip(),'\n']) 
    #text = ''.join(encode_macros(text,[dialect.pre,dialect.no_wiki],
    #                          [dialect.macro]))
    return text


##def encode_macros(text, elements_to_skip=None,
##               elements_to_process=None):
##    """This is used to flag macros that aren't in a nowiki block
##    before further parsing. Only flagged macros will be processed
##    later.
##
##    :parameters:
##      text
##        text to be processsed.
##      elements_to_skip
##        these wiki elements will not be processed.
##      elements_to_process
##        these wiki elements will have an escape added according to
##        their ``encode`` method
##    """
##
##    if not elements_to_skip:
##        for element in elements_to_process:
##            text = element.encode(text)
##        return [text]
##
##    mo = elements_to_skip[0].regexp.search(text)
##    parts = []
##    if mo:
##        if mo.start():
##            parts.extend(encode_macros(text[:mo.start()],elements_to_skip[1:],
##                                    elements_to_process))
##        parts.append(mo.group(0))
##        if mo.end() < len(text):
##            parts.extend(encode_macros(text[mo.end():],elements_to_skip,
##                                    elements_to_process))
##    else:
##        parts = encode_macros(text,elements_to_skip[1:],elements_to_process)
##    return parts
     

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

