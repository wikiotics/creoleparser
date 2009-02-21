# tests.py
# -*- coding: utf-8 -*-
#
# Copyright (c) 2007 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
import urllib
import unittest

from genshi import builder
from genshi.core import Markup

from core import Parser
from dialects import Creole10, dialect_base
from elements import SimpleElement


base_url = 'http://www.wikicreole.org/wiki/'
inter_wiki_url = 'http://wikiohana.net/cgi-bin/wiki.pl/'


def class_name_function(page_name):
    if page_name == 'NewPage':
        return 'nonexistent'


def path_name_function(page_name):
    if page_name == 'ThisPageHere':
        path = 'Special/ThisPageHere'
    else:
        path = urllib.quote(page_name.encode('utf-8'))
    return path



text2html = Parser(
    dialect=Creole10(
        wiki_links_base_url=base_url,
        interwiki_links_base_urls={'Ohana': inter_wiki_url},
        use_additions=True,
        no_wiki_monospace=False
        )
    )


def wrap_result(expected):
    return "<p>%s</p>\n" % expected


        
class BaseTest(object):
    """

    """
    parse = lambda x: None

    def test_newlines(self):
        self.assertEquals(
            self.parse("\na simple line"),
            wrap_result("a simple line"))
        self.assertEquals(
            self.parse("\n\na simple line\n\n"),
            wrap_result("a simple line"))

    def test_line_breaks(self):
        self.assertEquals(
            self.parse(r"break\\this"),
            wrap_result("break<br />this"))

    def test_raw_links(self):
        self.assertEquals(
            self.parse("http://www.google.com"),
            wrap_result("""<a href="http://www.google.com">http://www.google.com</a>"""))
        self.assertEquals(
            self.parse(r"http://www.google.com\\foo"),
            wrap_result("""<a href="http://www.google.com">http://www.google.com</a><br />foo"""))
        self.assertEquals(
            self.parse("~http://www.google.com"),
            wrap_result("""http://www.google.com"""))
        self.assertEquals(
            self.parse(r"<http://www.google.com>."),
            wrap_result("""&lt;<a href="http://www.google.com">http://www.google.com</a>&gt;."""))
        self.assertEquals(
            self.parse(r"(http://www.google.com) foo"),
            wrap_result("""(<a href="http://www.google.com">http://www.google.com</a>) foo"""))
        self.assertEquals(
            self.parse(r"http://www.google.com/#"),
            wrap_result("""<a href="http://www.google.com/#">http://www.google.com/#</a>"""))
        self.assertEquals(
            self.parse(r"//http://www.google.com//"),
            wrap_result("""<em><a href="http://www.google.com">http://www.google.com</a></em>"""))

    def test_links(self):
        self.assertEquals(
            self.parse("[[http://www.google.com]]"),
            wrap_result("""<a href="http://www.google.com">http://www.google.com</a>"""))
        self.assertEquals(
            self.parse("[[http://www.google.com/search\n?source=ig&hl=en&rlz=&q=creoleparser&btnG=Google+Search&aq=f]]"),
            wrap_result("""<a href="http://www.google.com/search\n?source=ig&amp;hl=en&amp;rlz=&amp;q=creoleparser&amp;btnG=Google+Search&amp;aq=f">http://www.google.com/search\n?source=ig&amp;hl=en&amp;rlz=&amp;q=creoleparser&amp;btnG=Google+Search&amp;aq=f</a>"""))
        self.assertEquals(
            self.parse(u"[[ɤ]]"),
            wrap_result("""<a href="http://www.wikicreole.org/wiki/%C9%A4">ɤ</a>"""))

    def test_links_with_spaces(self):
        self.assertEquals(
            self.parse("[[This Page Here]]"),
            wrap_result("""<a href="http://www.wikicreole.org/wiki/This_Page_Here">This Page Here</a>"""))
        self.assertEquals(
            self.parse("[[New Page|this]]"),
            wrap_result("""<a href="http://www.wikicreole.org/wiki/New_Page">this</a>"""))
        self.assertEquals(
            self.parse("[[Ohana:Home|This one]]"),
            wrap_result("""<a href="http://wikiohana.net/cgi-bin/wiki.pl/Home">This one</a>"""))


class Creole2HTMLTest(unittest.TestCase, BaseTest):
    """
    """
    def setUp(self):
        creole2html = Parser(
            dialect=Creole10(
                wiki_links_base_url=base_url,
                interwiki_links_base_urls={'Ohana': inter_wiki_url},
                use_additions=False,
                no_wiki_monospace=True
                )
            )
        self.parse = creole2html
        
    def test_links(self):
        super(Creole2HTMLTest, self).test_links()
        self.assertEquals(
            self.parse("[[http://www.google.com| <<luca Google>>]]"),
            wrap_result("""<a href="http://www.google.com">&lt;&lt;luca Google&gt;&gt;</a>"""))

