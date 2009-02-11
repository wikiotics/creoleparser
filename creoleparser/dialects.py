# dialects.py
#
# Copyright (c) 2009 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

from elements import *

class Creole10(object):
    """Constructor for Creole10 objects

    :parameters:
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
        If `True`, inline no_wiki will be rendered as <tt> not <span>
      use_additions
        If `True`, markup beyond the Creole 1.0 spec will be allowed
        (see http://purl.oclc.org/creoleparser/cheatsheet)
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
        function must accept the macro name as its first argument, the argument
        string (including any delimter) as the second, the macro body as its
        third (will be None for a macro without a body), and a Boolean as the
        fourth (True for Block type macros, False for normal macros).
        The function may return a string (which will be subject to further wiki
        processing) or a Genshi object (Stream, Markup, builder.Fragment, or
        builder.Element). If None is returned, the markup will
        be rendered unchanged.
      blog_line_endings
        If `True`, each newline character in a paragraph will be converted to
        a <br />. Note that the normal escaping mechanism (tilde) does not work
        for newlines, instead use a space before a newline to surpress <br />'s.
      simple_tokens
        A dictionary of rules for simple inline markup. If present, the
        `use_additions` option will not affect inline markup. If None, the
        following default dictionary is used (and `use_additions` may add to it)::
        
           {'**':'strong','//':'em'}
        
                   
    """

    def __init__(self,wiki_links_base_url='',wiki_links_space_char='_',
                 interwiki_links_base_urls={},
                 no_wiki_monospace=True, use_additions=False,
                 wiki_links_class_func=None, macro_func=None,
                 wiki_links_path_func=None, interwiki_links_funcs={},
                 interwiki_links_space_chars={},
                 blog_line_endings=False,
                 simple_tokens=None,
                 ):
        self.macro = Macro('',('<<','>>'),[],func=macro_func)
        self.bodiedmacro = BodiedMacro('',('<<','>>'),[],func=macro_func)
        self.block_macro = BlockMacro('',('<<','>>'),[],func=macro_func)
        self.bodied_block_macro = BodiedBlockMacro('',('<<','>>'),[],func=macro_func)
        self.br = LineBreak('br', r'\\',blog_like=blog_line_endings)
        self.raw_link = RawLink('a')
        self.url_link = URLLink('a','',[],delimiter = '|')
        self.interwiki_link = InterWikiLink('a','',[],delimiter1=':',delimiter2='|',
                                            base_urls=interwiki_links_base_urls,
                                            links_funcs=interwiki_links_funcs,
                                            default_space_char=wiki_links_space_char,
                                            space_chars=interwiki_links_space_chars)
        self.wiki_link = WikiLink('a','',[],delimiter = '|', base_url=wiki_links_base_url,
                                  space_char=wiki_links_space_char,class_func=wiki_links_class_func,
                                  path_func=wiki_links_path_func)
        self.img = Image('img',('{{','}}'),[],delimiter='|')
        self.link = Link('',('[[',']]'),[self.url_link,self.interwiki_link,self.wiki_link])

        if simple_tokens is not None:
            simple_token_dict = simple_tokens
        else:
            simple_token_dict = {'**':'strong','//':'em'}
            if use_additions:
                simple_token_dict.update({',,':'sub','^^':'sup','__':'u','##':'code'})
            
        self.simple_elements = SimpleElement('','',[],simple_token_dict)
        self.simple_elements.child_tags = [self.simple_elements]
        
        if no_wiki_monospace:
            no_wiki_tag = 'code'
        else:
            no_wiki_tag = 'span'
        self.no_wiki = NoWikiElement(no_wiki_tag,['{{{','}}}'],[])
        
        link_child_tags = [self.simple_elements]
        inline_elements = [self.no_wiki, self.img, self.link, self.br, self.raw_link, self.simple_elements]
        table_cell_children = [self.br, self.raw_link, self.simple_elements]

        if use_additions:
            inline_elements[0] = (self.no_wiki,self.bodiedmacro,self.macro)

        self.wiki_link.child_tags = link_child_tags
        self.url_link.child_tags = link_child_tags
        self.interwiki_link.child_tags = link_child_tags
            
        self.hr = LoneElement('hr','----',[])
        #self.lone_br = LoneElement('br',r'\\',[])
        self.blank_line = BlankLine()
        self.lone_place_holder = LonePlaceHolder('',['<<<','>>>'],[])

        self.headings = Heading('','=',inline_elements,tags=['h1','h2','h3','h4','h5','h6'])

        self.td = TableCell('td','|',table_cell_children)
        self.th = TableCell('th','|=',table_cell_children)
        if use_additions:
            self.tr = TableRow('tr','|',[(self.no_wiki,self.bodiedmacro,self.macro),self.img,self.link,self.th,self.td])
        else:
            self.tr = TableRow('tr','|',[self.no_wiki,self.img,self.link,self.th,self.td])
        self.table = Table('table','|',[self.tr])

        self.p = Paragraph('p',inline_elements)

        if use_additions:
            self.dd = DefinitionDef('dd',':',table_cell_children)
            self.dt = DefinitionTerm('dt',';',table_cell_children,stop_token=':')
            self.dl = List('dl',';',[(self.no_wiki,self.bodiedmacro,self.macro),self.img,self.link,self.dt,self.dd],stop_tokens='*#')
     
        self.li = ListItem('li',child_tags=[],list_tokens='*#')
        self.ol = List('ol','#',[self.li],stop_tokens='*')
        self.ul = List('ul','*',[self.li],stop_tokens='#')
        self.nested_ol = NestedList('ol','#',[self.li])
        self.nested_ul = NestedList('ul','*',[self.li])
        self.li.child_tags = [(self.nested_ol,self.nested_ul)] + inline_elements
        self.pre = PreBlock('pre',['{{{','}}}'])
        self.inline_elements = inline_elements
        if use_additions:
            self.block_elements = [(self.bodied_block_macro,self.pre,self.block_macro),
                                   self.blank_line,self.table,self.headings,self.hr,
                                   self.dl,self.ul,self.ol,self.lone_place_holder,self.p]

        else:
            self.block_elements = [self.pre,self.blank_line,self.table,self.headings,
                           self.hr,self.ul,self.ol,self.lone_place_holder,self.p]
        """These are the wiki elements that are searched at the top level of text to be
        processed. The order matters because elements later in the list need not have any
        knowledge of those before (as those were parsed out already). This makes the
        regular expression patterns for later elements very simple.
        """







