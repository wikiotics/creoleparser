# tests.py
#
# Copyright (c) 2007 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

import genshi.builder as bldr

from __init__ import text2html, creole2html
from dialects import Creole10
from core import Parser

def check_markup(m, s, p=text2html,paragraph=True):
    if paragraph:
        out = '<p>%s</p>\n' % s
    else:
        out = s + '\n'
    #print repr(out)
    gen = p.render(m)
    #print repr(gen)
    assert out == gen

def test_creole2html():

##    print creole2html(r"""
##Go to [[http://www.google.com]], it is [[http://www.google.com| <<luca Google>>]]\\
##even [[This Page Here]] is <<steve the steve macro!>> nice like [[New Page|this]].\\
##This is the <<sue sue macro!>> and this is the <<luca luca macro!>>.\\
##Don't touch {{{<<steve this!>>}}}.\\
##<<mateo>>A body!<</mateo>>\\
##As is [[Ohana:Home|This one]].""")
    
    assert creole2html(r"""
Go to [[http://www.google.com]], it is [[http://www.google.com| <<luca Google>>]]\\
even [[This Page Here]] is <<steve the steve macro!>> nice like [[New Page|this]].\\
This is the <<sue sue macro!>> and this is the <<luca luca macro!>>.\\
Don't touch {{{<<steve this!>>}}}.\\
<<mateo>>A body!<</mateo>>\\
As is [[Ohana:Home|This one]].""") == """\
<p>Go to <a href="http://www.google.com">http://www.google.com</a>, it is <a href="http://www.google.com">&lt;&lt;luca Google&gt;&gt;</a><br />
even <a href="http://www.wikicreole.org/wiki/This_Page_Here">This Page Here</a> is &lt;&lt;steve the steve macro!&gt;&gt; nice like <a href="http://www.wikicreole.org/wiki/New_Page">this</a>.<br />
This is the &lt;&lt;sue sue macro!&gt;&gt; and this is the &lt;&lt;luca luca macro!&gt;&gt;.<br />
Don't touch <tt>&lt;&lt;steve this!&gt;&gt;</tt>.<br />
&lt;&lt;mateo&gt;&gt;A body!&lt;&lt;/mateo&gt;&gt;<br />
As is <a href="http://wikiohana.net/cgi-bin/wiki.pl/Home">This one</a>.</p>
"""

##    print creole2html(r"""
##<<mateo>>This is the some random text
##over two lines<</mateo>><<mila>>A body!<</mila>>\\
##As is [[Ohana:Home|This one]].""")

    assert creole2html(r"""
<<mateo>>This is the some random text
over two lines<</mateo>><<mila>>A body!<</mila>>\\
As is [[Ohana:Home|This one]].""") == """\
<p>&lt;&lt;mateo&gt;&gt;This is the some random text
over two lines&lt;&lt;/mateo&gt;&gt;&lt;&lt;mila&gt;&gt;A body!&lt;&lt;/mila&gt;&gt;<br />
As is <a href="http://wikiohana.net/cgi-bin/wiki.pl/Home">This one</a>.</p>
"""

def test_text2html():

    assert text2html('**strong** soft\n') == '<p><strong>strong</strong> soft</p>\n'
    assert text2html('//this**strong** soft//') == '<p><em>this<strong>strong</strong> soft</em></p>\n'
    assert text2html('steve **is strong**\n{{{\nnot **weak**\n}}}\n') == \
            '<p>steve <strong>is strong</strong></p>\n<pre>not **weak**\n</pre>\n'
    assert text2html('{{{no **wiki** in here}}} but //here// is fine') == \
            '<p><span>no **wiki** in here</span> but <em>here</em> is fine</p>\n'
    assert text2html('steve **is strong //you know\n dude{{{not **weak**}}}\n') == \
            '<p>steve <strong>is strong <em>you know\n dude<span>not **weak**</span></em></strong></p>\n'
    
    assert text2html(
r"""   |= Item|= Size|= Price |
  | fish | **big**  |cheap   |
  | crab | small|expesive|

  |= Item|= Size|= Price 
  | fish | big  |//cheap//   
  | crab | small|**very\\expesive**
  """) == """\
<table><tr><th>Item</th><th>Size</th><th>Price</th></tr>
<tr><td>fish</td><td><strong>big</strong></td><td>cheap</td></tr>
<tr><td>crab</td><td>small</td><td>expesive</td></tr>
</table>
<table><tr><th>Item</th><th>Size</th><th>Price</th></tr>
<tr><td>fish</td><td>big</td><td><em>cheap</em></td></tr>
<tr><td>crab</td><td>small</td><td><strong>very<br />expesive</strong></td></tr>
</table>
"""

    assert text2html(r"""
  = Level 1 (largest) =
== Level 2 ==
 === Level 3 ===
==== Level 4 ====
===== Level 5 =====
====== Level 6 ======
=== Also level 3
=== Also level 3 =
=== Also level 3 ==
=== **is** //parsed// ===
  """) == """\
<h1>Level 1 (largest)</h1>
<h2>Level 2</h2>
<h3>Level 3</h3>
<h4>Level 4</h4>
<h5>Level 5</h5>
<h6>Level 6</h6>
<h3>Also level 3</h3>
<h3>Also level 3</h3>
<h3>Also level 3</h3>
<h3><strong>is</strong> <em>parsed</em></h3>
""" 