class Text2HTMLTest(unittest.TestCase, BaseTest):
    """
    """
    def setUp(self):
        self.parse = Parser(
        dialect=Creole10(
        wiki_links_base_url=base_url,
        interwiki_links_base_urls={'Ohana': inter_wiki_url},
        use_additions=True,
        no_wiki_monospace=False
           )
        )

    def test_links(self):
        super(Text2HTMLTest, self).test_links()
        self.assertEquals(
            self.parse("[[foobar]]"),
            wrap_result("""<a href="http://www.wikicreole.org/wiki/foobar">foobar</a>"""))
        self.assertEquals(
            self.parse("[[foo bar]]"),
            wrap_result("""<a href="http://www.wikicreole.org/wiki/foo_bar">foo bar</a>"""))
        self.assertEquals(
            self.parse("[[foo  bar]]"),
            wrap_result("[[foo  bar]]"))
        self.assertEquals(
            self.parse("[[mailto:someone@example.com]]"),
            wrap_result("""<a href="mailto:someone@example.com">mailto:someone@example.com</a>"""))
        self.assertEquals(
            self.parse("[[http://www.google.com| <<luca Google>>]]"),
            wrap_result("""<a href="http://www.google.com"><code class="unknown_macro">&lt;&lt;luca Google&gt;&gt;</code></a>"""))

    def test_bold(self):
        self.assertEquals(
            self.parse("the **bold** is bolded"),
            wrap_result("""the <strong>bold</strong> is bolded"""))
        self.assertEquals(
            self.parse("**this is bold** {{{not **this**}}}"),
            wrap_result("""<strong>this is bold</strong> <span>not **this**</span>"""))
        self.assertEquals(
            self.parse("**this is bold //this is bold and italic//**"),
            wrap_result("""<strong>this is bold <em>this is bold and italic</em></strong>"""))

    def test_italics(self):
        self.assertEquals(
            self.parse("the //italic// is italiced"),
            wrap_result("""the <em>italic</em> is italiced"""))
        self.assertEquals(
            self.parse("//this is italic// {{{//not this//}}}"),
        wrap_result("""<em>this is italic</em> <span>//not this//</span>"""))
        self.assertEquals(
            self.parse("//this is italic **this is italic and bold**//"),
        wrap_result("""<em>this is italic <strong>this is italic and bold</strong></em>"""))

    def test_macro_markers(self):
        self.assertEquals(
            self.parse("This is the <<sue sue macro!>>"),
            wrap_result("""This is the <code class="unknown_macro">&lt;&lt;sue sue macro!&gt;&gt;</code>"""))
        self.assertEquals(
            self.parse('<<bad name>>foo<</bad>>'),
            wrap_result('<code class="unknown_macro">&lt;&lt;bad name&gt;&gt;foo&lt;&lt;/bad&gt;&gt;</code>'))
        self.assertEquals(
            self.parse('<<unknown>>foo<</unknown>>'),
            wrap_result('<code class="unknown_macro">&lt;&lt;unknown&gt;&gt;foo&lt;&lt;/unknown&gt;&gt;</code>'))
        self.assertEquals(
            self.parse('<<unknown>>foo with\na line break<</unknown>>'),
            wrap_result('<code class="unknown_macro">&lt;&lt;unknown&gt;&gt;foo with<br />a line break&lt;&lt;/unknown&gt;&gt;</code>'))
        self.assertEquals(
            self.parse('<<unknown>>\nfoo\n<</unknown>>'),
            '<pre class="unknown_macro">&lt;&lt;unknown&gt;&gt;\nfoo\n&lt;&lt;/unknown&gt;&gt;</pre>')
        self.assertEquals(
            self.parse('start\n\n<<unknown>>\n\nend'),
            wrap_result('start</p>\n<p><code class="unknown_macro">&lt;&lt;unknown&gt;&gt;</code></p>\n<p>end'))

    def test_monotype(self):
        pass

    def test_table(self):
        self.assertEquals(
            self.parse(r"""
  |= Item|= Size|= Price|
  | fish | **big**  |cheap|
  | crab | small|expesive|

  |= Item|= Size|= Price
  | fish | big  |//cheap//
  | crab | small|**very\\expesive**
                """),
            """<table><tr><th>Item</th><th>Size</th><th>Price</th></tr>
<tr><td>fish</td><td><strong>big</strong></td><td>cheap</td></tr>
<tr><td>crab</td><td>small</td><td>expesive</td></tr>
</table>
<table><tr><th>Item</th><th>Size</th><th>Price</th></tr>
<tr><td>fish</td><td>big</td><td><em>cheap</em></td></tr>
<tr><td>crab</td><td>small</td><td><strong>very<br />expesive</strong></td></tr>
</table>\n""")

    def test_headings(self):
        self.assertEquals(
            self.parse("= Level 1 (largest)"),
            "<h1>Level 1 (largest)</h1>\n")
        self.assertEquals(
            self.parse("== Level 2"),
            "<h2>Level 2</h2>\n")
        self.assertEquals(
            self.parse("=== Level 3"),
            "<h3>Level 3</h3>\n")
        self.assertEquals(
            self.parse("==== Level 4"),
            "<h4>Level 4</h4>\n")
        self.assertEquals(
            self.parse("===== Level 5"),
            "<h5>Level 5</h5>\n")
        self.assertEquals(
            self.parse("====== Level 6"),
            "<h6>Level 6</h6>\n")
        self.assertEquals(
            self.parse("=== Also Level 3 ="),
            "<h3>Also Level 3</h3>\n")
        self.assertEquals(
            self.parse("=== Also Level 3 =="),
            "<h3>Also Level 3</h3>\n")
        self.assertEquals(
            self.parse("=== Also Level 3 ==="),
            "<h3>Also Level 3</h3>\n")
        self.assertEquals(
            self.parse("= Also Level = 1 ="),
            "<h1>Also Level = 1</h1>\n")
        
        self.assertEquals(
            self.parse("=== This **is** //parsed// ==="),
            "<h3>This <strong>is</strong> <em>parsed</em></h3>\n")

    def test_escape(self):
        self.assertEquals(
            self.parse("a lone escape ~ in the middle of a line"),
            wrap_result("a lone escape ~ in the middle of a line"))
        self.assertEquals(
            self.parse("or at the end ~\nof a line"),
            wrap_result("or at the end ~\nof a line"))
        self.assertEquals(
            self.parse("a double ~~ in the middle"),
            wrap_result("a double ~ in the middle"))
        self.assertEquals(
            self.parse("or at the end ~~"),
            wrap_result("or at the end ~"))
        self.assertEquals(
            self.parse("preventing markup for ~**bold~** and ~//italics~//"),
            wrap_result("preventing markup for **bold** and //italics//"))
        self.assertEquals(
            self.parse("preventing markup for ~= headings"),
            wrap_result("preventing markup for = headings"))
        self.assertEquals(
            self.parse("|preventing markup|for a pipe ~| in a table|"),
            "<table><tr><td>preventing markup</td><td>for a pipe | in a table</td></tr>\n</table>\n")

    def test_preformat(self):
        self.assertEquals(
            self.parse("""{{{
** some ** unformatted {{{ stuff }}} ~~~

 }}}
}}}"""),
            """\
<pre>** some ** unformatted {{{ stuff }}} ~~~

}}}
</pre>
""")

    def test_inline_unformatted(self):
        self.assertEquals(
            self.parse("""
            {{{** some ** unformatted {{{ stuff ~~ }}}}}}
            """),
            wrap_result("            <span>** some ** unformatted {{{ stuff ~~ }}}</span>"))

    def test_link_in_table(self):
        self.assertEquals(
            self.parse("|http://www.google.com|Google|"),
            """<table><tr><td><a href="http://www.google.com">http://www.google.com</a></td><td>Google</td></tr>\n</table>\n""")

    def test_link_in_bold(self):
        self.assertEquals(
            self.parse("**[[http://www.google.com|Google]]**"),
            wrap_result("""<strong><a href="http://www.google.com">Google</a></strong>"""))

    def test_link_in_heading(self):
        self.assertEquals(
            self.parse("= [[http://www.google.com|Google]]"),
            """<h1><a href="http://www.google.com">Google</a></h1>\n""")
        self.assertEquals(
            self.parse("== http://www.google.com"),
            """<h2><a href="http://www.google.com">http://www.google.com</a></h2>\n""")
        self.assertEquals(
            self.parse("== ~http://www.google.com"),
            "<h2>http://www.google.com</h2>\n")

    def test_unordered_lists(self):
        self.assertEquals(
            self.parse("""
* this is list **item one**
** //subitem 1//
** //subitem 2//
*** A
*** B
** //subitem 3//
* **item two
* **item three**
*# item four
            """),
            "<ul><li>this is list <strong>item one</strong>\n<ul><li><em>subitem 1</em>\n</li><li><em>subitem 2</em>\n<ul><li>A\n</li><li>B\n</li></ul></li><li><em>subitem 3</em>\n</li></ul></li><li><strong>item two</strong>\n</li><li><strong>item three</strong>\n</li><li># item four\n</li></ul>\n")

    def test_ordered_lists(self):
        self.assertEquals(
            self.parse("""
# this is list **item one**
## //subitem 1//
## //subitem 2//
### A
### B
# **item two
# **item three**
            """),
            "<ol><li>this is list <strong>item one</strong>\n<ol><li><em>subitem 1</em>\n</li><li><em>subitem 2</em>\n<ol><li>A\n</li><li>B\n</li></ol></li></ol></li><li><strong>item two</strong>\n</li><li><strong>item three</strong>\n</li></ol>\n")

    def test_mixed_lists(self):
        self.assertEquals(
            self.parse("""
# this is list **item one**
** //unordered subitem 1//
** //unordered subitem 2//
# **item two
** Unorder subitem 1
** Unorder subitem 2
# **item three**
            """),
            "<ol><li>this is list <strong>item one</strong>\n<ul><li><em>unordered subitem 1</em>\n</li><li><em>unordered subitem 2</em>\n</li></ul></li><li><strong>item two</strong>\n<ul><li>Unorder subitem 1\n</li><li>Unorder subitem 2\n</li></ul></li><li><strong>item three</strong>\n</li></ol>\n")

    def test_definition_lists(self):
        self.assertEquals(
            self.parse("""
; This is a title:
: this is its entry
; Another title : it's definition entry
; This is ~: a another title:
: this is its entry
** and this emphasized!
; Title
: definition 1
: defintioins 2"""),
            "<dl><dt>This is a title:</dt>\n<dd>this is its entry</dd>\n<dt>Another title</dt>\n<dd>it's definition entry</dd>\n<dt>This is : a another title:</dt>\n<dd>this is its entry\n<strong> and this emphasized!</strong></dd>\n<dt>Title</dt>\n<dd>definition 1</dd>\n<dd>defintioins 2</dd>\n</dl>\n")

    def test_image(self):
        self.assertEquals(
            self.parse("{{campfire.jpg}}"),
            """<p><img src="campfire.jpg" alt="campfire.jpg" title="campfire.jpg" /></p>\n""")

    def test_image_in_link(self):
        self.assertEquals(
            self.parse("[[http://google.com | {{ campfire.jpg | Nice Pic }}]]"),
            wrap_result("""<a href="http://google.com"><img src="campfire.jpg" alt="Nice Pic" title="Nice Pic" /></a>"""))
        self.assertEquals(
            self.parse("[[http://google.com | {{ campfire.jpg }}]]"),
            wrap_result("""<a href="http://google.com"><img src="campfire.jpg" alt="campfire.jpg" title="campfire.jpg" /></a>"""))

    def test_image_in_table(self):
        self.assertEquals(
            self.parse("|nice picture |{{campfire.jpg}}|"),
            """<table><tr><td>nice picture</td><td><img src="campfire.jpg" alt="campfire.jpg" title="campfire.jpg" /></td></tr>\n</table>\n""")

    def test_super_and_sub_scripts(self):
        self.assertEquals(
            self.parse("^^superscript^^"),
            wrap_result("<sup>superscript</sup>"))
        self.assertEquals(
            self.parse(",,subscript,,"),
            wrap_result("<sub>subscript</sub>"))
        self.assertEquals(
            self.parse("__underline__"),
            wrap_result("<u>underline</u>"))
        self.assertEquals(
            self.parse("//^^superscript^^,,subscript,,**__underline__**//"),
            wrap_result("<em><sup>superscript</sup><sub>subscript</sub><strong><u>underline</u></strong></em>"))
        self.assertEquals(
            self.parse("^^//superscript//\\hello^^\n,,sub**scr**ipt,,"),
            wrap_result("<sup><em>superscript</em>\\hello</sup>\n<sub>sub<strong>scr</strong>ipt</sub>"))
        self.assertEquals(
            self.parse("__underline__"),
            wrap_result("<u>underline</u>"))

