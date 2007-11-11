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

    def __init__(self,wiki_links_base_url='http://',wiki_links_space_char='_',
                 interwiki_links_base_urls={},
                 no_wiki_monospace=True, use_additions=False):
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
        """

        self.br = LineBreak('br', r'\\')
        self.http_link = RawLink('a')
        self.interwiki_link = InterWikiLink(delimiter=':',
                                            base_urls=interwiki_links_base_urls,
                                            space_char='_')
        self.wiki_link = WikiLink(base_url=wiki_links_base_url,
                                  space_char=wiki_links_space_char)
        self.img = Image('img',('{{','}}'),[],delimiter='|')
        self.link = Link('a',('[[',']]'),[],delimiter='|',
                        link_types=[self.http_link,self.interwiki_link,self.wiki_link])
        self.strong = InlineElement('strong', '**',[])
        self.em = InlineElement('em', '//',[])
        if no_wiki_monospace:
            no_wiki_tag = 'tt'
        else:
            no_wiki_tag = 'span'
        self.no_wiki = NoWikiElement(no_wiki_tag,['{{{','}}}'],[])
        
        self.em.child_tags = []
        self.strong.child_tags = [self.em]
        self.link.child_tags = [self.strong, self.em]
        header_children = [self.no_wiki, self.img, self.link, self.br, self.http_link, self.strong, self.em]
        table_cell_children = [self.br, self.http_link, self.strong, self.em]

        if use_additions:
            self.tt = InlineElement('tt', '##',[])
            self.em.child_tags.extend([self.tt])
            self.strong.child_tags.extend([self.tt])
            self.link.child_tags.extend([self.tt])
            header_children.extend([self.tt])
            table_cell_children.extend([self.tt])

            
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
            self.dd = DefinitionData('dd',':',[table_cell_children])
            self.dt = DefinitionTitle('dt',';',[table_cell_children],stop_token=':')
            self.dl = DefinitionList('dl',';',[self.no_wiki,self.img,self.link,self.dt,self.dd],stop_tokens='*#')
     
        self.li = ListItem('li',child_tags=[],list_tokens='*#')
        self.ol = List('ol','#',[self.li],other_token='*')
        self.ul = List('ul','*',[self.li],other_token='#')
        self.nested_ol = NestedList('ol','#',[self.li])
        self.nested_ul = NestedList('ul','*',[self.li])
        self.li.child_tags = [(self.nested_ol,self.nested_ul)] + header_children

        self.pre = PreBlock('pre',['{{{','}}}'])

        if use_additions:
            self.parse_order = [self.pre,self.blank_line,self.table]+ headings\
                           + [self.hr,self.dl,self.ul,self.ol,self.p]

        self.parse_order = [self.pre,self.blank_line,self.table]+ headings\
                           + [self.hr,self.ul,self.ol,self.p]
        """These are the wiki elements that are searched at the top level of text to be
        processed. The order matters because elements later in the list need not have any
        knowledge of those before (as those were parsed out already). This makes the
        regular expression patterns for later elements very simple.
        """