##    print text2html(r"""
##a lone escape ~ in the middle of a line
##or at the end ~
##a double ~~ in the middle
##at end ~~
##preventing ~** **bold** and ~// //italics//
## ~= stopping headers!
##| in table~| cells | too!
##""")


    assert text2html(r"""
a lone escape ~ in the middle of a line
or at the end ~
a double ~~ in the middle
at end ~~
preventing ~** **bold** and ~// //italics//
 ~= stopping headers!
| in table~| cells | too!
""") == """\
<p>a lone escape ~ in the middle of a line
or at the end ~
a double ~ in the middle
at end ~
preventing ** <strong>bold</strong> and // <em>italics</em>
 = stopping headers!</p>
<table><tr><td>in table| cells</td><td>too!</td></tr>
</table>
"""

    assert text2html("\
Names of pages have to LookLikeThis.\r\nIt's called a WikiName.\r\nIf you write\
 a word that LookLikeThis.\r\n") == """\
<p>Names of pages have to LookLikeThis.
It's called a WikiName.
If you write a word that LookLikeThis.</p>
"""

    assert text2html(r"""
{{{
** some ** unformatted {{{ stuff }}} ~~~
 }}}
}}}
""") == """\
<pre>** some ** unformatted {{{ stuff }}} ~~~
}}}
</pre>
"""

    assert text2html("""\
{{{** some ** unformatted {{{ stuff ~~ }}}}}}""") == """\
<p><span>** some ** unformatted {{{ stuff ~~ }}}</span></p>
"""

    assert text2html("""\
|http://www.google.com| steve|

hello **[[http://www.google.com|Google]]**
= http://www.yahoo.com
== ~http://www.yahoo.com
""") == """\
<table><tr><td><a href="http://www.google.com">http://www.google.com</a></td><td>steve</td></tr>
</table>
<p>hello <strong><a href="http://www.google.com">Google</a></strong></p>
<h1><a href="http://www.yahoo.com">http://www.yahoo.com</a></h1>
<h2>http://www.yahoo.com</h2>
"""

    assert text2html(r"""
Go to [[http://www.google.com]], it is [[http://www.google.com| Google]]\\
even [[This Page Here]] is nice like [[This Page|this]].\\
As is [[Ohana:Home|This one]].""") == """\
<p>Go to <a href="http://www.google.com">http://www.google.com</a>, it is <a href="http://www.google.com">Google</a><br />
even <a href="http://www.wikicreole.org/wiki/This_Page_Here">This Page Here</a> is nice like <a href="http://www.wikicreole.org/wiki/This_Page">this</a>.<br />
As is <a href="http://wikiohana.net/cgi-bin/wiki.pl/Home">This one</a>.</p>
"""

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

    assert text2html(r"""
* this is list **item one**
** item one - //subitem 1//
### one **http://www.google.com**
### two [[Creole1.0]]
### three\\covers\\many~\\lines
** //subitem 2//
### what is this?
### no idea?
**** A
**** B
### And lots of
drivel here
** //subitem 3//
*** huh?
* **item two
* **item three**
# new ordered list, item 1
# item 2
## sub item
##sub item
""") == """\
<ul><li>this is list <strong>item one</strong>
<ul><li>item one - <em>subitem 1</em>
<ol><li>one <strong><a href="http://www.google.com">http://www.google.com</a></strong></li>
<li>two <a href="http://www.wikicreole.org/wiki/Creole1.0">Creole1.0</a></li>
<li>three<br />covers<br />many\\\\lines</li></ol></li>
<li><em>subitem 2</em>
<ol><li>what is this?</li>
<li>no idea?
<ul><li>A</li>
<li>B</li></ul></li>
<li>And lots of
drivel here</li></ol></li>
<li><em>subitem 3</em>
<ul><li>huh?</li></ul></li></ul></li>
<li><strong>item two</strong></li>
<li><strong>item three</strong></li></ul>
<ol><li>new ordered list, item 1</li>
<li>item 2
<ol><li>sub item</li>
<li>sub item</li></ol></li></ol>
"""

    assert text2html(r"""
= Big Heading 
----
\\
|nice picture |{{campfire.jpg}}|\\
|same picture as a link| [[http://google.com | {{ campfire.jpg | campfire.jpg }} ]]|""") == """\
<h1>Big Heading</h1>
<hr />
<p><br /></p>
<table><tr><td>nice picture</td><td><img src="campfire.jpg" alt="campfire.jpg" /></td><td><br /></td></tr>
<tr><td>same picture as a link</td><td><a href="http://google.com"><img src="campfire.jpg" alt="campfire.jpg" /></a></td></tr>
</table>
"""
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
    
    assert text2html(r"""
hello
; This is a title:
: Yes, sir!
; This is~: a another title:
: Yes, sir!
** and this emphasized!
; Another title : it's definition
; Another title ~: it's definition **NOT**
: here it is
*this is a list!!
; Wiki
; Creole
what about this?
: something neat
: two defintioins?""") == """\
<p>hello</p>
<dl><dt>This is a title:</dt>
<dd>Yes, sir!</dd>
<dt>This is: a another title:</dt>
<dd>Yes, sir!
<strong> and this emphasized!</strong></dd>
<dt>Another title</dt>
<dd>it's definition</dd>
<dt>Another title : it's definition <strong>NOT</strong></dt>
<dd>here it is</dd>
</dl>
<ul><li>this is a list!!</li></ul>
<dl><dt>Wiki</dt>
<dt>Creole</dt>
<dd>what about this?</dd>
<dd>something neat</dd>
<dd>two defintioins?</dd>
</dl>
"""

    assert text2html(r"""
hello
^^superscript^^
,,subscript,,
__underlined__

//^^superscript^^
,,subscript,,
__underlined__//

^^//superscript//\\hello^^
,,sub**scr**ipt,,
##__underlined__##

{{{^^//superscript//\\hello^^
,,sub**scr**ipt,,}}}
##__underlined__##""") == """\
<p>hello
<sup>superscript</sup>
<sub>subscript</sub>
<u>underlined</u></p>
<p><em><sup>superscript</sup>
<sub>subscript</sub>
<u>underlined</u></em></p>
<p><sup><em>superscript</em><br />hello</sup>
<sub>sub<strong>scr</strong>ipt</sub>
<tt><u>underlined</u></tt></p>
<p><span>^^//superscript//\\\\hello^^
,,sub**scr**ipt,,</span>
<tt><u>underlined</u></tt></p>
"""

    assert text2html(r"""
double tildes ~~ in the middle
double tildes at the end ~~
tilde in the middle ~ of a line
tilde at the end of a line ~
tilde at the end of a paragraph ~

tilde at the start of a ~word
double tilde at the start of a ~~word
double tilde at the end of a paragraph ~~""") == """\
<p>double tildes ~ in the middle
double tildes at the end ~
tilde in the middle ~ of a line
tilde at the end of a line ~
tilde at the end of a paragraph ~</p>
<p>tilde at the start of a word
double tilde at the start of a ~word
double tilde at the end of a paragraph ~</p>
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

def test_wiki_links_class_func():

    def class_func(page_name):
        if page_name == 'NewPage':
            return 'nonexistent'

    def path_func(page_name):
        if page_name == 'ThisPageHere':
            path = 'Special/ThisPageHere'
        else:
            path = page_name
        return path
            
        
    dialect = Creole10(
        wiki_links_base_url='http://creoleparser.x10hosting.com/cgi-bin/creolepiki/',
        wiki_links_space_char='',
        use_additions=True,
        no_wiki_monospace=False,
        wiki_links_class_func=class_func,
        wiki_links_path_func=path_func)

    parser = Parser(dialect)

##    print parser(r"""
##Go to [[http://www.google.com]], it is [[http://www.google.com| Google]]\\
##even [[This Page Here]] is nice like [[New Page|this]].\\
##As is [[Ohana:Home|This one]].""")

    assert parser(r"""
Go to [[http://www.google.com]], it is [[http://www.google.com| Google]]\\
even [[This Page Here]] is nice like [[New Page|this]].\\
As is [[Ohana:Home|This one]].""") == """\
<p>Go to <a href="http://www.google.com">http://www.google.com</a>, it is <a href="http://www.google.com">Google</a><br />
even <a href="http://creoleparser.x10hosting.com/cgi-bin/creolepiki/Special/ThisPageHere">This Page Here</a> is nice like <a class="nonexistent" href="http://creoleparser.x10hosting.com/cgi-bin/creolepiki/NewPage">this</a>.<br />
As is [[Ohana:Home|This one]].</p>
"""

