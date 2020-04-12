import regex
import unittest

class TestNFA(unittest.TestCase):
    def test_dump(self):
        pattern = 'a{2,4}b*'
        dfa = regex.compile_automaton(pattern)
        self.assertEqual(dfa.match('aaabb'), True)


if __name__ == '__main__':
    unittest.main()
