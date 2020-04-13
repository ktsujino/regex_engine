import time
import regex
import re

REPEAT=1000

def profile(pattern, string):
    print(f'pattern: {pattern}')
    print(f'string: {string}')
    print(f'repeat: {REPEAT}')
    re_matcher = re.compile(pattern)
    my_matcher = regex.compile_regex(pattern)
    print('DFA generated by my regex:')
    print(f'#states: {len(my_matcher.enum_states())}')
    print(f'dump:\n{my_matcher}')

    before = time.time()
    for _ in range(REPEAT):
        re_matcher.match(string)
    after = time.time()
    elapsed = after - before
    print(f'standard library re took {elapsed} sec')
    before = time.time()
    for _ in range(REPEAT):
        my_matcher.match(string)
    after = time.time()
    elapsed = after - before
    print(f'my regex took {elapsed} sec')

if __name__ == '__main__':
    profile('a+' * 20, 'a'*20)
