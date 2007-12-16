# dialects.py
#
# Copyright (c) 2007 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

from elements import *

class Creole10(object):

    """This class contains most of the logic and specification of the markup."""

    def __init__(self,wiki_links_base_url='',wiki_links_space_char='_',
                 interwiki_links_base_urls={},
                 no_wiki_monospace=True, use_additions=False,
                 wiki_links_class_func=None, macro_func=None,
                 wiki_links_path_func=None):
        """Constructor for Creole10 oblects.

        Most attributes of new Creole objects are derived from the WikiElement
        class. Please see the constructor of that class and other specific element
        classes for details.

        :parameters:
          wiki_links_base_url
            self explanitory
          wiki_links_space_char
            When wiki_links have spaces, this character replaces those spaces in
            the url. 
          interwiki_links_base_urls
            Dictionary of urls for interwiki links.
          no_wiki_monospace
            If ``True``, inline no_wiki will be rendered as <tt> not <span>
          use_additions
            If ``True``, markup beyond the Creole 1.0 spec will be allowed.
            Including monospace (##).
          wiki_links_class_func
            If supplied, this fuction will be called when a wiki link is found and
            the return value (should be a string) will be added as a class attribute
            of the cooresponding link. The function must accept the page name (any
            spaces will have been replaced THIS IS NEW IN 0.3.3) as it's only argument.
            If no class attribute is to be added, return no value (or None).
          wiki_links_path_func
            If supplied, this fuction will be called when a wiki link is found and
            the return value (should be a string) will be joined to the base_url
            to form the url for href. The function must accept the page name (any
            spaces will have been replaced) as it's only argument. Returning the
            unaltered page name is equivalent to not supplying this function at all.
          macro_func
            If supplied, this fuction will be called when macro markup is found. The
            function must accept the macro name (lower_case and hyphens only) as its
            first argument, the argument string (including any delimter) as the second,
            and the macro body as it's third (will be None for a macro without a body).
            The function may return a string (which will be subject to further wiki
            processing) or a Genshi Stream object. If None is returned, the markup will
            be rendered unchanged.
            Examples:
            1) <<macro-name arg_string>>the body<</macro-name>>
            2) <<macro-name I have no body, just this argument string>>
                      
         """
        self.macro = Macro('',('<<','>>'),[],func=macro_func)
        self.bodiedmacro = BodiedMacro('',('<<','>>'),[],func=macro_func)
        self.br = LineBreak('br', r'\\')
        self.raw_link = RawLink('a')
        self.url_link = URLLink('a','',[],delimiter = '|')
        self.interwiki_link = InterWikiLink('a','',[],delimiter1=':',delimiter2='|',
                                            base_urls=interwiki_links_base_urls,
                                            space_char='_')
        self.wiki_link = WikiLink('a','',[],delimiter = '|', base_url=wiki_links_base_url,
                                  space_char=wiki_links_space_char,class_func=wiki_links_class_func,
                                  path_func=wiki_links_path_func)
        self.img = Image('img',('{{','}}'),[],delimiter='|')
        self.link = Link('',('[[',']]'),[self.url_link,self.interwiki_link,self.wiki_link])
        self.strong = InlineElement('strong', '**',[])
        self.em = InlineElement('em', '//',[])
        if no_wiki_monospace:
            no_wiki_tag = 'tt'
        else:
            no_wiki_tag = 'span'
        self.no_wiki = NoWikiElement(no_wiki_tag,['{{{','}}}'],[])
        
        self.em.child_tags = []
        self.strong.child_tags = [self.em]
        link_child_tags = [self.strong, self.em]
        header_children = [self.no_wiki, self.img, self.link, self.br, self.raw_link, self.strong, self.em]
        table_cell_children = [self.br, self.raw_link, self.strong, self.em]

        if use_additions:
            self.sub = InlineElement('sub', ',,',[])
            self.sup = InlineElement('sup', '^^',[self.sub])
            self.u = InlineElement('u', '__',[self.sup, self.sub])
            self.tt = InlineElement('tt', '##',[self.u, self.sup, self.sub])
            self.em.child_tags.extend([self.tt, self.u, self.sup, self.sub])
            self.strong.child_tags.extend([self.tt, self.u, self.sup, self.sub])
            link_child_tags.extend([self.tt, self.u, self.sup, self.sub])
            header_children.extend([self.tt, self.u, self.sup, self.sub])
            table_cell_children.extend([self.tt, self.u, self.sup, self.sub])

        self.wiki_link.child_tags = link_child_tags
        self.url_link.child_tags = link_child_tags
        self.interwiki_link.child_tags = link_child_tags

            
        self.hr = LoneElement('hr','----',[])
        #self.lone_br = LoneElement('br',r'\\',[])
        self.blank_line = BlankLine()

        self.h1 = Heading('h1','=',header_children)
        self.h2 = Heading('h2','==',header_children)
        self.h3 = Heading('h3','===',header_children)
        self.h4 = Heading('h4','====',header_children)
        self.h5 = Heading('h5','=====',header_children)
        self.h6 = Heading('h6','======',header_children)

        headings = [self.h1,self.h2,self.h3,self.h4,self.h5,self.h6]

        self.td = TableCell('td','|',table_cell_children)
        self.th = TableCell('th','|=',table_cell_children)
        self.tr = TableRow('tr','|',[self.no_wiki,self.img,self.link,self.th,self.td])
        self.table = Table('table','|',[self.tr])

        self.p = Paragraph('p',header_children)

        if use_additions:
            self.dd = DefinitionDef('dd',':',[table_cell_children])
            self.dt = DefinitionTerm('dt',';',[table_cell_children],stop_token=':')
            self.dl = List('dl',';',[self.no_wiki,self.img,self.link,self.dt,self.dd],stop_tokens='*#')
     
        self.li = ListItem('li',child_tags=[],list_tokens='*#')
        self.ol = List('ol','#',[self.li],stop_tokens='*')
        self.ul = List('ul','*',[self.li],stop_tokens='#')
        self.nested_ol = NestedList('ol','#',[self.li])
        self.nested_ul = NestedList('ul','*',[self.li])
        self.li.child_tags = [(self.nested_ol,self.nested_ul)] + header_children

        self.pre = PreBlock('pre',['{{{','}}}'])

        if use_additions:
            self.parse_order = [self.bodiedmacro,self.macro,self.pre,self.blank_line,self.table]+ headings\
                           + [self.hr,self.dl,self.ul,self.ol,self.p]
        else:
            self.parse_order = [self.bodiedmacro,self.macro,self.pre,self.blank_line,self.table]+ headings\
                           + [self.hr,self.ul,self.ol,self.p]
        """These are the wiki elements that are searched at the top level of text to be
        processed. The order matters because elements later in the list need not have any
        knowledge of those before (as those were parsed out already). This makes the
        regular expression patterns for later elements very simple.
        """