class Dialect(object):
    """

    """

    def __init__(self):

        self.link.child_tags = [self.url_link,self.interwiki_link,self.wiki_link]

           
        self.simple_elements.child_tags = [self.simple_elements]
        
      
        link_child_tags = [self.simple_elements]
        inline_elements = [self.no_wiki, self.img, self.link, self.br, self.raw_link, self.simple_elements]
        table_cell_children = [self.br, self.raw_link, self.simple_elements]

        if self.use_additions:
            inline_elements[0] = (self.no_wiki,self.bodiedmacro,self.macro)

        self.wiki_link.child_tags = link_child_tags
        self.url_link.child_tags = link_child_tags
        self.interwiki_link.child_tags = link_child_tags
            
        self.headings.child_tags = inline_elements

        self.td.child_tags = table_cell_children
        self.th.child_tags = table_cell_children
        if self.use_additions:
            self.tr.child_tags = [(self.no_wiki,self.bodiedmacro,self.macro),self.img,self.link,self.th,self.td]
        else:
            self.tr.child_tags = [self.no_wiki,self.img,self.link,self.th,self.td]
        self.table.child_tags = [self.tr]

        self.p.child_tags = inline_elements

        if self.use_additions:
            self.dd.child_tags = table_cell_children
            self.dt.child_tags = table_cell_children
            self.dl.child_tags = [(self.no_wiki,self.bodiedmacro,self.macro),self.img,self.link,self.dt,self.dd]
     
        self.ol.child_tags = [self.li]
        self.ul.child_tags = [self.li]
        self.nested_ol.child_tags = [self.li]
        self.nested_ul.child_tags = [self.li]
        self.li.child_tags = [(self.nested_ol,self.nested_ul)] + inline_elements
        self.inline_elements = inline_elements
        if self.use_additions:
            self.block_elements = [(self.bodied_block_macro,self.pre,self.block_macro),
                                   self.blank_line,self.table,self.headings,self.hr,
                                   self.dl,self.ul,self.ol,self.lone_place_holder,self.p]

        else:
            self.block_elements = [self.pre,self.blank_line,self.table,self.headings,
                           self.hr,self.ul,self.ol,self.lone_place_holder,self.p]
        """These are the wiki elements that are searched at the top level of text to be
        processed. The order matters because elements later in the list need not have any
        knowledge of those before (as those were parsed out already). This makes the
        regular expression patterns for later elements very simple.
        """

    wiki_links_base_url=''
    wiki_links_space_char='_'
    interwiki_links_base_urls={}
    no_wiki_monospace=True
    use_additions=False
    wiki_links_class_func=None
    macro_func=None
    wiki_links_path_func=None
    interwiki_links_funcs={}
    interwiki_links_space_chars={}

    macro = Macro('',('<<','>>'),[],func=macro_func)
    bodiedmacro = BodiedMacro('',('<<','>>'),[],func=macro_func)
    block_macro = BlockMacro('',('<<','>>'),[],func=macro_func)
    bodied_block_macro = BodiedBlockMacro('',('<<','>>'),[],func=macro_func)
    br = LineBreak('br', r'\\')
    raw_link = RawLink('a')
    url_link = URLLink('a','',[],delimiter = '|')
    interwiki_link = InterWikiLink('a','',[],delimiter1=':',delimiter2='|',
                                        base_urls=interwiki_links_base_urls,
                                        links_funcs=interwiki_links_funcs,
                                        default_space_char=wiki_links_space_char,
                                        space_chars=interwiki_links_space_chars)
    wiki_link = WikiLink('a','',[],delimiter = '|', base_url=wiki_links_base_url,
                              space_char=wiki_links_space_char,class_func=wiki_links_class_func,
                              path_func=wiki_links_path_func)
    img = Image('img',('{{','}}'),[],delimiter='|')
    link = Link('',('[[',']]'),[])

    simple_token_dict = {'**':'strong','//':'em'}
    if use_additions:
        simple_token_dict.update({',,':'sub','^^':'sup','__':'u','##':'tt'})
        
    simple_elements = SimpleElement('','',[],simple_token_dict)
    
    if no_wiki_monospace:
        no_wiki_tag = 'tt'
    else:
        no_wiki_tag = 'span'
    no_wiki = NoWikiElement(no_wiki_tag,['{{{','}}}'],[])
    
    hr = LoneElement('hr','----',[])
    blank_line = BlankLine()
    lone_place_holder = LonePlaceHolder('',['<<<','>>>'],[])

    headings = Heading('','=',[],tags=['h1','h2','h3','h4','h5','h6'])

    td = TableCell('td','|',[])
    th = TableCell('th','|=',[])
    if use_additions:
        tr = TableRow('tr','|',[])
    else:
        tr = TableRow('tr','|',[])
    table = Table('table','|',[])

    p = Paragraph('p',[])

    if use_additions:
        dd = DefinitionDef('dd',':',[])
        dt = DefinitionTerm('dt',';',[],stop_token=':')
        dl = List('dl',';',[],stop_tokens='*#')
 
    li = ListItem('li',child_tags=[],list_tokens='*#')
    ol = List('ol','#',[],stop_tokens='*')
    ul = List('ul','*',[],stop_tokens='#')
    nested_ol = NestedList('ol','#',[])
    nested_ul = NestedList('ul','*',[])
    pre = PreBlock('pre',['{{{','}}}'])
