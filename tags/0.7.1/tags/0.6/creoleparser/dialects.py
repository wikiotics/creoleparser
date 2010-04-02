# dialects.py
#
# Copyright (c) 2009 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

import warnings

from elements import *



def create_dialect(dialect_base, **kw_args):
    """Factory function for dialect objects (for parameter defaults,
    see :func:`~creoleparser.dialects.creole10_base`)

    :parameters:
      dialect_base
        The class factory to use for creating the dialect object.
        ``creoleparser.dialects.creole10_base`` and  
        ``creoleparser.dialects.creole11_base`` are possible values.
      wiki_links_base_url
        The page name found in wiki links will be appended to this to form
        the href.
      wiki_links_space_char
        When wiki_links have spaces, this character replaces those spaces in
        the url. 
      interwiki_links_base_urls
        Dictionary of urls for interwiki links.
      interwiki_links_space_chars
        Dictionary of characters that that will be used to replace spaces
        that occur in interwiki_links. If no key is present for an interwiki
        name, the wiki_links_space_char will be used.
      interwiki_links_funcs
        Dictionary of functions that will be called for interwiki link
        names. Works like wiki_links_path_func
      no_wiki_monospace
        If `True`, inline no_wiki will be rendered as <code> not <span>
      wiki_links_class_func
        If supplied, this fuction will be called when a wiki link is found and
        the return value (should be a string) will be added as a class attribute
        of the corresponding link. The function must accept the page name (any
        spaces will have been replaced) as it's only argument.
        If no class attribute is to be added, return `None`.
      wiki_links_path_func
        If supplied, this fuction will be called when a wiki link is found and
        the return value (should be a string) will be joined to the base_url
        to form the url for href. The function must accept the page name (any
        spaces will have been replaced) as it's only argument. Returning the
        unaltered page name is equivalent to not supplying this function at all.
      macro_func
        If supplied, this fuction will be called when macro markup is found. The
        function must accept the following postional arguments:
        
        1. macro name (string)
        2. the argument, including any delimter (string)
        3. the macro body (string or None for a macro without a body)
        4. macro type (boolean, True for block macros, False for normal macros)
        5. an `environ` object (see :meth:`creoleparser.core.Parser.generate`)
        
        The function may return a string (which will be subject to further wiki
        processing) or a Genshi object (Stream, Markup, builder.Fragment, or
        builder.Element). If None is returned, the markup will
        be rendered unchanged.
      blog_style_endings
        If `True`, each newline character in a paragraph will be converted to
        a <br />. Note that the escaping mechanism (tilde) does not work
        for newlines.
        
    """

    return dialect_base(**kw_args)()



def creole10_base(wiki_links_base_url='',wiki_links_space_char='_',
                 interwiki_links_base_urls={},
                 no_wiki_monospace=True,
                 wiki_links_class_func=None,
                 wiki_links_path_func=None, interwiki_links_funcs={},
                 interwiki_links_space_chars={},
                 blog_style_endings=False,
                 ):
    """Returns a base class for extending
    (for parameter descriptions, see :func:`~creoleparser.dialects.create_dialect`)

    The returned class does not implement any of the proposed additions to
    to Creole 1.0 specification.

    """
        
    class Base(Dialect):

        br = LineBreak('br', r'\\',blog_style=blog_style_endings)
        headings = Heading(['h1','h2','h3','h4','h5','h6'],'=')
        no_wiki = NoWikiElement(no_wiki_monospace and 'code' or 'span',['{{{','}}}'])
        img = Image('img',('{{','}}'),delimiter='|')
        simple_element = SimpleElement(token_dict={'**':'strong','//':'em'})
        hr = LoneElement('hr','----')
        blank_line = BlankLine()
        p = Paragraph('p')
        pre = PreBlock('pre',['{{{','}}}'])
        raw_link = RawLink('a')
        
        link = Link('',('[[',']]'))
        url_link = URLLink('a',delimiter = '|',)
        interwiki_link = InterWikiLink('a',delimiter1=':',delimiter2='|',
                                            base_urls=interwiki_links_base_urls,
                                            links_funcs=interwiki_links_funcs,
                                            default_space_char=wiki_links_space_char,
                                            space_chars=interwiki_links_space_chars)
        wiki_link = WikiLink('a',delimiter = '|',base_url=wiki_links_base_url,
                              space_char=wiki_links_space_char,class_func=wiki_links_class_func,
                              path_func=wiki_links_path_func)

        td = TableCell('td','|')
        th = TableCell('th','|=')
        tr = TableRow('tr','|')
        table = Table('table','|')

        li = ListItem('li',list_tokens='*#')
        ol = List('ol','#',stop_tokens='*')
        ul = List('ul','*',stop_tokens='#')
        nested_ol = NestedList('ol','#')
        nested_ul = NestedList('ul','*')

        def __init__(self):
            self.link.child_elements = [self.url_link,self.interwiki_link,self.wiki_link]
            self.simple_element.child_elements = [self.simple_element]
            self.wiki_link.child_elements = [self.simple_element]
            self.interwiki_link.child_elements = [self.simple_element]
            self.url_link.child_elements = [self.simple_element]
            self.headings.child_elements = self.inline_elements
            self.p.child_elements = self.inline_elements
            self.td.child_elements = [self.br, self.raw_link, self.simple_element]
            self.th.child_elements = [self.br, self.raw_link, self.simple_element]
            self.tr.child_elements = [self.no_wiki,self.img,self.link,self.th,self.td]
            self.table.child_elements = [self.tr]
            self.ol.child_elements = [self.li]
            self.ul.child_elements = [self.li]
            self.nested_ol.child_elements = [self.li]
            self.nested_ul.child_elements = [self.li]
            self.li.child_elements = [(self.nested_ol,self.nested_ul)] + self.inline_elements

        @property 
        def inline_elements(self):
            return [self.no_wiki, self.img, self.link, self.br, self.raw_link, self.simple_element]

        @property 
        def block_elements(self):
            return [self.pre,self.blank_line,self.table,self.headings,
                               self.hr,self.ul,self.ol,self.p]
            """self.block_elements are the wiki elements that are searched at the top level of text to be
            processed. The order matters because elements later in the list need not have any
            knowledge of those before (as those were parsed out already). This makes the
            regular expression patterns for later elements very simple.
            """        

    return Base



