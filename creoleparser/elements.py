# elements.py
#
# Copyright (c) 2007 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

import re

import genshi.builder as bldr

from core import escape_char, esc_neg_look, fragmentize, element_store


__docformat__ = 'restructuredtext en'

class WikiElement(object):
    
    """Baseclass for all wiki WikiElements."""
    
    append_newline = False
    """Determines if newlines are appended to Element(s) during processing.
    Should only affect readability of source xml.
    """
    
    def __init__(self, tag, token, child_tags):
        """Constructor for WikiElement objects.

        Subclasses may have other keyword arguments.   

        :parameters:
          tag
            The xhtml tag associated with the element.
          token
            The character string (or strings) that identifies the element
            in wiki markup.
          child_tags
            A list of wiki_elements that will be searched for in the body of the
            element.  The order of these elements matters, because if an element is
            found before the element that encloses it, the enclosing element will
            never be found.  In cases where this imposes limits (e.g, ``strong`` and
            ``em`` should be allowed to nest each other), place the conflicting
            elements in a sublist. The parser will then find which comes first.
        """
        self.tag = tag
        self.token = token
        self.child_tags = child_tags
                
    def _build(self,mo):
        """Returns a genshi Element that has ``self.tag`` as the
        outermost tag.

        This methods if called exclusively by ``fragmentize``

        :parameters:
          mo
            match object, usually the one returned by
            self.regexp.search(s) 
        """
        return bldr.tag.__getattr__(self.tag)(fragmentize(mo.group(1),
                                                          self.child_tags))

    def re_string(self):
        """The regular expression pattern that is compiled into ``self.regexp``.

        The regular expression must consume the entire wiki element,
        including the tokens. For block elements, the newline on the last
        line must be consumed also. group(1) should normally be the
        entire string inside the tokens. If not, a custom ``_build``
        method will be needed.
        """
        pass

    def _process(self, mo, text, wiki_elements):
        """Returns genshi Fragments (Elements and text)

        This is mainly for block level markup. See InlineElement
        for the other method.
        """
        frags = []
        # call again for leading text and extend the result list 
        if mo.start():
            frags.extend(fragmentize(text[:mo.start()],wiki_elements[1:]))
        # append the found wiki element to the result list
        frags.append(self._build(mo))
        # make the source output easier to read
        if self.append_newline:
            frags.append('\n')
        # call again for trailing text and extend the result list
        if mo.end() < len(text):
            frags.extend(fragmentize(text[mo.end():],wiki_elements))
        return frags
        
    def __repr__(self):
        return "<WikiElement "+str(self.tag)+">"

class InlineElement(WikiElement):

    r"""For finding generic inline elements like ``strong`` and ``em``.

    >>> em = InlineElement('em','//',[])
    >>> mo1 = em.regexp.search('a //word// in a line')
    >>> mo2 = em.regexp.search('a //word in a line\n or two\n')
    >>> mo1.group(0),mo1.group(1)
    ('//word//', 'word')
    >>> mo2.group(0),mo2.group(1)
    ('//word in a line\n or two', 'word in a line\n or two')

    Use a list for the ``token`` argument to have different start
    and end strings. These must be closed.

    >>> foo = InlineElement('foo',['<<','>>'],[])
    >>> mo = foo.regexp.search('blaa <<here it is >>\n')
    >>> mo.group(1)
    'here it is '
        
    """

    def __init__(self, tag, token, child_tags=[]):
        super(InlineElement,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL)

    def re_string(self):
        if isinstance(self.token,str):
            content = '(.+?)'
            end = '(' + esc_neg_look + re.escape(self.token) + r'|$)'
            return esc_neg_look + re.escape(self.token) + content + end
        else:
            content = '(.+?)'
            return esc_neg_look + re.escape(self.token[0]) + content + esc_neg_look + re.escape(self.token[1])

    def _process(self, mo, text, wiki_elements):
        """Returns genshi Fragments (Elements and text)"""
        processed = self._build(mo)
        store_id = str(id(processed)) # str(hash(processed))
        element_store.d[store_id] = processed
        text = ''.join([text[:mo.start()],'<<<',store_id,'>>>',
                        text[mo.end():]])
        frags = fragmentize(text,wiki_elements)
        return frags