def test_marco_func():

    def a_macro_func(macro_name, arg_string,body):
        if macro_name == 'steve':
            return '**' + arg_string + '**'
        if macro_name == 'luca':
            return bldr.tag.strong(arg_string).generate()
        if macro_name == 'mateo':
            return bldr.tag.em(body).generate()
        if macro_name == 'Reverse':
            return body[::-1]
        if macro_name == 'Reverse-it':
            return body[::-1]
        if macro_name == 'ReverseIt':
            return body[::-1]
        if macro_name == 'lib.ReverseIt-now':
            return body[::-1]
        
    dialect = Creole10(
        wiki_links_base_url='http://creoleparser.x10hosting.com/cgi-bin/creolepiki/',
        wiki_links_space_char='',
        use_additions=True,
        no_wiki_monospace=False,
        macro_func=a_macro_func)

    parser = Parser(dialect)

    check_markup(u'<<mateo>>fooɤ<</mateo>>','<em>foo\xc9\xa4</em>',p=parser,paragraph=False)
    check_markup(u'<<steve fooɤ>>','<strong> foo\xc9\xa4</strong>',p=parser)
    check_markup('<<Reverse>>foo<</Reverse>>','oof',p=parser)
    check_markup('<<Reverse-it>>foo<</Reverse-it>>','oof',p=parser)
    check_markup('<<ReverseIt>>foo<</ReverseIt>>','oof',p=parser)
    check_markup('<<lib.ReverseIt-now>>foo<</lib.ReverseIt-now>>','oof',p=parser)
    check_markup('<<bad name>>foo<</bad name>>',
                 '&lt;&lt;bad name&gt;&gt;foo&lt;&lt;/bad name&gt;&gt;',p=parser)
    check_markup('<<unknown>>foo<</unknown>>',
                 '&lt;&lt;unknown&gt;&gt;foo&lt;&lt;/unknown&gt;&gt;',p=parser,paragraph=False)
    check_markup(u'<<luca boo>>foo<</unknown>>',
                 '<strong> boo</strong>foo&lt;&lt;/unknown&gt;&gt;',p=parser)

    

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
As is [[Ohana:Home|This one]].</p>
&lt;&lt;mila&gt;&gt;A body!&lt;&lt;/mila&gt;&gt;
"""

def test_interwiki_links():

    def iw_func(name):
        return name[::-1]

    d = Creole10(
        interwiki_links_funcs={
            'moo':iw_func,
            'goo':iw_func,
        },
        interwiki_links_base_urls={
            'goo': 'http://example.org',
            'poo': 'http://example.org',
        },
        interwiki_links_space_chars={
            'goo': '+', 
            'poo': '+',
        },
    )
    p = Parser(d)

    def checklink(m, a, p=p):
        out = '<p>%s</p>\n' % a
        gen = str(p.generate(m))
        #print gen
        assert out == gen

    checklink('[[moo:foo bar|Foo]]', '<a href="rab_oof">Foo</a>')
    checklink('[[goo:foo|Foo]]', '<a href="http://example.org/oof">Foo</a>')
    checklink('[[poo:foo|Foo]]', '<a href="http://example.org/foo">Foo</a>')
    checklink('[[poo:foo bar|Foo]]', '<a href="http://example.org/foo+bar">Foo</a>')
    checklink('[[goo:foo bar|Foo]]', '<a href="http://example.org/rab+oof">Foo</a>')
    checklink('[[roo:foo bar|Foo]]', '[[roo:foo bar|Foo]]')
    assert '[[noo:foo|Foo]]' == '[[noo:foo|Foo]]'

def test_sanitizing():
    check_markup('{{javascript:alert(document.cookie)}}','<img src="unsafe_uri_detected" alt="unsafe_uri_detected" />')
    

def _test():
    import doctest
    doctest.testmod()
    test_creole2html()
    test_text2html()
    test_no_wiki_monospace_option()
    test_use_additions_option()
    test_place_holders()
    test_wiki_links_class_func()
    test_marco_func()
    test_interwiki_links()
    test_sanitizing()

if __name__ == "__main__":
    _test()



