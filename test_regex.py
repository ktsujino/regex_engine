import regex
import unittest

class TestMatch(unittest.TestCase):
    def test_range_quantifier(self):
        pattern = 'a{2,4}b*'
        matcher = regex.compile_regex(pattern)
        self.assertEqual(matcher.match('abb'), False)
        self.assertEqual(matcher.match('aaa'), True)
        self.assertEqual(matcher.match('aaabb'), True)
        self.assertEqual(matcher.match('aaaaabb'), False)

    def test_nested_quantifier(self):
        pattern = '(a+b)*c+'
        matcher = regex.compile_regex(pattern)
        self.assertEqual(matcher.match('aababc'), True)
        self.assertEqual(matcher.match('c'), True)
        self.assertEqual(matcher.match('aaaabab'), False)

    def test_question_quantifier(self):
        pattern = '((a?b)*)+'
        matcher = regex.compile_regex(pattern)
        self.assertEqual(matcher.match(''), True)
        self.assertEqual(matcher.match('bab'), True)
        self.assertEqual(matcher.match('aab'), False)

    def test_dot(self):
        pattern = 'a.b'
        matcher = regex.compile_regex(pattern)
        self.assertEqual(matcher.match('axb'), True)
        self.assertEqual(matcher.match('ab'), False)
        self.assertEqual(matcher.match('axbx'), False)

if __name__ == '__main__':
    unittest.main()
