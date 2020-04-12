import automata
import lex
import syntax

def compile_automaton(regex):
        tokens = lex.lexical_analysis(regex)
        ast = syntax.syntactic_analysis(tokens)
        nfa = automata.NFA.from_ast(ast)
        nfa.epsilon_elimination()
        dfa = automata.DFA.from_nfa(nfa)
        return dfa