class DialectOptionsTest(unittest.TestCase):

    def test_no_wiki_monospace_option(self):
        dialect = Creole10(no_wiki_monospace=True)
        parse = Parser(dialect)
        self.assertEquals(
            parse("This block of {{{no_wiki **shouldn't** be monospace}}} now"),
            wrap_result("This block of <code>no_wiki **shouldn't** be monospace</code> now"))

    def test_use_additions_option(self):
        dialect = Creole10(use_additions=True)
        parse = Parser(dialect)
        self.assertEquals(
            parse("This block of ##text **should** be monospace## now"),
            wrap_result("This block of <code>text <strong>should</strong> be monospace</code> now"))

    def test_blog_style_endings_option(self):
        dialect = Creole10(blog_style_endings=True)
        parse = Parser(dialect)
        self.assertEquals(
            parse("The first line\nthis text **should** be on the second line\n now third"),
            wrap_result("The first line<br />this text <strong>should</strong> be on the second line<br /> now third"))

class ExtendingTest(unittest.TestCase):
    

    def test_simple_tokens_option(self):
        Base = dialect_base()
        class MyDialect(Base):
            simple_elements = SimpleElement(token_dict={'*':'strong','#':'code'})
        parse = Parser(MyDialect())
        self.assertEquals(
            parse("This block of #text *should* be monospace# now"),
            wrap_result("This block of <code>text <strong>should</strong> be monospace</code> now"))

