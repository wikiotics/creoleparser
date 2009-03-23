import unittest
from __init__ import parse_args
from core import ArgParser
from dialects import Creepy


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
        self.assertEquals(
            self.parse("""one 'two' "three" """),
            (['one', 'two', "three"],{}))
    def test_mixed_args(self):
        self.assertEquals(
            self.parse("one one = oneval "),
            (['one'],{'one': 'oneval'}))

    def test_quoting(self):
        self.assertEquals(
            self.parse(""" "height = 54in" one = "don't try it" """),
            (['height = 54in'],{'one': "don't try it"}))
   

class ListTest(unittest.TestCase, BaseTest):
    """
    """
    def setUp(self):
        self.parse = ArgParser(Creepy(),force_strings=False)
        
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
            self.parse(" one  = 'oneval' foo "),
            ([],{'one':['oneval','foo']}))  

class NoListTest(unittest.TestCase, BaseTest):
    """
    """
    def setUp(self):
        self.parse = ArgParser(Creepy(),force_strings=True)
        
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

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ListTest),
        unittest.makeSuite(NoListTest),
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
