Python3 based self-educational implementation of regex engine.

Only very basic subset of regex is supported in a suboptimal way:
- ascii only
- char range operator: [], .
- quantification: {}, *, +
- union |
- escape \
.

Firstly, lex.py first does lexical parsing of input pattern.
Brackets [] and {} have non-recursive nature, so they are processed as part of this lex step.

Next, syntax.py converts lists of lexically analyzed tokens into syntax tree.
Formally this should be done by proper LL or LR or LALR or whatever parser, but I didn't have
enough energy to implement these nice and generic parsers from scratch, so I chose ad-hoc approach to:
- first detect () and process them first in a recursive way
- split the list of tokens by |
- process quantification and concatenation operatotions in | split terms
- merge them all to single tree
.
This is slower than proper one-pass linear-time parser but works fine for short regex patterns.

Finally, automata.py converts syntax tree (AST) into automata.
First AST is converted into Non-deterministic Finite Automanton (NFA) with Thompson's construction [1].
Then NFA is converted into Deterministic Finite Automaton (DFA) with subset consruction [2].

User-proveded regex pattern is compiled into this DFA and is used to match against input strings.
This top level behavior is encapsulated in regex.py .

See test_*.py for how to run these.

[1] https://en.wikipedia.org/wiki/Thompson%27s_construction

[2] https://en.wikipedia.org/wiki/Powerset_construction