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
from dialects import Creole10


base_url = 'http://www.wikicreole.org/wiki/'
inter_wiki_url = 'http://wikiohana.net/cgi-bin/wiki.pl/'


def class_name_function(page_name):
    if page_name == 'NewPage':
        return 'nonexistent'


def path_name_function(page_name):
    if page_name == 'ThisPageHere':
        path = 'Special/ThisPageHere'
    else:
        path = urllib.quote(page_name)
    return path


creole2html = Parser(
    dialect=Creole10(
        wiki_links_base_url=base_url,
        interwiki_links_base_urls={'Ohana': inter_wiki_url},
        use_additions=False,
        no_wiki_monospace=True
        )
    )


text2html = Parser(
    dialect=Creole10(
        wiki_links_base_url=base_url,
        interwiki_links_base_urls={'Ohana': inter_wiki_url},
        use_additions=True,
        no_wiki_monospace=False
        )
    )

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


def check_markup(m, s, p=text2html,paragraph=True,context='block'):
    if paragraph:
        out = '<p>%s</p>\n' % s
    else:
        out = s
    gen = p.render(m,context=context)
    #print 'obtained:', repr(gen)
    #print 'expected:', repr(out)
    assert out == gen


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
            wrap_result("""<a href="http://www.google.com">&lt;&lt;luca Google&gt;&gt;</a>"""))

    def test_links_with_spaces(self):
        self.assertEquals(
            self.parse("[[This Page Here]] is <<steve the steve macro!>>"),
            wrap_result("""<a href="http://www.wikicreole.org/wiki/This_Page_Here">This Page Here</a> is &lt;&lt;steve the steve macro!&gt;&gt;"""))
        self.assertEquals(
            self.parse("[[New Page|this]]"),
            wrap_result("""<a href="http://www.wikicreole.org/wiki/New_Page">this</a>"""))
        self.assertEquals(
            self.parse("[[Ohana:Home|This one]]"),
            wrap_result("""<a href="http://wikiohana.net/cgi-bin/wiki.pl/Home">This one</a>"""))

    def test_macro_markers(self):
        self.assertEquals(
            self.parse("This is the <<sue sue macro!>>"),
            wrap_result("""This is the &lt;&lt;sue sue macro!&gt;&gt;"""))


class Creole2HTMLTest(unittest.TestCase, BaseTest):
    """
    """
    def setUp(self):
        self.parse = creole2html


class Text2HTMLTest(unittest.TestCase, BaseTest):
    """
    """
    def setUp(self):
        self.parse = text2html

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
            self.parse("=== This **is** //parsed// ==="),
            "<h3>This <strong>is</strong> <em>parsed</em></h3>\n")

    def test_escape(self):
        self.assertEquals(
            self.parse("a lone escape ~ in the middle of a line"),
            wrap_result("a lone escape ~ in the middle of a line"))
        self.assertEquals(
            self.parse("or at the end ~"),
            wrap_result("or at the end ~"))
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
            }}}"""),
            wrap_result("<span>\n            ** some ** unformatted {{{ stuff </span> ~~\n            }}}"))

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

    # XXX the next two list tests need to be verified -- I don't think they
    # should be rendrered in the manner that they are, with new nested
    # ul/ol tags

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
            """),
            "<ul><li>this is list <strong>item one</strong>\n<ul><li><em>subitem 1</em></li>\n<li><em>subitem 2</em>\n<ul><li>A</li>\n<li>B</li></ul></li>\n<li><em>subitem 3</em></li></ul></li>\n<li><strong>item two</strong></li>\n<li><strong>item three</strong></li></ul>\n")

    def test_ordered_lists(self):
        self.assertEquals(
            self.parse("""
# this is list **item one**
## //subitem 1//
## //subitem 2//
### A
### B
** //subitem 3//
# **item two
# **item three**
            """),
            "<ol><li>this is list <strong>item one</strong>\n<ol><li><em>subitem 1</em></li>\n<li><em>subitem 2</em>\n<ol><li>A</li>\n<li>B\n<ul><li><em>subitem 3</em></li></ul></li></ol></li></ol></li>\n<li><strong>item two</strong></li>\n<li><strong>item three</strong></li></ol>\n")

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
            wrap_result("""<img src="campfire.jpg" alt="campfire.jpg" />"""))

    def test_image_in_link(self):
        self.assertEquals(
            self.parse("[[http://google.com | {{ campfire.jpg | Nice Pic }}]]"),
            wrap_result("""<a href="http://google.com"><img src="campfire.jpg" alt="Nice Pic" /></a>"""))
        self.assertEquals(
            self.parse("[[http://google.com | {{ campfire.jpg }}]]"),
            wrap_result("""<a href="http://google.com"><img src="campfire.jpg" alt="campfire.jpg" /></a>"""))

    def test_image_in_table(self):
        self.assertEquals(
            self.parse("|nice picture |{{campfire.jpg}}|"),
            """<table><tr><td>nice picture</td><td><img src="campfire.jpg" alt="campfire.jpg" /></td></tr>\n</table>\n""")

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


    # XXX I think these tests are currently not passing against trunk

    ##    print text2html(r"""
    ##a lone escape ~ in the middle of a line
    ##or at the end ~
    ##a double ~~ in the middle
    ##at end ~~
    ##preventing ~** **bold** and ~// //italics//
    ## ~= stopping headers!
    ##| in table~| cells | too!
    ##""")


    ##    print text2html(r"""
    ##* this is list **item one**
    ##** item one - //subitem 1//
    ##### one **http://www.google.com**
    ##### two [[Creole1.0]]
    ##### three\\covers\\many\\lines
    ##** //subitem 2//
    ##### what is this?
    ##### no idea?
    ##**** A
    ##**** B
    ##### And lots of
    ##drivel here
    ##** //subitem 3//
    ##*** huh?
    ##* **item two
    ##* **item three**
    ### new ordered list, item 1
    ### item 2
    #### sub item
    ####sub item
    ##""")

    ##    print text2html(r"""
    ##hello
    ##; This is a title:
    ##: Yes, sir!
    ##; This is~: a another title:
    ##: Yes, sir!
    ##** and this emphasized!
    ##; Another title : it's definition
    ##; Another title ~: it's definition **NOT**
    ##: here it is
    ##*this is a list!!
    ##; Wiki
    ##; Creole
    ##what about this?
    ##: something neat
    ##: two defintioins?""")

