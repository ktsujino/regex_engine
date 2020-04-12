import syntax
from collections import defaultdict

class NFAState:
    def __init__(self):
        self.id = None
        self.transitions = defaultdict(set)

    def epsilon_expansion(self):
        epsilon_set = set()
        new_set = {self}
        while new_set:
            next_new_set = set()
            for state in new_set:
                for dest_state in state.transitions[None]:
                    if dest_state not in new_set and dest_state not in epsilon_set:
                        next_new_set.add(dest_state)
            epsilon_set |= new_set
            new_set = next_new_set
        self.epsilon_set = epsilon_set

    def __str__(self):
        out = '%s: {%s}' % (str(self.id),
                            ', '.join(['%s->%s' % (char, '|'.join([str(state.id) for state in dest_states])) \
                                       for char, dest_states in self.transitions.items() if dest_states]))
        return out
                                                   

class NFA: # Non-deterministic Finite Automaton
    def __init__(self, init_state=None, accept_state=None):
        if not init_state:
            init_state = NFAState()
        if not accept_state:
            accept_state = NFAState()
        self.init_state = init_state
        self.accept_state = accept_state

    def __str__(self):
        out = '[init: %s (%s), accept: %s]\n' % \
            (str(self.init_state.id),
             '|'.join([str(state.id) for state in self.init_state.epsilon_set]) if hasattr(self.init_state, 'epsilon_set') else '',
             str(self.accept_state.id))
        for state in self.enum_states():
            out += str(state) + '\n'
        return out

    def append_nfa(self, nfa):
        self.accept_state.transitions = nfa.init_state.transitions
        self.accept_state = nfa.accept_state

    @classmethod
    def make_nfa_optional(cls, nfa):
        nfa.init_state.transitions[None].add(nfa.accept_state)
        return nfa

    @classmethod
    def make_kleene_closure_of_nfa(cls, target):
        nfa = NFA()
        nfa.init_state.transitions[None].add(target.init_state)
        target.accept_state.transitions[None].add(nfa.accept_state)
        target.accept_state.transitions[None].add(target.init_state)
        nfa.init_state.transitions[None].add(nfa.accept_state)
        return nfa

    @classmethod
    def from_ast(cls, ast_node):
        type2method = {
            syntax.EpsilonNode :        NFA.from_epsilon_ast_node,
            syntax.CharNode :           NFA.from_char_ast_node,
            syntax.ConcatenationNode :  NFA.from_concatenation_ast_node,
            syntax.UnionNode :          NFA.from_union_ast_node,
            syntax.QuantificationNode : NFA.from_quantification_ast_node,
            }
        nfa = type2method[type(ast_node)](ast_node)
        return nfa

    @classmethod
    def from_epsilon_ast_node(cls, ast_node=None):
        nfa = NFA()
        nfa.init_state.transitions[None].add(nfa.accept_state)
        return nfa

    @classmethod
    def from_char_ast_node(cls, ast_node):
        nfa = NFA()
        for char in ast_node.char_set:
            nfa.init_state.transitions[char].add(nfa.accept_state)
        return nfa

    @classmethod
    def from_concatenation_ast_node(cls, ast_node):
        children_nfa = [NFA.from_ast(child) for child in ast_node.children]
        nfa = None
        for child_nfa in children_nfa:
            if not nfa:
                nfa = child_nfa
            else:
                nfa.append_nfa(child_nfa)
        return nfa

    @classmethod
    def from_union_ast_node(cls, ast_node):
        children_ast = [NFA.from_ast(child) for child in ast_node.children]
        nfa = NFA()
        for child_ast in children_ast:
            nfa.init_state.transitions[None].add(child_ast.init_state)
            child_ast.accept_state.transitions[None].add(nfa.accept_state)
        return nfa

    @classmethod
    def from_quantification_ast_node(cls, ast_node):
        state = NFAState()
        nfa = NFA(init_state=state, accept_state=state)
        for _ in range(ast_node.lb):
            operand_nfa = NFA.from_ast(ast_node.operand)
            nfa.append_nfa(operand_nfa)
        if ast_node.ub < float('inf'):
            for _ in range(ast_node.lb, ast_node.ub):
                optional_nfa = NFA.make_nfa_optional(NFA.from_ast(ast_node.operand))
                nfa.append_nfa(optional_nfa)
        else:
            kleene_closure_nfa = NFA.make_kleene_closure_of_nfa(NFA.from_ast(ast_node.operand))
            nfa.append_nfa(kleene_closure_nfa)
        return nfa

    def enum_states(self):
        states = set()
        stack = [self.init_state]
        while stack:
            state = stack.pop(-1)
            if state in states:
                continue
            states.add(state)
            for next_states in state.transitions.values():            
                for next_state in next_states:
                    stack.append(next_state)
            if hasattr(state, 'epsilon_set'):
                stack += list(state.epsilon_set)

        return states
                    
    def epsilon_expansion_and_numbering(self):
        i = 0
        for state in self.enum_states():
            state.epsilon_expansion()
            state.id = i
            i += 1
            
    def epsilon_elimination(self):
        self.epsilon_expansion_and_numbering()
        for state in self.enum_states():
            del state.transitions[None]
            for char, dest_states in state.transitions.items():
                expanded_destinations = set()
                for dest_state in dest_states:
                    expanded_destinations |= dest_state.epsilon_set
                state.transitions[char] = expanded_destinations

class DFAState:
    def __init__(self, _id):
        self.id = _id
        self.transitions = {}

    def __str__(self):
        out = '%s: {%s}' % (str(self.id),
                            ', '.join(['%s->%s' % (char, str(dest_state.id)) \
                                       for char, dest_state in self.transitions.items()]))
        return out

class DFA: # Deterministic Finite Automaton
    def __init__(self):
        self.init_state = None
        self.accept_states = set()

    def __str__(self):
        out = '[init: %s, accept: %s]\n' % \
            (str(self.init_state.id),
             '|'.join([str(state.id) for state in self.accept_states]))
        for state in self.enum_states():
            out += str(state) + '\n'
        return out

    def match(self, s):
        state = self.init_state
        for c in s:
            if c not in state.transitions:
                return False
            state = state.transitions[c]
        if state in self.accept_states:
            return True
        else:
            return False

    @classmethod
    def merge_transitions(cls, transitions):
        merged = defaultdict(set)
        for transition in transitions:
            for char, dest_states in transition.items():
                merged[char] |= dest_states
        return merged

    @classmethod
    def from_nfa(cls, nfa):
        dfa = DFA()
        nfas2dfas = defaultdict(lambda: DFAState(len(nfas2dfas)))
        init_nfas = frozenset(nfa.init_state.epsilon_set)
        stack = [init_nfas]
        dfa.init_state = nfas2dfas[init_nfas]
        done_nfas = set()
        while stack:
            nfas = stack.pop(-1)
            if nfas in done_nfas:
                continue
            done_nfas.add(nfas)
            transitions = DFA.merge_transitions([state.transitions for state in nfas])
            dfas = nfas2dfas[nfas]
            for char, next_nfas in transitions.items():
                next_nfas = frozenset(next_nfas)
                dfas.transitions[char] = nfas2dfas[next_nfas]
                stack.append(next_nfas)
        dfa.accept_states = {dfas for nfas, dfas in nfas2dfas.items() if nfa.accept_state in nfas}
        return dfa

    def enum_states(self):
        states = set()
        stack = [self.init_state]
        while stack:
            state = stack.pop(-1)
            if state in states:
                continue
            states.add(state)
            for next_state in state.transitions.values():
                stack.append(next_state)
        return states