##    def test_simple_tokens_option2(self):
##        dialect = Creole10(simple_tokens=[('--','del')])
##        parse = Parser(dialect)
##        self.assertEquals(
##            parse("This block of --text **should** be monospace-- now"),
##            wrap_result("This block of <del>text <strong>should</strong> be monospace</del> now"))
        
class NoSpaceDialectTest(unittest.TestCase, BaseTest):

    def setUp(self):
        noSpaces = Parser(
            dialect=Creole10(
                wiki_links_base_url=base_url,
                wiki_links_space_char='',
                use_additions=True,
                no_wiki_monospace=False,
                wiki_links_class_func=class_name_function,
                wiki_links_path_func=path_name_function
                )
            )
        self.parse = noSpaces

    def test_links_with_spaces(self):
        self.assertEquals(
            self.parse("[[This Page Name Has Spaces]]"),
            wrap_result("""<a href="http://www.wikicreole.org/wiki/ThisPageNameHasSpaces">This Page Name Has Spaces</a>"""))

    def test_special_link(self):
        self.assertEquals(
            self.parse("[[This Page Here]]"),
            wrap_result("""<a href="http://www.wikicreole.org/wiki/Special/ThisPageHere">This Page Here</a>"""))

    def test_new_page(self):
        self.assertEquals(
            self.parse("[[New Page|this]]"),
            wrap_result("""<a class="nonexistent" href="http://www.wikicreole.org/wiki/NewPage">this</a>"""))


