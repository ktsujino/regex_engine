# Strictly speaking, interpratation of [] and {} should be done as
# part of syntactic parsing, but they are not recursive and also
# short in general, so made them part of lexical analysis here to
# simplify our syntax rules.

class Token:
    def __init__(self, val):
        self.val = val

class CharToken(Token):
    pass

class QuantificationToken(Token):
    pass

class OpenParToken(Token):
    pass

class CloseParToken(Token):
    pass

class UnionToken(Token):
    pass

def find(s, c, start_pos):
    escape = False
    for pos in range(start_pos, len(s)):
        if escape:
            escape = False
        elif s[pos] == '\\':
            escape = True
        elif s[pos] == c:
            return pos
    return None
        
def lexical_analysis(s):
    tokens = []
    pos = 0
    escape = False
    while pos < len(s):
        if escape:
            tokens.append(CharToken(s[pos]))
            pos += 1
        elif s[pos] == '\\':
            escape = True
            pos += 1
        elif s[pos] == '{':
            end_pos = find(s, '}', pos)
            if end_pos is None:
                tokens.append(CharToken(s[pos]))
                pos += 1
            else:
                tokens.append(QuantificationToken(s[pos:(end_pos+1)]))
                pos = end_pos + 1
        elif s[pos] == '+' or s[pos] == '*' or s[pos] == '?':
            tokens.append(QuantificationToken(s[pos]))
            pos += 1
        elif s[pos] == '|':
            tokens.append(UnionToken(s[pos]))
            pos += 1
        elif s[pos] == '(':
            tokens.append(OpenParToken(s[pos]))
            pos += 1
        elif s[pos] == ')':
            tokens.append(CloseParToken(s[pos]))
            pos += 1
        elif s[pos] == '[':
            end_pos = find(s, ']', pos)
            if end_pos is None:
                raise Exception('unmatched []')
            else:
                tokens.append(CharToken(s[pos:(end_pos+1)]))
                pos = end_pos + 1
        else:
            tokens.append(CharToken(s[pos]))
            pos += 1

    return tokens