def creole11_base(macro_func=None,**kwargs):
    """Returns a base class for extending (for parameter descriptions, see :func:`~creoleparser.dialects.create_dialect`)

    The returned class implements most of the *officially* proposed additions to
    to Creole 1.0 specification:

        * superscript, subscript, underline, and monospace
        * definition lists
        * macros
            
        (see http://purl.oclc.org/creoleparser/cheatsheet)

   **A Basic Extending Example**

   Here we create a dialect that alters the basic Creole inline syntax by
   removing underline and adding strike-though::

       >>> Base = creole11_base()
       >>> class MyDialect(Base):
       ...       simple_element = SimpleElement(token_dict={'**':'strong',
       ...                                                  '//':'em',
       ...                                                  ',,':'sub',
       ...                                                  '^^':'sup',
       ...                                                  '--':'del',
       ...                                                  '##':'code'})
       >>> from core import Parser
       >>> parser = Parser(MyDialect())
       >>> print parser.render("delete --this-- but don't underline __this__"),
       <p>delete <del>this</del> but don't underline __this__</p>
           
   For a more complex example, see the `source code of this function
   <http://code.google.com/p/creoleparser/source/browse/trunk/creoleparser/dialects.py>`_.
   It extends the class created from creole10_base().

   .. note::

       It is generally safest to create only one dialect instance per base
       class. This is because WikiElement objects are bound as class
       attributes and would therefor be shared between multiple instances,
       which could lead to unexpected behaviour.

    
    """
    
    Creole10Base = creole10_base(**kwargs)
    
    class Base(Creole10Base):
        
        simple_element = SimpleElement(token_dict={'**':'strong','//':'em',',,':'sub',
                                                  '^^':'sup','__':'u','##':'code'})
        dd = DefinitionDef('dd',':')
        dt = DefinitionTerm('dt',';',stop_token=':')
        dl = List('dl',';',stop_tokens='*#')

        macro = Macro('',('<<','>>'),func=macro_func)
        bodiedmacro = BodiedMacro('',('<<','>>'),func=macro_func)
        bodied_block_macro = BodiedBlockMacro('',('<<','>>'),func=macro_func)    

        def __init__(self):
            super(Base,self).__init__()
            self.tr.child_elements[0] = (self.no_wiki,self.bodiedmacro,self.macro)
            self.dd.child_elements = [self.br, self.raw_link, self.simple_element]
            self.dt.child_elements = [self.br, self.raw_link, self.simple_element]
            self.dl.child_elements = [(self.no_wiki,self.bodiedmacro,self.macro),self.img,self.link,self.dt,self.dd]
        
        @property 
        def inline_elements(self):
            return [(self.no_wiki,self.bodiedmacro,self.macro), self.img, self.link, self.br, self.raw_link, self.simple_element]

        @property 
        def block_elements(self):
            return [(self.bodied_block_macro,self.pre),self.blank_line,self.table,self.headings,
                           self.hr,self.dl,self.ul,self.ol,self.p]
    return Base



class Dialect(object):
    """Base class for dialect objects. Doesn't do anything."""
    pass


def Creole10(use_additions=False, **kwargs):
    warnings.warn("""
Use of Creole10 is depreciated, use create_dialect() instead. 
"""
                  )

    if use_additions:
        dialect_base = creole11_base
    else:
        dialect_base = creole10_base
        

    return create_dialect(dialect_base=dialect_base,**kwargs)
 
def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()    