class RawLink(InlineElement):
    
    """Used to find raw urls in wiki text and build xml from them.

    >>> raw_link = RawLink(tag='a')
    >>> mo = raw_link.regexp.search(" a http://www.google.com url ")
    >>> raw_link.href(mo)
    'http://www.google.com'
    >>> raw_link._build(mo).generate().render()
    '<a href="http://www.google.com">http://www.google.com</a>'
    
    """

    def __init__(self, tag):
        super(RawLink,self).__init__(tag=tag, token=None, child_tags=None)
        self.regexp = re.compile(self.re_string())

    def re_string(self):
        escape = '(' + re.escape(escape_char) + ')?'
        protocol = '(https?://'
        rest_of_url = r'\S+?)'
        #allow one punctuation character or '**' or '//'
        look_ahead = r'(?=([,.?!:;"\']|\*\*|//)?(\s|$))' 
        return escape + protocol + rest_of_url + look_ahead

    def _build(self,mo):
        if not mo.group(1):
            return bldr.tag.__getattr__(self.tag)(self.alias(mo),
                                              href=self.href(mo))
        else:
            return self.href(mo)
        
    def href(self,mo):
        """Returns the string for the href attribute of the Element."""
        return mo.group(2)

    def alias(self,mo):
        """Returns the string for the content of the Element."""
        return self.href(mo)


class InterWikiLink(InlineElement):

    """Used to find interwiki links and return a href and alias.

    The search scope for these is only inside wiki links,
    before the pipe(|)! 

    >>> interwiki_link = InterWikiLink(delimiter=':',
    ... base_urls=dict(somewiki='http://somewiki.org/',
    ...                bigwiki='http://bigwiki.net/'),
    ...                space_char='_')
    >>> mo = interwiki_link.regexp.search(" somewiki:Home Page ")
    >>> interwiki_link.href(mo)
    'http://somewiki.org/Home_Page'
    >>> interwiki_link.alias(mo)
    'somewiki:Home Page'
    
    """

    def __init__(self,delimiter,base_urls,space_char):
        self.delimiter = delimiter
        self.regexp = re.compile(self.re_string())
        self.base_urls = base_urls
        self.space_char = space_char

    def re_string(self):
        wiki_id = r'(\w+)'
        optional_spaces = ' *'
        page_name = r'(\S+( +\S+)*)' #allows any number of single spaces 
        return wiki_id + optional_spaces + re.escape(self.delimiter) + \
               optional_spaces + page_name + optional_spaces + '$'

    def href(self,mo):
        base_url = self.base_urls.get(mo.group(1))
        if not base_url:
            return None
        return base_url + mo.group(2).replace(' ',self.space_char)

    def alias(self,mo):
        return ''.join([mo.group(1),self.delimiter,mo.group(2)])


class WikiLink(InlineElement):

    """Used to find wiki links and return a href and alias.

    The search scope for these is only inside wiki links, before the pipe(|)

    >>> wiki_link = WikiLink(base_url='http://somewiki.org/',
    ...                      space_char='_')
    >>> mo = wiki_link.regexp.search(" Home Page ")
    >>> wiki_link.href(mo)
    'http://somewiki.org/Home_Page'
    >>> wiki_link.alias(mo)
    'Home Page'
    
    """

    def __init__(self,base_url,space_char):
        self.regexp = re.compile(self.re_string())
        self.base_url = base_url
        self.space_char = space_char

    def re_string(self):
        optional_spaces = ' *'
        page_name = r'(\S+( +\S+)*)' #allows any number of single spaces 
        return optional_spaces + page_name + optional_spaces + '$' 

    def href(self,mo):
        return self.base_url + mo.group(1).replace(' ',self.space_char)

    def alias(self,mo):
        return mo.group(1)


class BlockElement(WikiElement):

    """Block elements inherit form this class

    Wiki elements wanting ``append_newline = True`` should use this
    as the base also.

    """

    append_newline = True


class List(BlockElement):

    """Finds list (ordered, unordered, and definition) wiki elements.

    group(1) of the match object includes all lines from the list
    including newline characters.
        
    """

    def __init__(self, tag, token,child_tags,stop_tokens):
        super(List,self).__init__(tag, token, child_tags)
        self.stop_tokens = stop_tokens
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)

    def re_string(self):
        """This re_string is for finding generic block elements like
        lists (ordered, unordered, and definition) that start with a
        single token.
        """
        leading_whitespace = r'^([ \t]*'
        only_one_token = re.escape(self.token)+'[^'+ re.escape(self.token) + ']'
        rest_of_list = r'.*?\n)'