class DialectOptionsTest(unittest.TestCase):
    """
    """

def test_no_wiki_monospace_option():
    dialect = Creole10(no_wiki_monospace=True)
    parser = Parser(dialect)
    assert parser(r"""
This block of {{{no_wiki **shouldn't** be monospace}}} now""") == """\
<p>This block of <tt>no_wiki **shouldn't** be monospace</tt> now</p>
"""

def test_use_additions_option():
    dialect = Creole10(use_additions=True)
    parser = Parser(dialect)
    assert parser(r"""
This block of ##text **should** be monospace## now""") == """\
<p>This block of <tt>text <strong>should</strong> be monospace</tt> now</p>
"""

##    print text2html(r"""
##This block of ##text <<<23>>> be <<<hi>>>monospace <<<>>>## now""")

def test_place_holders():
    assert text2html(r"""
This block of ##text <<<23>>> be <<<hi>>>monospace <<<>>>## now""") == """\
<p>This block of <tt>text &lt;&lt;&lt;23&gt;&gt;&gt; be &lt;&lt;&lt;hi&gt;&gt;&gt;monospace &lt;&lt;&lt;&gt;&gt;&gt;</tt> now</p>
"""

class NoSpaceDialectTest(unittest.TestCase, BaseTest):
    """
    """
    def setUp(self):
        self.parse = noSpaces

    def test_links_with_spaces(self):
        self.assertEquals(
            self.parse("[[This Page Name Has Spaces]]"),
            wrap_result("""<a href="http://www.wikicreole.org/wiki/ThisPageNameHasSpaces">This Page Name Has Spaces</a>"""))
        #self.assertEquals(
        #    self.parse("[[Ohana:Home|This one]]"),
        #    wrap_result("""<a href="http://wikiohana.net/cgi-bin/wiki.pl/Home">This one</a>"""))

    def test_special_link(self):
        self.assertEquals(
            self.parse("[[This Page Here]]"),
            wrap_result("""<a href="http://www.wikicreole.org/wiki/Special/ThisPageHere">This Page Here</a>"""))

    def test_new_page(self):
        self.assertEquals(
            self.parse("[[New Page|this]]"),
            wrap_result("""<a class="nonexistent" href="http://www.wikicreole.org/wiki/NewPage">this</a>"""))


class MacroTest(unittest.TestCase):
    """
    """

