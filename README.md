Python3 based self-educational implementation of regex engine.

Only very basic subset of regex is supported in a suboptimal way:
- ascii only
- char range operator: [] and .
- quantification: {}, * and +
- union: |
- grouping (without capture): ()
- escape: \\

.

Try
```
$ echo foo | python3 regex.py 'fo+'
```
.

lex.py first does lexical parsing of input pattern.
Brackets [] and {} have non-recursive nature, so they are processed as part of this lex step to simplify syntactic parsing, although formally they should belong to syntacitic parsing.

Next, syntax.py converts the list of lexically analyzed tokens into a syntax tree.
Formally this should be done by proper LL() or LR() or LALR() or whatever parser, but I didn't have
enough energy to implement these nice and generic parsers from scratch, so I chose ad-hoc approach to:
- first detect () and process them first in a recursive way
- split the list of tokens by |
- process quantification and concatenation operatotions in | split terms
- merge them all to single tree
.
This skims through the imput sequence multiple times, and therefore is much slower than proper one-pass linear-time parser, but works fine for short regex patterns.

Finally, automata.py converts the generated syntax tree (AST) into automata.
First the AST is converted into Non-deterministic Finite Automanton (NFA) with Thompson's construction [1].
Then the NFA is converted into a Deterministic Finite Automaton (DFA) with subset consruction [2].

User-proveded regex pattern is compiled into this DFA and is used to match against input strings.
This top level behavior is encapsulated in regex.py .

See test_*.py for how to run these.

[1] https://en.wikipedia.org/wiki/Thompson%27s_construction

[2] https://en.wikipedia.org/wiki/Powerset_construction