##        only_one_other_token = re.escape(self.other_token)+'(?!'+ \
##                               re.escape(self.other_token) + ')'
        only_one_stop_token = '([' + re.escape(self.stop_tokens) + r'])(?!\3)'        
        look_ahead = '(?=([ \t]*' + only_one_stop_token + '|$))'
        return leading_whitespace + only_one_token + rest_of_list + \
               look_ahead


class ListItem(WikiElement):
    r"""Matches the current list item.

    Everything up to the next same-level list item is matched.

    >>> list_item = ListItem('li',[],'#*')
    >>> mo = list_item.regexp.search("*one\n**one.1\n**one.2\n*two\n")
    >>> mo.group(2)
    'one\n**one.1\n**one.2\n'
    >>> mo.group(0)
    '*one\n**one.1\n**one.2\n'
    
    """
    
    append_newline = True

    def __init__(self, tag, child_tags, list_tokens):
        """Constructor for list items.

        :parameters"
          list_tokens
            A string that includes the tokens used for lists
        """
        super(ListItem,self).__init__(tag, token=None,
                                      child_tags=child_tags)
        self.list_tokens = list_tokens
        self.regexp = re.compile(self.re_string(),re.DOTALL)

    def re_string(self):
        whitespace = r'\s*'
        item_start = '([*#]+)'
        rest_of_item = r'(.*?\n)'
        start_of_same_level_item = r'\1(?![*#])'
        look_ahead = '(?=(' + whitespace + start_of_same_level_item + '|$))'
        return whitespace + item_start + whitespace + '?' + \
               rest_of_item + look_ahead

    def _build(self,mo):
        return bldr.tag.__getattr__(self.tag)(fragmentize(mo.group(2),
                                                          self.child_tags))


class NestedList(WikiElement):

    r"""Finds a list in the current list item.

    >>> nested_ul = NestedList('ul','*',[])
    >>> mo = nested_ul.regexp.search('one\n**one.1\n**one.2\n')
    >>> mo.group(1)
    '**one.1\n**one.2\n'
    >>> mo.group(0) == mo.group(1)
    True

    """

    def __init__(self, tag, token,child_tags):
        super(NestedList,self).__init__(tag, token, child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)

    def re_string(self):
        look_behind = r'(?<=\n)' # have to avoid finding a list on the first line
        whitespace = r'(\s*'
        rest_of_list = '.*$)'
        return look_behind + '^' + whitespace + re.escape(self.token) + \
               rest_of_list


class DefinitionTerm(BlockElement):

    r"""Processes definition terms.

    >>> term = DefinitionTerm('dt',';',[],stop_token=':')
    >>> mo1,mo2 = term.regexp.finditer(";term1\n:def1\n;term2:def2\n")
    >>> mo1.group(1), mo2.group(1)
    ('term1', 'term2')
    >>> mo1.group(0), mo2.group(0)
    (';term1\n', ';term2')

    group(1) of the match object is the term line or up to the first ':'
        
    """

    def __init__(self, tag, token,child_tags,stop_token):
        super(DefinitionTerm,self).__init__(tag, token, child_tags)
        self.stop_token = stop_token
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)

    def re_string(self):
        leading_whitespace = r'^([ \t]*'
        #only_one_token = re.escape(self.token)+'[^'+ re.escape(self.token) + ']'
        rest_of_list = r'.*?\n)'
        #only_one_stop_token = '([' + re.escape(self.stop_tokens) + r'])(?!\3)'
        #look_ahead = r'(?=([ \t]*' + only_one_stop_token + '|$))'
        return r'^[ \t]*' + re.escape(self.token) + r'[ \t]*(.*?' + \
               re.escape(self.stop_token) +  '?)\s*(\n|(?=(' + \
               esc_neg_look + re.escape(self.stop_token) + r'|$)))'