def test_marco_func():

    def html2stream(text):
        wrapped = Markup(text)
        fragment = builder.tag(wrapped)
        stream = fragment.generate()
        return stream

    def a_macro_func(macro_name, arg_string,body,context):
        if macro_name == 'html':
            return html2stream(body)
        if macro_name == 'steve':
            return '**' + arg_string + '**'
        if macro_name == 'luca':
            return builder.tag.strong(arg_string).generate()
        if macro_name == 'mateo':
            return builder.tag.em(body).generate()
        if macro_name == 'Reverse':
            return body[::-1]
        if macro_name == 'Reverse-it':
            return body[::-1]
        if macro_name == 'ReverseIt':
            return body[::-1]
        if macro_name == 'lib.ReverseIt-now':
            return body[::-1]
        if macro_name == 'ifloggedin':
            return body
        if macro_name == 'username':
            return 'Joe Blow'
        if macro_name == 'center':
            return builder.tag.span(body, class_='centered').generate()
        if macro_name == 'footer':
            return '<<center>>This is a footer.<</center>>'
        if macro_name == 'footer2':
            return '<<center>>\nThis is a footer.\n<</center>>'
        if macro_name == 'reverse-lines':
            l = reversed(body.rstrip().split('\n'))
            if arg_string.strip() == 'output=wiki':
                return '\n'.join(l) + '\n'
            else:
                return builder.tag('\n'.join(l) + '\n').generate()

    dialect = Creole10(
        wiki_links_base_url='http://creoleparser.x10hosting.com/cgi-bin/creolepiki/',
        wiki_links_space_char='',
        use_additions=True,
        no_wiki_monospace=False,
        macro_func=a_macro_func)

    parser = Parser(dialect)

    check_markup('<<html>><q cite="http://example.org">foo</q><</html>>',
                 '<q cite="http://example.org">foo</q>',p=parser)
    check_markup(u'<<mateo>>fooɤ<</mateo>>','<em>foo\xc9\xa4</em>',p=parser)
    check_markup(u'<<steve fooɤ>>','<strong> foo\xc9\xa4</strong>',p=parser)
    check_markup('<<Reverse>>foo<</Reverse>>','oof',p=parser)
    check_markup('<<Reverse-it>>foo<</Reverse-it>>','oof',p=parser)
    check_markup('<<ReverseIt>>foo<</ReverseIt>>','oof',p=parser)
    check_markup('<<lib.ReverseIt-now>>foo<</lib.ReverseIt-now>>','oof',p=parser)
    check_markup('<<bad name>>foo<</bad name>>',
                 '&lt;&lt;bad name&gt;&gt;foo&lt;&lt;/bad name&gt;&gt;',p=parser)
    check_markup('<<unknown>>foo<</unknown>>',
                 '&lt;&lt;unknown&gt;&gt;foo&lt;&lt;/unknown&gt;&gt;',p=parser)
    check_markup(u'<<luca boo>>foo<</unknown>>',
                 '<strong> boo</strong>foo&lt;&lt;/unknown&gt;&gt;',p=parser)
    check_markup('Hello<<ifloggedin>> <<username>><</ifloggedin>>!',
                 'Hello Joe Blow!',p=parser)
    check_markup(' <<footer>>',' <span class="centered">This is a footer.</span>',p=parser)
    check_markup('<<footer2>>','<span class="centered">This is a footer.\n</span>',p=parser,paragraph=False)
    check_markup('<<luca foobar>>','<strong> foobar</strong>',p=parser,paragraph=False)
    check_markup("""\
<<reverse-lines>>
one
two
{{{
three
}}}

four
<</reverse-lines>>
""","""\
four

}}}
three
{{{
two
one
""",p=parser,paragraph=False)
    check_markup("""\
<<reverse-lines output=wiki>>
one
two
}}}
three
{{{

four
<</reverse-lines>>
""","""\
<p>four</p>
<pre>three
</pre>
<p>two
one</p>
""",p=parser,paragraph=False)
    check_markup("""\
one
<<footer>>

<<luca foobar>>

<<steve foo>>
""","""\
<p>one
<span class="centered">This is a footer.</span></p>
<strong> foobar</strong><p><strong> foo</strong></p>
""",p=parser,paragraph=False)



