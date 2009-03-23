# core.py
#
# Copyright (c) 2009 Stephen Day
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


class Parser(object):
    
    def __init__(self,dialect, method='xhtml', strip_whitespace=False, encoding='utf-8'):
        """Constructor for Parser objects

        :parameters:
          dialect
            Usually created using :func:`creoleparser.dialects.create_dialect`
          method
            This value is passed to Genshies Steam.render(). Possible values
            include ``xhtml``, ``html``, ``xml``, and ``text``.
          strip_whitespace
            This value is passed to Genshies Steam.render().
          encoding
            This value is passed to Genshies Steam.render().
            
        """
    
        self.dialect = dialect
        self.method = method
        self.strip_whitespace = strip_whitespace
        self.encoding=encoding

    def generate(self,text,element_store=None,context='block', environ=None):
        """Returns a Genshi Stream.

        :parameters:
          text
            The text to be parsed.
          context
            This is useful for marco development where (for example) supression
            of paragraph tags is desired. Can be 'inline', 'block', or a list
            of WikiElement objects (use with caution).
          element_store
            Internal dictionary that's passed around a lot ;)
          environ
            This can be any type of object. It will be passed to ``macro_func``
            unchanged (for a description of ``macro_func``, see
            :func:`~creoleparser.dialects.create_dialect`).
            
        """
        
        if element_store is None:
            element_store = {}
        if not isinstance(context,list):
            if context == 'block':
                top_level_elements = self.dialect.block_elements
                do_preprocess = True
            elif context == 'inline':
                top_level_elements = self.dialect.inline_elements
                do_preprocess = False
        else:
            top_level_elements = context
            do_preprocess = False

        if do_preprocess:
            text = preprocess(text,self.dialect)

        return bldr.tag(fragmentize(text,top_level_elements,element_store, environ)).generate()


    def render(self, text, element_store=None, context='block', environ=None, **kwargs):
        """Returns the final output string (e.g., xhtml). See
        :meth:`~creoleparser.core.Parser.generate` for named parameter descriptions.

        Left over keyword arguments (``kwargs``) will be passed to Genshi's Stream.render() method,
        overriding the corresponding attributes of the Parser object. For more infomation on Streams,
        see the `Genshi documentation <http://genshi.edgewall.org/wiki/Documentation/streams.html#serialization-options>`_.
        
        """

        if element_store is None:
            element_store = {}
        kwargs.setdefault('method',self.method)
        kwargs.setdefault('encoding',self.encoding)
        if kwargs['method'] != "text":
            kwargs.setdefault('strip_whitespace',self.strip_whitespace)
        stream = self.generate(text, element_store, context, environ)
        return stream.render(**kwargs)

    def __call__(self,text, **kwargs):
        """Wrapper for the render method. Returns final output string.

        """

        return self.render(text, **kwargs)


class ArgParser(object):
    
    def __init__(self,dialect, force_strings=False):
        """Constructor for ArgParser objects

        :parameters:
          dialect
            Usually created using :class:`creoleparser.dialects.CreoleArgs`
          force_strings
            If True, all lists will be converted to strings using
            ``' '.join(list)``. This guarentees returned values will be of
            type string or unicode.
            
        """
    
        self.dialect = dialect
        self.force_strings = force_strings


    def __call__(self, arg_string, force_strings='default'):
        """Parses the ``arg_string`` returning a two-tuple 

        :parameters:
          force_strings
            The default value is taken from the corresponding instance
            attribute. See the constructor (`__init__`) for a description.
        
        """

        if force_strings == 'default':
            force_strings = self.force_strings

        frags = fragmentize(arg_string,self.dialect.top_elements,{},{})
        assert len(frags) <= 2
        positional_args = []
        kw_args = {}
        for arg_group in frags:
           if isinstance(arg_group,list):
               positional_args = arg_group
           else:
               kw_args = arg_group
        if force_strings is True:
          for i,v in enumerate(positional_args):
             if isinstance(v,list):
                positional_args[i] = ' '.join(v)
          for k,v in kw_args.items():
             if isinstance(v,list):
                kw_args[k] = ' '.join(v)
        return (positional_args, kw_args)


def fragmentize(text,wiki_elements, element_store, environ, remove_escapes=True):

    """Takes a string of wiki markup and outputs a list of genshi
    Fragments (Elements and strings).

    This recursive function, with help from the WikiElement objects,
    does almost all the parsing.

    When no WikiElement objects are supplied, escapes are removed from
    ``text`` (except if remove_escapes=True)  and it is
    returned as-is. This is the only way for recursion to stop.

    :parameters:
      text
        the text to be parsed
      wiki_elements
        list of WikiElement objects to be searched for
      environ
        object that may by used by macros
      remove_escapes
        If False, escapes will not be removed
    
    """

    while wiki_elements:
        # If the first supplied wiki_element is actually a list of elements, \
        # search for all of them and match the closest one only.
        if isinstance(wiki_elements[0],(list,tuple)):
            x = None
            mos = None
            for element in wiki_elements[0]:
                mo = element.regexp.search(text)
                if mo:
                    if x is None or mo.start() < x:
                        x,wiki_element,mos = mo.start(),element,[mo]
        else:
            wiki_element = wiki_elements[0]
            mos = [mo for mo in wiki_element.regexp.finditer(text)]
             
        if mos:
            frags = wiki_element._process(mos, text, wiki_elements, element_store, environ)
            break
        else:
            wiki_elements = wiki_elements[1:]

    # remove escape characters 
    else: 
        if remove_escapes:
            text = esc_to_remove.sub('',text)
        frags = fill_from_store(text,element_store)
        
    return frags


def fill_from_store(text,element_store):
    frags = []
    mo = place_holder_re.search(text)
    while mo:
        if mo.start():
            frags.append(text[:mo.start()])
        frags.append(element_store.get(mo.group(1),
                       mo.group(1).join(['<<<','>>>'])))
        if mo.end() < len(text):
            text = text[mo.end():]
        else:
            break
        mo = place_holder_re.search(text)
    else:
        frags.append(text)
    return frags


def preprocess(text, dialect):
    """This should generally be called before fragmentize().

    :parameters:
      text
        text to be processsed.
      dialect
        a ``Dialect`` object.
    """
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    return text


def chunk(text, blank_lines, hard_elements, limit):
    """Safely breaks large Creole documents into a list of smaller
    ones (strings) - DEPRECIATED
    """
    hard_spans = []
    for e in hard_elements:
        for mo in e.regexp.finditer(text):
            hard_spans.append(mo.span())

    hard_chars = []
    for x,y in hard_spans:
        hard_chars.extend(range(x,y))
    hard_chars = set(hard_chars)

    chunks = []
    start = 0
    for i in range(len(blank_lines)/limit):
        for mo in blank_lines[limit/2 + i*limit:limit*3/2+i*limit:10]:
            if mo.start() not in hard_chars:
                chunks.append(text[start:mo.start()])
                start = mo.end()
                break
    chunks.append(text[start:])
    
    return chunks



def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

