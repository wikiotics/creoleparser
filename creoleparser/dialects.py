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
        #self.strong.child_tags = [self.em,self.br,self.link,self.img,self.http_link]
        #self.link.child_tags = [(self.strong, self.em), self.img]

##        if use_additions:
##            self.tt = InlineElement('tt', '##',[(self.strong,self.em,self.link),self.br,self.img,self.http_link])
##            self.strong.child_tags = [(self.em,self.tt,self.link),self.br,self.img,self.http_link]
##            self.em.child_tags = [(self.strong,self.tt,self.link),self.br,self.img,self.http_link]
##            self.link.child_tags = [(self.strong, self.em,self.tt), self.img]
##            header_children = [self.no_wiki,(self.strong, self.em, self.tt,self.link),
##                               self.br,self.img,self.http_link]
##
##        else:
##            self.em.child_tags = [(self.strong,self.link),self.br,self.img,self.http_link]
##            self.strong.child_tags = [(self.em,self.link),self.br,self.img,self.http_link]
##            self.link.child_tags = [(self.strong, self.em), self.img]
##            header_children = [self.no_wiki,(self.strong, self.em, self.link),
##                               self.br,self.img,self.http_link]

        if use_additions:
            self.tt = InlineElement('tt', '##',[self.strong,self.link,self.br,self.img,self.http_link,self.em])
            self.strong.child_tags = [self.tt,self.link,self.br,self.img,self.http_link,self.em]
            self.em.child_tags = [self.strong,self.tt,self.link,self.br,self.img,self.http_link]
            self.link.child_tags = [self.strong, self.tt, self.img,self.em]
            header_children = [self.no_wiki,self.strong, self.tt,self.link,
                               self.br,self.img,self.http_link,self.em]

        else:
            self.em.child_tags = [self.strong,self.link,self.br,self.img,self.http_link]
            self.strong.child_tags = [self.link,self.br,self.img,self.http_link,self.em]
            self.link.child_tags = [self.strong, self.img,self.em]
            header_children = [self.no_wiki,self.strong, self.link,
                               self.br,self.img,self.http_link,self.em]
            
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
        
        self.td = TableCell('td','|',header_children)
        self.th = TableCell('th','|=',header_children)
        self.tr = TableRow('tr','|',[self.th,self.td])
        self.table = Table('table','|',[self.tr])

        self.p = Paragraph('p',header_children)

        self.li = ListItem('li',child_tags=[],list_tokens='*#')
        self.ol = List('ol','#',[self.li],other_token='*')
        self.ul = List('ul','*',[self.li],other_token='#')
        self.nested_ol = NestedList('ol','#',[self.li])
        self.nested_ul = NestedList('ul','*',[self.li])
        self.li.child_tags = [(self.nested_ol,self.nested_ul)] + header_children

        self.pre = PreBlock('pre',['{{{','}}}'])

##        self.parse_order = [self.pre,self.blank_line,self.table]+ headings\
##                           + [self.hr,self.lone_br,self.ul,self.ol,self.p]
        self.parse_order = [self.pre,self.blank_line,self.table]+ headings\
                           + [self.hr,self.ul,self.ol,self.p]
        """These are the wiki elements that are searched at the top level of text to be
        processed. The order matters because elements later in the list need not have any
        knowledge of those before (as those were parsed out already). This makes the
        regular expression patterns for later elements very simple.
        """
