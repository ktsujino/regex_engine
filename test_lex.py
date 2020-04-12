import lex

import unittest

class TestLexicalAnalysis(unittest.TestCase):

    def check_tokens(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for a, e in zip(actual, expected):
            self.assertEqual(type(a), type(e))
            self.assertEqual(a.val, e.val)
    
    def test_empty(self):
        regex = ''
        actual_tokens = lex.lexical_analysis(regex)
        expected_tokens = [
        ]
        self.check_tokens(actual_tokens, expected_tokens)

    def test_chars(self):
        regex = 'ab{'
        actual_tokens = lex.lexical_analysis(regex)
        expected_tokens = [lex.CharToken('a'),
                           lex.CharToken('b'),
                           lex.CharToken('{'),
        ]
        self.check_tokens(actual_tokens, expected_tokens)

    def test_brackets(self):
        regex = 'a[a-z].'
        actual_tokens = lex.lexical_analysis(regex)
        expected_tokens = [lex.CharToken('a'),
                           lex.CharToken('[a-z]'),
                           lex.CharToken('.'),
        ]
        self.check_tokens(actual_tokens, expected_tokens)

    def test_parens(self):
        regex = '([a-z\]]{1,2}b.)+\+'
        actual_tokens = lex.lexical_analysis(regex)
        expected_tokens = [lex.OpenParToken('('),
                           lex.CharToken('[a-z\]]'),
                           lex.QuantificationToken('{1,2}'),
                           lex.CharToken('b'),
                           lex.CharToken('.'),
                           lex.CloseParToken(')'),
                           lex.QuantificationToken('+'),
                           lex.CharToken('+'),
        ]
        self.check_tokens(actual_tokens, expected_tokens)

       
if __name__ == '__main__':
    unittest.main()