class MacroTest(unittest.TestCase, BaseTest):
    """
    """

    def setUp(self):
        dialect = Creole10(
            wiki_links_base_url='http://creoleparser.x10hosting.com/cgi-bin/creolepiki/',
            wiki_links_space_char='',
            use_additions=True,
            no_wiki_monospace=False,
            macro_func=self.macroFactory)
        self.parse = Parser(dialect)

    class Wiki(object):
        page_title='Home'
    
    def getFragment(self, text):
        wrapped = Markup(text)
        fragment = builder.tag(wrapped)
        return fragment

    def getStream(self, text):
        wrapped = Markup(text)
        fragment = builder.tag(wrapped)
        return fragment.generate()

    def macroFactory(self, macro_name, arg_string, body, context,wiki):
        if macro_name == 'html':
            return self.getFragment(body)
        elif macro_name == 'title':
            return wiki.page_title
        elif macro_name == 'span':
            return builder.tag.span(self.parse.generate(body,context='inline'),id_=arg_string.strip())
        elif macro_name == 'div':
            return builder.tag.div(self.parse.generate(body),id_=arg_string.strip())
        elif macro_name == 'html2':
            return Markup(body)
        elif macro_name == 'htmlblock':
            return self.getStream(body)
        elif macro_name == 'pre':
            return builder.tag.pre('**' + body + '**')
        elif macro_name == 'steve':
            return '**' + arg_string + '**'
        elif macro_name == 'luca':
            return builder.tag.strong(arg_string)
        elif macro_name == 'mateo':
            return builder.tag.em(body)
        elif macro_name == 'ReverseFrag':
            return builder.tag(body[::-1])
        elif macro_name == 'Reverse':
            return body[::-1]
        elif macro_name == 'Reverse-it':
            return body[::-1]
        elif macro_name == 'ReverseIt':
            return body[::-1]
        elif macro_name == 'lib.ReverseIt-now':
            return body[::-1]
        elif macro_name == 'ifloggedin':
            return body
        elif macro_name == 'username':
            return 'Joe Blow'
        elif macro_name == 'center':
            return builder.tag.span(body, class_='centered')
        elif macro_name == 'footer':
            return '<<center>>This is a footer.<</center>>'
        elif macro_name == 'footer2':
            return '<<center>>\nThis is a footer.\n<</center>>'
        elif macro_name == 'reverse-lines':
            if body is not None:
                l = reversed(body.rstrip().split('\n'))
                if arg_string.strip() == 'output=wiki':
                    return '\n'.join(l) + '\n'
                else:
                    return builder.tag('\n'.join(l) + '\n')

    def test_macros(self):
        self.assertEquals(
            self.parse('<<title>>',page=self.Wiki),
            wrap_result('Home'))
        self.assertEquals(
            self.parse('<<html>><q cite="http://example.org">foo</q><</html>>'),
            wrap_result('<q cite="http://example.org">foo</q>'))
        self.assertEquals(
            self.parse('<<html2>><b>hello</b><</html2>>'),
            '<b>hello</b>\n')
        self.assertEquals(
            self.parse('<<htmlblock>><q cite="http://example.org">foo</q><</htmlblock>>'),
                '<q cite="http://example.org">foo</q>\n')
        self.assertEquals(
            self.parse('<<pre>>//no wiki//<</pre>>'),
            '<pre>**//no wiki//**</pre>\n')
        self.assertEquals(
            self.parse('<<pre>>one<</pre>>\n<<pre>>two<</pre>>'),
            '<pre>**one**</pre>\n<pre>**two**</pre>\n')
        self.assertEquals(
            self.parse('<<pre>>one<<pre>>\n<</pre>>two<</pre>>'),
            '<pre>**one&lt;&lt;pre&gt;&gt;\n&lt;&lt;/pre&gt;&gt;two**</pre>\n')
        self.assertEquals(
            self.parse(u'<<mateo>>fooɤ<</mateo>>'),
            wrap_result('<em>foo\xc9\xa4</em>'))
        self.assertEquals(
            self.parse(u'<<steve fooɤ>>'),
            wrap_result('<strong> foo\xc9\xa4</strong>'))
        self.assertEquals(
            self.parse('<<ReverseFrag>>**foo**<</ReverseFrag>>'),
            wrap_result('**oof**'))
        self.assertEquals(        
            self.parse('<<Reverse>>**foo**<</Reverse>>'),
            wrap_result('<strong>oof</strong>'))
        self.assertEquals(
            self.parse('<<Reverse>>foo<</Reverse>>'),
            wrap_result('oof'))
        self.assertEquals(
            self.parse('<<Reverse-it>>foo<</Reverse-it>>'),
            wrap_result('oof'))
        self.assertEquals(
            self.parse('<<ReverseIt>>foo<</ReverseIt>>'),
            wrap_result('oof'))
        self.assertEquals(
            self.parse('<<lib.ReverseIt-now>>foo<</lib.ReverseIt-now>>'),
            wrap_result('oof'))
        self.assertEquals(
            self.parse(u'<<luca boo>>foo<</unknown>>'),
            wrap_result('<strong> boo</strong>foo&lt;&lt;/unknown&gt;&gt;'))
        self.assertEquals(
            self.parse('Hello<<ifloggedin>> <<username>><</ifloggedin>>!'),
            wrap_result('Hello Joe Blow!'))
        self.assertEquals(
            self.parse(' <<footer>>'),
            wrap_result(' <span class="centered">This is a footer.</span>'))
        self.assertEquals(
            self.parse('<<footer2>>'),
            '<p><span class="centered">\nThis is a footer.\n</span></p>\n')
        self.assertEquals(
            self.parse('<<luca foobar>>'),
            '<p><strong> foobar</strong></p>\n')
        self.assertEquals(
            self.parse("<<reverse-lines>>one<</reverse-lines>>"),
            wrap_result("one\n"))
        self.assertEquals(
            self.parse("<<reverse-lines>>one\ntwo\n<</reverse-lines>>"),
            wrap_result("two\none\n"))
        self.assertEquals(
            self.parse("<<reverse-lines>>\none\ntwo<</reverse-lines>>"),
            wrap_result("two\none\n\n"))
        self.assertEquals(
            self.parse(
"""\
<<reverse-lines>>

one

two

<</reverse-lines>>
"""),
 """\
<p>two

one

</p>""")
        self.assertEquals(
            self.parse(u"\n<<div one>>\nblaa<</div>>"),
            '<div id="one"><p>blaa</p>\n</div>\n')
        self.assertEquals(
            self.parse("<<reverse-lines>>one\n{{{two}}}\n<</reverse-lines>>"),
            wrap_result("{{{two}}}\none\n"))
        self.assertEquals(
            self.parse("<<reverse-lines>>one\n{{{\ntwo}}}\n<</reverse-lines>>"),
            wrap_result("two}}}\n{{{\none\n"))
        self.assertEquals(
            self.parse("<<reverse-lines>>one\n{{{\ntwo\n}}}<</reverse-lines>>"),
            wrap_result("}}}\ntwo\n{{{\none\n"))
        self.assertEquals(
            self.parse("<<reverse-lines>>\none\n{{{\ntwo\n}}}\n<</reverse-lines>>"),
            "<p>}}}\ntwo\n{{{\none\n</p>")
        self.assertEquals(
            self.parse("<<reverse-lines output=wiki>>one\n{{{\ntwo\n}}}<</reverse-lines>>"),
            wrap_result("}}}\ntwo\n{{{\none\n"))
        self.assertEquals(
            self.parse("<<reverse-lines output=wiki>>one\n}}}\ntwo\n{{{<</reverse-lines>>"),
            wrap_result("<span>\ntwo\n</span>\none\n"))
        self.assertEquals(
            self.parse("<<reverse-lines output=wiki>>one\n}}}\ntwo\n{{{\n<</reverse-lines>>"),
            wrap_result("<span>\ntwo\n</span>\none\n"))
        self.assertEquals(
            self.parse("<<reverse-lines output=wiki>>\none\n}}}\n\ntwo\n{{{\n<</reverse-lines>>"),
            "<pre>two\n\n</pre>\n<p>one</p>\n")
        self.assertEquals(
            self.parse("<<reverse-lines output=wiki>>\none\n\n}}}\ntwo\n{{{\n<</reverse-lines>>"),
            "<pre>two\n</pre>\n<p>one</p>\n")

    def test_nesting_macros(self):
        self.assertEquals(
            self.parse('<<span one>>part 1<</span>><<span two>>part 2<</span>>'),
            wrap_result('<span id="one">part 1</span><span id="two">part 2</span>'))
        self.assertEquals(
            self.parse('<<span>>part 1a<<span two>>part 2<</span>>part 1b<</span>>'),
            wrap_result('<span id="">part 1a<span id="two">part 2</span>part 1b</span>'))
        self.assertEquals(
            self.parse('<<span>>part 1a<<span>>part 2<</span>>part 1b<</span>>'),
            wrap_result('<span id="">part 1a<span id="">part 2</span>part 1b</span>'))
        self.assertEquals(
            self.parse('<<span one>>part 1a<<span two>>part 2<</span>>part 1b<</span>>'),
            wrap_result('<span id="one">part 1a<span id="two">part 2</span>part 1b</span>'))
        self.assertEquals(
            self.parse("""
<<div one>>
part 1a
<<div two>>
part 2
<</div>>
part 1b
<</div>>"""),'<div id="one"><p>part 1a</p>\n<div id="two"><p>part 2</p>\n</div><p>part 1b</p>\n</div>')
        self.assertEquals(
            self.parse("""
<<div one>>
part 1
<</div>>
<<div one>>
part 2
<</div>>"""),'<div id="one"><p>part 1</p>\n</div><div id="one"><p>part 2</p>\n</div>')

        
    def test_links(self):
        self.assertEquals(
            self.parse("http://www.google.com"),
            wrap_result("""<a href="http://www.google.com">http://www.google.com</a>"""))
        self.assertEquals(
            self.parse("~http://www.google.com"),
            wrap_result("""http://www.google.com"""))
        self.assertEquals(
            self.parse("[[http://www.google.com]]"),
            wrap_result("""<a href="http://www.google.com">http://www.google.com</a>"""))
        self.assertEquals(
            self.parse("[[http://www.google.com| <<luca Google>>]]"),
            wrap_result("""<a href="http://www.google.com"><strong> Google</strong></a>"""))

    def test_links_with_spaces(self):
        self.assertEquals(
            self.parse("[[This Page Here]] is <<steve the steve macro!>>"),
            wrap_result("""<a href="http://creoleparser.x10hosting.com/cgi-bin/creolepiki/ThisPageHere">This Page Here</a> is <strong> the steve macro!</strong>"""))
        self.assertEquals(
            self.parse("[[New Page|this]]"),
            wrap_result("""<a href="http://creoleparser.x10hosting.com/cgi-bin/creolepiki/NewPage">this</a>"""))



