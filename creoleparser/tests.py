# tests.py
#
# Copyright (c) 2007 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

from __init__ import creole_to_xhtml
from dialects import Creole10
from core import Parser

def test_creole_to_xhtml():

    assert creole_to_xhtml('**strong** soft\n') == '<p><strong>strong</strong> soft</p>\n'
    assert creole_to_xhtml('//this**strong** soft//') == '<p><em>this<strong>strong</strong> soft</em></p>\n'
    assert creole_to_xhtml('steve **is strong**\n{{{\nnot **weak**\n}}}\n') == \
            '<p>steve <strong>is strong</strong></p>\n<pre>not **weak**\n</pre>\n'
    assert creole_to_xhtml('{{{no **wiki** in here}}} but //here// is fine') == \
            '<p><tt>no **wiki** in here</tt> but <em>here</em> is fine</p>\n'
    assert creole_to_xhtml('steve **is strong //you know\n dude{{{not **weak**}}}\n') == \
            '<p>steve <strong>is strong <em>you know\n dude<tt>not **weak**</tt></em></strong></p>\n'

    assert creole_to_xhtml(
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

    assert creole_to_xhtml(r"""
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

    assert creole_to_xhtml(r"""
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

    assert creole_to_xhtml("\
Names of pages have to LookLikeThis.\r\nIt's called a WikiName.\r\nIf you write\
 a word that LookLikeThis.\r\n") == """\
<p>Names of pages have to LookLikeThis.
It's called a WikiName.
If you write a word that LookLikeThis.</p>
"""

    assert creole_to_xhtml(r"""
{{{
** some ** unformatted {{{ stuff }}} ~~~
 }}}
}}}
""") == """\
<pre>** some ** unformatted {{{ stuff }}} ~~~
}}}
</pre>
"""

    assert creole_to_xhtml("""\
{{{** some ** unformatted {{{ stuff ~~ }}}}}}""") == """\
<p><tt>** some ** unformatted {{{ stuff ~~ }}}</tt></p>
"""

    assert creole_to_xhtml("""\
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

    assert creole_to_xhtml(r"""
Go to [[http://www.google.com]], it is [[http://www.google.com| Google]]\\
even [[This Page]] is nice like [[This Page|this]].\\
As is [[Ohana:Home|This one]].""") == """\
<p>Go to <a href="http://www.google.com">http://www.google.com</a>, it is <a href="http://www.google.com">Google</a><br />
even <a href="http://www.wikicreole.org/wiki/This_Page">This Page</a> is nice like <a href="http://www.wikicreole.org/wiki/This_Page">this</a>.<br />
As is <a href="http://wikiohana.net/cgi-bin/wiki.pl/Home">This one</a>.</p>
"""

    assert creole_to_xhtml(r"""
* this is list **item one**
** item one - //subitem 1//
### one **http://www.google.com**
### two [[Creole1.0]]
### three\\covers\\many\\lines
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
<ul><li> this is list <strong>item one</strong>
<ul><li> item one - <em>subitem 1</em>
<ol><li> one <strong><a href="http://www.google.com">http://www.google.com</a></strong>
</li>
<li> two <a href="http://www.wikicreole.org/wiki/Creole1.0">Creole1.0</a>
</li>
<li> three<br />covers<br />many<br />lines
</li>
</ol></li>
<li> <em>subitem 2</em>
<ol><li> what is this?
</li>
<li> no idea?
<ul><li> A
</li>
<li> B
</li>
</ul></li>
<li> And lots of
drivel here
</li>
</ol></li>
<li> <em>subitem 3</em>
<ul><li> huh?
</li>
</ul></li>
</ul></li>
<li> <strong>item two</strong>
</li>
<li> <strong>item three</strong>
</li>
</ul>
<ol><li> new ordered list, item 1
</li>
<li> item 2
<ol><li> sub item
</li>
<li>sub item
</li>
</ol></li>
</ol>
"""

    assert creole_to_xhtml(r"""
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

def test_no_wiki_monospace_option():
    dialect = Creole10(no_wiki_monospace=False)
    parser = Parser(dialect)
    assert parser(r"""
This block of {{{no_wiki **shouldn't** be monospace}}} now""") == """\
<p>This block of <span>no_wiki **shouldn't** be monospace</span> now</p>
"""
    
def test_use_additions_option():
    dialect = Creole10(use_additions=True)
    parser = Parser(dialect)
    assert parser(r"""
This block of ##text **should** be monospace## now""") == """\
<p>This block of <tt>text <strong>should</strong> be monospace</tt> now</p>
"""

def _test():
    import doctest
    doctest.testmod()
    test_creole_to_xhtml()
    test_no_wiki_monospace_option()
    test_use_additions_option()

if __name__ == "__main__":
    _test()