##    print parser(r"""
##Go to [[http://www.google.com]], it is [[http://www.google.com| <<luca Google>>]]\\
##even [[This Page Here]] is <<steve the steve macro!>> nice like [[New Page|this]].\\
##This is the <<sue sue macro!>> and this is the <<luca luca macro!>>.\\
##Don't touch {{{<<steve this!>>}}}.\\
##<<mateo>>A body!<</mateo>>\\
##As is [[Ohana:Home|This one]].""")

    assert parser(r"""
Go to [[http://www.google.com]], it is [[http://www.google.com| <<luca Google>>]]\\
even [[This Page Here]] is <<steve the steve macro!>> nice like [[New Page|this]].\\
This is the <<sue sue macro!>> and this is the <<luca luca macro!>>.\\
Don't touch {{{<<steve this!>>}}}.\\
<<mateo>>A body!<</mateo>>\\
As is [[Ohana:Home|This one]].""") == """\
<p>Go to <a href="http://www.google.com">http://www.google.com</a>, it is <a href="http://www.google.com"><strong> Google</strong></a><br />
even <a href="http://creoleparser.x10hosting.com/cgi-bin/creolepiki/ThisPageHere">This Page Here</a> is <strong> the steve macro!</strong> nice like <a href="http://creoleparser.x10hosting.com/cgi-bin/creolepiki/NewPage">this</a>.<br />
This is the &lt;&lt;sue sue macro!&gt;&gt; and this is the <strong> luca macro!</strong>.<br />
Don't touch <span>&lt;&lt;steve this!&gt;&gt;</span>.<br />
<em>A body!</em><br />
As is [[Ohana:Home|This one]].</p>
"""

##    print parser(r"""
##Go to [[http://www.google.com]], it is [[http://www.google.com| <<luca Google>>]]\\
##even [[This Page Here]] is <<steve the steve macro!>> nice like [[New Page|this]].\\
##<<mateo>>This is the some random text
##over two lines<</mateo>><<mila>>A body!<</mila>>\\
##As is [[Ohana:Home|This one]].
##<<mila>>A body!<</mila>>""")

    assert parser(r"""
Go to [[http://www.google.com]], it is [[http://www.google.com| <<luca Google>>]]\\
even [[This Page Here]] is <<steve the steve macro!>> nice like [[New Page|this]].\\
<<mateo>>This is the some random text
over two lines<</mateo>><<mila>>A body!<</mila>>\\
As is [[Ohana:Home|This one]].
<<mila>>A body!<</mila>>""") == """\
<p>Go to <a href="http://www.google.com">http://www.google.com</a>, it is <a href="http://www.google.com"><strong> Google</strong></a><br />
even <a href="http://creoleparser.x10hosting.com/cgi-bin/creolepiki/ThisPageHere">This Page Here</a> is <strong> the steve macro!</strong> nice like <a href="http://creoleparser.x10hosting.com/cgi-bin/creolepiki/NewPage">this</a>.<br />
<em>This is the some random text
over two lines</em>&lt;&lt;mila&gt;&gt;A body!&lt;&lt;/mila&gt;&gt;<br />
As is [[Ohana:Home|This one]].
&lt;&lt;mila&gt;&gt;A body!&lt;&lt;/mila&gt;&gt;</p>
"""

class InterWikiLinksTest(unittest.TestCase):
    """
    """


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

        self.parser = Parser(dialect)

    def test_interwiki_links(self):
        self.assertEquals(
            str(self.parser.generate("[[moo:foo bar|Foo]]")),
            wrap_result("""<a href="rab_oof">Foo</a>"""))
        self.assertEquals(
            str(self.parser.generate("[[goo:foo|Foo]]")),
            wrap_result("""<a href="http://example.org/oof">Foo</a>"""))
        self.assertEquals(
            str(self.parser.generate("[[poo:foo|Foo]]")),
            wrap_result("""<a href="http://example.org/foo">Foo</a>"""))
        self.assertEquals(
            str(self.parser.generate("[[poo:foo bar|Foo]]")),
            wrap_result("""<a href="http://example.org/foo%2Bbar">Foo</a>"""))
        self.assertEquals(
            str(self.parser.generate("[[goo:foo bar|Foo]]")),
            wrap_result("""<a href="http://example.org/rab+oof">Foo</a>"""))
        self.assertEquals(
            str(self.parser.generate("[[roo:foo bar|Foo]]")),
            wrap_result("""[[roo:foo bar|Foo]]"""))


class TaintingTest(unittest.TestCase):
    """
    """
    def test_cookies(self):
        self.assertEquals(
            text2html("{{javascript:alert(document.cookie)}}"),
            wrap_result("""<img src="unsafe_uri_detected" alt="unsafe_uri_detected" />"""))
        self.assertEquals(
            text2html("[[javascript:alert(document.cookie)]]"),
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
        result = text2html.render(self.markup, context=context)
        #self.assertEqual(result, wrap_result("steve <em>rad</em>"))


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