class InterWikiLinksTest(unittest.TestCase):

    def setUp(self):
        def inter_wiki_link_maker(name):
            return name[::-1]

        functions = {
            'moo':inter_wiki_link_maker,
            'goo':inter_wiki_link_maker,
            }
        base_urls = {
            'goo': 'http://example.org',
            'poo': 'http://example.org',
            }
        space_characters = {
            'goo': '+',
            'poo': '+',
            }

        dialect = Creole10(
            interwiki_links_funcs=functions,
            interwiki_links_base_urls=base_urls,
            interwiki_links_space_chars=space_characters
            )

        self.parse = Parser(dialect)

    def test_interwiki_links(self):
        self.assertEquals(
            str(self.parse("[[moo:foo bar|Foo]]")),
            wrap_result("""<a href="rab_oof">Foo</a>"""))
        self.assertEquals(
            str(self.parse("[[goo:foo|Foo]]")),
            wrap_result("""<a href="http://example.org/oof">Foo</a>"""))
        self.assertEquals(
            str(self.parse("[[poo:foo|Foo]]")),
            wrap_result("""<a href="http://example.org/foo">Foo</a>"""))
        self.assertEquals(
            str(self.parse("[[poo:foo bar|Foo]]")),
            wrap_result("""<a href="http://example.org/foo%2Bbar">Foo</a>"""))
        self.assertEquals(
            str(self.parse("[[goo:foo bar|Foo]]")),
            wrap_result("""<a href="http://example.org/rab+oof">Foo</a>"""))
        self.assertEquals(
            str(self.parse("[[roo:foo bar|Foo]]")),
            wrap_result("""[[roo:foo bar|Foo]]"""))


