#!/usr/bin/env python3
# Writes the three refusal tests that came with D240 to D244 (T571), from
# a table written by hand, as docs/briefs/step19-review/review-refusals.py
# writes the review's: the program, the text the message points at (its
# column is counted here, from the program's own text), and the message.
# Nothing here asks the compiler. What perl does with each is in its
# comment, from perl 5.42 run plain (`--perl` prints each again).
#
#     python3 docs/briefs/step19-limit/refusals.py 5512
import os
import subprocess
import sys
T = []
def r(name, why, body, at, message, nth=1):
    T.append((name, why, body, at, message, nth))

S = 'my $s = "aaa";\n'
r('blank-before-lazy', "perl reads a+ ? as a+?, and prints a (T571).", S + 'my @l = $s =~ /(a+ ?)/x;\nsay "@l";', '?)',
  'a blank before the ? of a lazy quantifier under /x: perl reads them together, a+ ? as a+?; write them together')
r('blank-before-possessive', "perl reads a{1,2} + as a{1,2}+, a possessive quantifier, and prints aa (T571).", S + 'my @l = $s =~ /(a{1,2} +)/x;\nsay "@l";', '+)',
  'a blank before a + after a quantifier under /x: perl reads them together, a possessive quantifier, which is not in the language yet (D226)')
r('blank-after-m', "perl takes the blank, and prints 1 (T571).", S + 'say $s =~ m /a/ ? 1 : 0;', 'm /',
  'a blank between m and its pattern: perl takes it; write the delimiter hard against the m, m{...}, or /.../ (D227)')
r('line-after-m', "perl takes the end of the line, and prints 1 (T571).", S + 'say $s =~ m\n  {a} ? 1 : 0;', 'm\n',
  'a blank between m and its pattern: perl takes it; write the delimiter hard against the m, m{...}, or /.../ (D227)')


def write(first):
    n = first
    for name, why, body, at, message, nth in T:
        program = f'# kind: refused\n# {why}\nuse v5.42;\n{body}\n'
        path = f't/{n}-re-{name}'
        open(path + '.pl', 'w', encoding='utf-8').write(program)
        k = program.index('use v5.42;')
        for _ in range(nth):
            k = program.index(at, k + 1)
        line = program.count('\n', 0, k) + 1
        col = len(program[program.rfind('\n', 0, k) + 1:k]) + 1
        open(path + '.expected', 'w', encoding='utf-8').write(f'{path}.pl:{line}:{col}: {message}\nexit: 1\n')
        n += 1
    return n


if __name__ == '__main__':
    if sys.argv[1] == '--perl':
        for name, why, body, at, message, nth in T:
            r_ = subprocess.run([os.environ.get('CURLY_PERL', 'perl'), '-e', 'use v5.42;\n' + body], capture_output=True, text=True, timeout=10)
            print(f'{name}: exit {r_.returncode}; {r_.stdout!r}; {r_.stderr.strip()[:200]!r}')
    else:
        print(write(int(sys.argv[1])) - 1)
