import unittest
from string import lower

from __init__ import parse_args
from core import ArgParser
from dialects import creepy_base


class BaseTest(object):
    """

    """
    parse = parse_args

    def test_pos_args(self):
        self.assertEquals(
            self.parse("one two"),
            (['one', 'two'],{}))
        self.assertEquals(
         self.parse(""),
            ([],{}))
    def test_kw_args(self):
        self.assertEquals(
            self.parse(" one = oneval "),
            ([],{'one': 'oneval'}))
        self.assertEquals(
            self.parse("one = oneval two=twoval"),
            ([],{'one': 'oneval','two': 'twoval'}))
        self.assertEquals(
            self.parse("""one = 'oneval' two = "twoval" """),
            ([],{'one': 'oneval','two': 'twoval'}))

    def test_mixed_args(self):
        self.assertEquals(
            self.parse("one one = oneval "),
            (['one'],{'one': 'oneval'}))

    def test_quoting(self):
        self.assertEquals(
            self.parse("""one 'two' "three" """),
            (['one', 'two', "three"],{}))
        self.assertEquals(
            self.parse(""" "height = 54in" one = "don't try it" """),
            (['height = 54in'],{'one': "don't try it"}))

    def test_empty_strings(self):
        self.assertEquals(
            self.parse(""" '' '' foo='' boo = """),
            (['', ''], {'foo': '', 'boo': ''}))
  

class ListTest(unittest.TestCase, BaseTest):
    """
    """
    def setUp(self):
        self.parse = ArgParser(creepy_base(),force_strings=False)
        
    def test_pos_args(self):
        super(ListTest, self).test_pos_args()
        self.assertEquals(
            self.parse(" one [ two ] "),
            (['one',['two']],{}))
        self.assertEquals(
            self.parse(" one [two three ] "),
            (['one', ['two', 'three']],{}))
        self.assertEquals(
            self.parse(" [one two] "),
            ([['one','two']],{}))

    def test_kw_args(self):
        super(ListTest, self).test_kw_args()
        self.assertEquals(
            self.parse(" one  = [ oneval ] two = twoval "),
            ([],{'one':['oneval'],'two':'twoval'}))

    def test_mixed_args(self):
        super(ListTest, self).test_mixed_args()
        self.assertEquals(
            self.parse(" [one] one  = [ oneval ] "),
            ([['one']],{'one':['oneval']}))

    def test_implicit_list(self):
        self.assertEquals(
            self.parse(" one  = oneval foo two = twoval"),
            ([],{'one':['oneval','foo'],'two':'twoval'}))
        self.assertEquals(
            self.parse(" one  = oneval foo one = twoval"),
            ([],{'one':['oneval','foo', 'twoval']}))
        self.assertEquals(
            self.parse(" one  = 'oneval' foo "),
            ([],{'one':['oneval','foo']}))  

class NoListTest(unittest.TestCase, BaseTest):
    """
    """
    def setUp(self):
        self.parse = ArgParser(creepy_base(),force_strings=True)
        
    def test_pos_args(self):
        super(NoListTest, self).test_pos_args()
        self.assertEquals(
            self.parse(" one [ two ] "),
            (['one','two'],{}))
        self.assertEquals(
            self.parse(" one [two three ] "),
            (['one', 'two three'],{}))
        self.assertEquals(
            self.parse(" [one two] "),
            (['one two'],{}))

    def test_kw_args(self):
        super(NoListTest, self).test_kw_args()
        self.assertEquals(
            self.parse(" one  = [ oneval ] "),
            ([],{'one':'oneval'}))

    def test_mixed_args(self):
        super(NoListTest, self).test_mixed_args()
        self.assertEquals(
            self.parse(" [one] one  = [ oneval ] "),
            (['one'],{'one':'oneval'}))
        
    def test_implicit_list(self):
        self.assertEquals(
            self.parse(" one  = oneval foo "),
            ([],{'one':'oneval foo'}))
        self.assertEquals(
            self.parse(" one  = 'oneval' foo "),
            ([],{'one':'oneval foo'}))  

class KeyFuncTest(unittest.TestCase, BaseTest):
    """
    """
    def setUp(self):
        self.parse = ArgParser(creepy_base(key_func=lower),force_strings=False)
        
    def test_kw_args(self):
        super(KeyFuncTest, self).test_kw_args()
        self.assertEquals(
            self.parse(" ONE  = [ oneval ] Two = twoval "),
            ([],{'one':['oneval'],'two':'twoval'}))

    def test_mixed_args(self):
        super(KeyFuncTest, self).test_mixed_args()
        self.assertEquals(
            self.parse(" [one] One  = [ oneval ] "),
            ([['one']],{'one':['oneval']}))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ListTest),
        unittest.makeSuite(NoListTest),
        unittest.makeSuite(KeyFuncTest),
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