class TaintingTest(unittest.TestCase):
    """
    """
    def setUp(self):
        self.parse = text2html

    def test_cookies(self):
        self.assertEquals(
            self.parse("{{javascript:alert(document.cookie)}}"),
            """<p><img src="unsafe_uri_detected" alt="unsafe_uri_detected" title="unsafe_uri_detected" /></p>\n""")
        self.assertEquals(
            self.parse("[[javascript:alert(document.cookie)]]"),
            wrap_result("[[javascript:alert(document.cookie)]]"))


class LongDocumentTest(unittest.TestCase):
    """
    """
    def test_very_long_document(self):
        lines = [str(x)+' blaa blaa' for x in range(2000)]
        lines[50] = '{{{'
        lines[500] = '}}}'
        lines[1100] = '{{{'
        lines[1400] = '}}}'
        doc = '\n\n'.join(lines)
        pre = False
        expected_lines = []
        for line in lines:
            if line == '{{{':
                expected_lines.append('<pre>\n')
                pre = True
            elif line == '}}}':
                expected_lines.append('</pre>\n')
                pre = False
            elif pre:
                expected_lines.append(line+'\n\n')
            else:
                expected_lines.append('<p>'+line+'</p>\n')
        expected = ''.join(expected_lines)
        rendered = text2html(doc)
        self.assertEquals(text2html(doc), expected)


