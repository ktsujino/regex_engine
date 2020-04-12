import lex
import syntax

import unittest

class TestSyntacticAnalysis(unittest.TestCase):

    def check_tree(self, actual, expected, verbose=False):
        if verbose:
            print(actual)
        self.assertEqual(type(actual), type(expected))
        if type(actual) == syntax.CharNode:
            self.assertEqual(actual.char_set, expected.char_set)
        elif type(actual) == syntax.QuantificationNode:
            self.assertEqual(actual.lb, expected.lb)
            self.assertEqual(actual.ub, expected.ub)
            self.check_tree(actual.operand, expected.operand, verbose)
        elif type(actual) == syntax.UnionNode or type(actual) == syntax.ConcatenationNode:
            self.assertEqual(len(actual.children), len(expected.children))
            for a, e in zip(actual.children, expected.children):
                self.check_tree(a, e, verbose)
        elif type(actual) == syntax.EpsilonNode:
            pass
    
    def test_empty(self):
        regex = ''
        actual_tokens = lex.lexical_analysis(regex)
        actual_tree = syntax.syntactic_analysis(actual_tokens)
        expected_tree = syntax.EpsilonNode()
        self.check_tree(actual_tree, expected_tree)

    def test_concat(self):
        regex = '[a-c]b.'
        actual_tokens = lex.lexical_analysis(regex)
        actual_tree = syntax.syntactic_analysis(actual_tokens)
        expected_tree = syntax.ConcatenationNode([
            syntax.CharNode({'a', 'b', 'c'}),
            syntax.CharNode({'b'}),
            syntax.CharNode({chr(x) for x in range(128)}),
            ])
        self.check_tree(actual_tree, expected_tree)

    def test_quantification(self):
        regex = '.*'
        actual_tokens = lex.lexical_analysis(regex)
        actual_tree = syntax.syntactic_analysis(actual_tokens)
        expected_tree = syntax.QuantificationNode(lb=0, ub=float('inf'),
                                                  operand=syntax.CharNode({chr(x) for x in range(128)}))
        self.check_tree(actual_tree, expected_tree)

    def test_grouping(self):
        regex = '((ab?)c)+'
        actual_tokens = lex.lexical_analysis(regex)
        actual_tree = syntax.syntactic_analysis(actual_tokens)
        expected_tree = \
            syntax.QuantificationNode(
                lb=1, ub=float('inf'),
                operand=syntax.ConcatenationNode([
                    syntax.ConcatenationNode([
                        syntax.CharNode({'a'}),
                        syntax.QuantificationNode(lb=0, ub=1, operand=\
                                                  syntax.CharNode({'b'}))]),
                    syntax.CharNode({'c'})]),
                )
        self.check_tree(actual_tree, expected_tree)

    def test_union(self):
        regex = '(a|b)|c+'
        actual_tokens = lex.lexical_analysis(regex)
        actual_tree = syntax.syntactic_analysis(actual_tokens)
        expected_tree = \
            syntax.UnionNode([
                syntax.UnionNode([
                    syntax.CharNode({'a'}),
                    syntax.CharNode({'b'})
                    ]),
                syntax.QuantificationNode(lb=1, ub=float('inf'), operand=\
                                          syntax.CharNode({'c'}))])
        self.check_tree(actual_tree, expected_tree)
        
if __name__ == '__main__':
    unittest.main()
