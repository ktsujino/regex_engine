# syntax rules:
#
# Z -> EXPRESSION Eof
# EXPRESSION -> TERM
# EXPRESSION -> PAR_EXPRESSION
# EXPRESSION -> EXPRESSION Union EXPRESSION
# PAR_EXPRESSION -> OpenPar EXPRESSION ClosePar
# FACTOR -> Char
# FACTOR -> Char Quantification
# FACTOR -> PAR_EXPRESSION Quantification
# TERM -> FACTOR
# TERM -> TERM FACTOR
#
# Writing proper parser is beyond my patience,
# so writing less generic pseudo-parser thing here.
# If you are serious, just use yacc or something.

import lex

class UnionPlaceholder:
    pass

class ASTNode:
    pass

class EpsilonNode(ASTNode):
    def __str__(self):
        return 'Epsilon()'

class CharNode(ASTNode):
    def __init__(self, char_set):
        self.char_set = char_set
    def __str__(self):
        return 'Char(%s)' % (self.char_set)

class ConcatenationNode(ASTNode):
    def __init__(self, children):
        self.children = children
    def __str__(self):
        return 'Concat(%s)' % (', '.join([str(child) for child in self.children]))

class UnionNode(ASTNode):
    def __init__(self, children):
        self.children = children
    def __str__(self):
        return 'Union(%s)' % (', '.join([str(child) for child in self.children]))

class QuantificationNode(ASTNode):
    def __init__(self, lb, ub, operand):
        self.lb = lb
        self.ub = ub
        self.operand = operand
    def __str__(self):
        return 'Quantification(%s, %s, %s)' % (self.lb, self.ub, str(self.operand))

def decode_char_token(s):
    if s[0] == '[':
        char_set = parse_square_bracket(s[1:])
    elif s[0] == '\\':
        char_set = {s[1]}
    elif s[0] == '.':
        char_set = {chr(x) for x in range(128)}
    else:
        char_set = {s[0]}
    return CharNode(char_set)

def parse_square_bracket(s):
    escaped = False
    char_set = set()
    pos = 0
    while True:
        if pos >= len(s):
            raise Exception('found unmatched square brackets')
        elif escaped:
            char_set.add(s[pos])
            escaped = False
            pos += 1
        elif s[pos] == '\\':
            escape = True
            pos += 1
        elif s[pos] == ']':
            return char_set
        elif pos + 2 < len(s) and s[pos+1] == '-':
            # range notation like 0-9
            lb = ord(s[pos])
            ub = ord(s[pos+2])
            if lb > ub:
                raise Exception('invalid range notation (a-b) in square brackets')
            for c in range(lb, ub+1):
                char_set.add(chr(c))
            pos += 3
        else:
            # normal chars, including [ and trailing -
            char_set.add(s[pos])
            pos += 1

def decode_quantification_token(s):
    if s[0] == '{':
        lb, ub = parse_curly_bracket(s[1:])
    elif s[0] == '*':
        lb, ub = 0, float('inf')
    elif s[0] == '+':
        lb, ub = 1, float('inf')
    elif s[0] == '?':
        lb, ub = 0, 1
    else:
        raise Exception('found invalid quantification operator')
    return lb, ub

def parse_curly_bracket(s):
    sections = s[:-1].split(',')
    try:
        sections_int = [int(section) for section in sections]
    except ValueError:
        raise Exception('found invalid expression in curly brackets')
    if len(sections) == 1:
        lb = sections_int[0]
        ub = lb
    elif len(sections) == 2:
        lb = sections_int[0]
        ub = sections_int[1]
    else:
        raise Exception('found invalid expression in curly brackets')
    return lb, ub

def syntactic_analysis(tokens):
    if not tokens:
        return EpsilonNode()
    node_list = analyze_expression(tokens)
    groups = [[]]
    for node in node_list:
        if type(node) == UnionPlaceholder:
            groups.append(list())
        else:
            groups[-1].append(node)
    if len(groups) == 1:
        return group_node(groups[-1])
    else:
        children = [group_node(group) for group in groups]
        return UnionNode(children)

def group_node(group):
    group = resolve_quantification(group)
    if len(group) == 1:
        return group[0]
    else:
        return ConcatenationNode(group)

def analyze_expression(tokens):
    if not tokens:
        return []
    node_list = []
    # detect parenthesis
    start_pos = len(tokens)
    end_pos = len(tokens)
    level = 0

    for pos in range(len(tokens)):
        if type(tokens[pos]) == lex.OpenParToken:
            if level == 0:
                start_pos = pos
            level += 1
        elif type(tokens[pos]) == lex.CloseParToken:
            level -= 1
            if level == 0:
                end_pos = pos
                break

    if start_pos > 0:
        node_list += analyze_term(tokens[:start_pos])
    if start_pos < end_pos:
        node_list.append(syntactic_analysis(tokens[(start_pos+1):end_pos]))
    if end_pos+1 < len(tokens):
        node_list += analyze_expression(tokens[(end_pos+1):])

    return node_list
                     
def analyze_term(tokens):
    node_list = []
    pos = 0
    while pos < len(tokens):
        if type(tokens[pos]) == lex.CharToken:
            char_node = decode_char_token(tokens[pos].val)
            node_list.append(char_node)
        elif type(tokens[pos]) == lex.QuantificationToken:
            lb, ub = decode_quantification_token(tokens[pos].val)
            if len(node_list) > 0 and type(node_list[-1]) == QuantificationNode:
                raise Exception('found contiguous quantification operators')
            node_list.append(QuantificationNode(lb, ub, None))
        elif type(tokens[pos]) == lex.UnionToken:
            node_list.append(UnionPlaceholder())
        pos += 1
    return node_list

def resolve_quantification(nodes):
    out = []
    for node in nodes:
        if type(node) == QuantificationNode:
            if len(out) == 0:
                raise Exception('found invalid quantification operator')
            node.operand = out.pop(-1)
        out.append(node)
    return out