class ContextTest(unittest.TestCase):
    """
    """
    def setUp(self):
        self.markup = "steve //rad//"

    def test_block_context(self):
        result = text2html.render(self.markup, context="block")
        self.assertEqual(result, wrap_result("steve <em>rad</em>"))

    def test_inline_context(self):
        result = text2html.render(self.markup, context="inline")
        self.assertEqual(result, "steve <em>rad</em>")

    def test_inline_elements_context(self):
        context = text2html.dialect.inline_elements
        result = text2html.render(self.markup, context=context)
        self.assertEqual(result, "steve <em>rad</em>")

    def test_block_elements_context(self):
        context = text2html.dialect.block_elements
        result = text2html.render(self.markup+'\n', context=context)
        self.assertEqual(result, wrap_result("steve <em>rad</em>"))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Creole2HTMLTest),
        unittest.makeSuite(Text2HTMLTest),
        unittest.makeSuite(DialectOptionsTest),
        unittest.makeSuite(NoSpaceDialectTest),
        unittest.makeSuite(MacroTest),
        unittest.makeSuite(InterWikiLinksTest),
        unittest.makeSuite(TaintingTest),
        unittest.makeSuite(LongDocumentTest),
        unittest.makeSuite(ContextTest),
        unittest.makeSuite(ExtendingTest),
        ))


def run_suite(verbosity=1):
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(test_suite())


if __name__ == "__main__":
    import sys
    args = sys.argv
    verbosity = 1
    if len(args) > 1:
        verbosity = args[1]
    run_suite(verbosity=verbosity)