class DefinitionDef(BlockElement):

    r"""Processes definitions.

    >>> definition = DefinitionDef('dd',':',[])
    >>> mo1,mo2 = definition.regexp.finditer(":def1a\ndef1b\n:def2\n")
    >>> mo1.group(1), mo2.group(1)
    ('def1a\ndef1b', 'def2')
    >>> mo1.group(0), mo2.group(0)
    (':def1a\ndef1b\n', ':def2\n')

    group(1) of the match object includes all lines from the defintion
    up to the next definition.
        
    """

    def __init__(self, tag, token,child_tags):
        super(DefinitionDef,self).__init__(tag, token, child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)

    def re_string(self):
        leading_whitespace = r'^([ \t]*'
        rest_of_list = r'.*?\n)'
        look_ahead = r'(?=([ \t]*' + re.escape(self.token) + r')|$)'
        return r'^[ \t]*' + re.escape(self.token) + r'?[ \t]*(.+?)\s*\n(?=([ \t]*' + \
               re.escape(self.token) + r')|$)'


class Paragraph(BlockElement):

    """"This should be the last outer level wiki element to be "searched".

    Anything that is left over will be placed in paragraphs.

    """

    def __init__(self, tag, child_tags):
        super(Paragraph,self).__init__(tag,token=None, child_tags=child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)

    def re_string(self):
        return r'^(.*)\n'


class Heading(BlockElement):

    r"""Finds heading wiki elements.

    >>> h1 = Heading('h1','=',[])
    >>> mo = h1.regexp.search('before\n = An important thing = \n after')
    >>> mo.group(1)
    'An important thing'
    >>> mo.group(0)
    ' = An important thing = \n'

    """
  
    def __init__(self, tag, token, child_tags):
        super(Heading,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.MULTILINE)

    def re_string(self):
        whitespace = r'[ \t]*'
        neg_look_ahead = '(?!' + re.escape(self.token[0]) + ')'
        content = '(.*?)'
        trailing_markup = '(' + re.escape(self.token[0]) + r'+[ \t]*)?\n'
        return '^' + whitespace + re.escape(self.token) + neg_look_ahead + \
               whitespace + content + whitespace + trailing_markup


class Table(BlockElement):

    r"""Find tables.

    >>> table = Table('table','|',[])
    >>> mo = table.regexp.search("before\n | one | two |\n|one|two \n hi")
    >>> mo.group(1)
    ' | one | two |\n|one|two \n'
    >>> mo.group(0) == mo.group(1)
    True
    
    """

    def __init__(self, tag, token, child_tags=[]):
        super(Table,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.MULTILINE)

    def re_string(self):
        whitespace = r'[ \t]*'
        rest_of_line = r'.*?\n'
        return '^((' + whitespace + re.escape(self.token) + \
               rest_of_line + ')+)'


class TableRow(BlockElement):

    r"""Finds rows in a table.

    >>> row = TableRow('tr','|',[])
    >>> mo = row.regexp.search(' | one | two |\n|one|two \n')
    >>> mo.group(1)
    '| one | two '
    >>> mo.group(0)
    ' | one | two |\n'
    
    """

    def __init__(self, tag, token, child_tags=[]):
        super(TableRow,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.MULTILINE)

    def re_string(self):
        whitespace = r'[ \t]*'
        content = '(' + re.escape(self.token) + '.*?)'
        trailing_token = re.escape(self.token) + '?'
        return '^' + whitespace + content + trailing_token + \
               whitespace + r'\n'


class TableCell(WikiElement):

    r"""Finds cells in a table row.

    >>> cell = TableCell('td','|',[])
    >>> mo = cell.regexp.search('| one | two ')
    >>> mo.group(1)
    'one'
    >>> mo.group(0)
    '| one '
    
    """

    def __init__(self, tag, token, child_tags=[]):
        super(TableCell,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string())

    def re_string(self):
        whitespace = r'[ \t]*'
        content = '(.*?)'
        look_ahead = '((?=' + esc_neg_look + re.escape(self.token[0]) + ')|$)'
        return esc_neg_look + re.escape(self.token) + whitespace + \
               content + whitespace + look_ahead    



class Link(InlineElement):

    """Finds and builds links."""
    
    def __init__(self, tag, token, child_tags, delimiter,link_types):
        super(Link,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string())
        self.delimiter = delimiter
        self.link_types = link_types
        
    def _build(self,mo):
        body = mo.group(1).split(self.delimiter, 1)
        link = body[0]
        if len(body) == 1:
            alias = None
        else:
            alias = body[1].strip()
        for link_type in self.link_types:
            link_mo = link_type.regexp.search(link)
            if link_mo:
                href = link_type.href(link_mo)
                break
        if not link_mo:
            return bldr.tag.span('Bad Link - ',link)
        if not alias:
            alias = link_type.alias(link_mo)
        else:
            alias = fragmentize(alias,self.child_tags)
        return bldr.tag.__getattr__(self.tag)(alias ,href=link_type.href(link_mo))


class Image(InlineElement):

    """Processes image elements.

    >>> img = Image('img',('{{','}}'),[], delimiter='|')
    >>> mo = img.regexp.search('{{ picture.jpg | An image of a house }}')
    >>> img._build(mo).generate().render()
    '<img src="picture.jpg" alt="An image of a house"/>'

    """

    def __init__(self, tag, token, child_tags,delimiter):
        super(Image,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string())
        self.delimiter = delimiter
        self.src_regexp = re.compile(r'^\s*(\S+)\s*$')

    def _build(self,mo):
        body = mo.group(1).split(self.delimiter,1)
        src_mo = self.src_regexp.search(body[0])
        if not src_mo:
            return bldr.tag.span('Bad Image src')
        link = src_mo.group(1)
        if len(body) == 1:
            alias = link
        else:
            alias = body[1].strip()
        return bldr.tag.__getattr__(self.tag)(src=link ,alt=alias)


class NoWikiElement(InlineElement):

    """Inline no-wiki.

    When two or more end tokens are found together, only last marks
    the end of the element.

    This element must be on a single line.
    
    """

    def __init__(self, tag, token, child_tags=[]):
        super(NoWikiElement,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL) 

    def _build(self,mo):
        if self.tag:
            return bldr.tag.__getattr__(self.tag)(
                   fragmentize(mo.group(1), self.child_tags,
                               remove_escapes=False))
        else:
            return bldr.tag(fragmentize(mo.group(1),self.child_tags,
                                        remove_escapes=False))

    def re_string(self):
        if isinstance(self.token,str):
            content = '(.+?' + re.escape(self.token[-1]) + '*)'
            return esc_neg_look + re.escape(self.token) + \
                   content + re.escape(self.token)
        else:
            content = '(.+?' + re.escape(self.token[1][-1]) + '*)'
            return esc_neg_look + re.escape(self.token[0]) + \
                   content + re.escape(self.token[1])


class PreBlock(BlockElement):

    """A preformatted block.

    If a closing token is found on a line with a space as the first
    character, it will be remove from the output.
    
    """

    def __init__(self, tag, token, child_tags=[]):
        super(PreBlock,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)
        self.regexp2 = re.compile(self.re_string2(),re.MULTILINE)

    def re_string(self):
        if isinstance(self.token,str):
            return '^' + re.escape(self.token) + r'\s*?\n(.*?\n)' + \
                   re.escape(self.token) + r'\s*?\n'
        else:
            start = '^' + re.escape(self.token[0]) + r'\s*?\n'
            content = r'(.*?\n)'
            end = re.escape(self.token[1]) + r'\s*?\n'
            return start + content + end

    def re_string2(self):
        """Finds a closing token will a space at the start of the line."""
        if isinstance(self.token,str):
            return r'^ (\s*?' + re.escape(self.token) + r'\s*?\n)'
        else:
            return r'^ (\s*?' + re.escape(self.token[1]) + r'\s*?\n)'

    def _build(self,mo):
        match = self.regexp2.sub(r'\1',mo.group(1))
        
        return bldr.tag.__getattr__(self.tag)(fragmentize(match,self.child_tags,remove_escapes=False))


class LoneElement(BlockElement):

    """Element on a line by itself with no content (e.g., <hr/>)"""

    def __init__(self, tag, token, child_tags):
        super(LoneElement,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)

    def re_string(self):
        return r'^(\s*?' + re.escape(self.token) + r'\s*?\n)'

    def _build(self,mo):
        return bldr.tag.__getattr__(self.tag)()

 
class BlankLine(WikiElement):

    """Blank lines divide elements but don't add any output."""

    def __init__(self):
        super(BlankLine,self).__init__(tag=None,token='' , child_tags=[])
        self.regexp = re.compile(self.re_string(),re.MULTILINE)

    def re_string(self):
        return r'^(\s*\n)+'
     
    def _build(self,mo):
        return None

    
class LineBreak(InlineElement):

    """An inline line break."""

    #append_newline = True
    def __init__(self,tag, token, child_tags=[]):
        super(LineBreak,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL)

    def re_string(self):
        return re.escape(self.token)
    
    def _build(self,mo):
        return bldr.tag.__getattr__(self.tag)()



def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()    
