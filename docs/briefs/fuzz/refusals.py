#!/usr/bin/env python3
# Writes the refusal tests of what the fuzzer found (D246, T602) from a
# table written by hand: the program, the text the message points at (its
# column is counted here, from the program's own text), and the message.
# Nothing here asks the compiler. What perl does with each is in its
# comment, from perl 5.42 run plain (`python3 docs/briefs/fuzz/refusals.py
# --perl` prints each again).
#
#     python3 docs/briefs/fuzz/refusals.py 5720
import os
import subprocess
import sys
T = []
def r(name, why, body, at, message, nth=1):
    T.append((name, why, body, at, message, nth))

HOP = "this {kind} can change {what}, which holds the container it is {a} of: perl takes the container first, and reads or stores a freed one when the {kind} lets go of it (D246); take the {kind} into a my first"
KEY = lambda what: HOP.format(kind='key', what=what, a='a key')
INDEX = lambda what: HOP.format(kind='index', what=what, a='an index')

r('store-key-frees-head', "perl dies: Modification of a read-only value attempted (T602).",
  'my $v;\nsub f() {\n    $v = undef;\n    return "k";\n}\n$v->{f()} = 5;\nsay defined($v) ? "def" : "undef";', 'f()} =', KEY('$v'))
r('read-index-frees-head', "perl prints an empty line, and warns: Use of uninitialized value in say.",
  'my $v = [1, 2];\nsub f() {\n    $v = [7, 8];\n    return 0;\n}\nsay $v->[f()];', 'f()]', INDEX('$v'))
r('index-assigns-head', "perl prints an empty line, and warns: Use of uninitialized value in say.",
  'my $v = [1, 2];\nsay $v->[($v = [7, 8]) ? 0 : 1];', '? 0', INDEX('$v'))
r('element-base', "perl prints an empty line, and warns: Use of uninitialized value in say.",
  'my @a = ([1]);\nsub f() {\n    @a = ([5]);\n    return 0;\n}\nsay $a[0][f()];', 'f()]', INDEX('@a'))
r('hash-element-base', "perl prints 'u': the freed hash has no key k.",
  'my %h = (a => {k => 1});\nsub f() {\n    %h = (a => {k => 2});\n    return "k";\n}\nsay $h{a}{f()} // "u";', 'f()}', KEY('%h'))
r('second-hop', "perl prints an empty line, and warns: Use of uninitialized value in say.",
  'my $r = [[1]];\nsub f() {\n    $r->[0] = [5];\n    return 0;\n}\nsay $r->[0][f()];', 'f()]', INDEX('what references reach'))
r('exists', "perl dies: Not a HASH reference, of the freed hash.",
  'my $h = {k => 1};\nsub f() {\n    $h = {k => 2};\n    return "k";\n}\nsay exists($h->{f()}) ? 1 : 0;', 'f()}', KEY('$h'))
r('delete', "perl dies: Not a HASH reference, of the freed hash.",
  'my $h = {k => 1};\nsub f() {\n    $h = {k => 2};\n    return "k";\n}\ndelete $h->{f()};\nsay scalar(%{$h});', 'f()}', KEY('$h'))
r('step', "perl dies: Modification of a read-only value attempted.",
  'my $v = {k => 1};\nsub f() {\n    $v = {k => 5};\n    return "k";\n}\n$v->{f()}++;\nsay $v->{k};', 'f()}', KEY('$v'))
r('through-a-reference-call', "perl prints an empty line, and warns: Use of uninitialized value in say.",
  'my $v = [1];\nmy $g = sub { $v = [2]; return 0 };\nsay $v->[$g->()];', '$g->()', INDEX('$v'))
r('list-assignment-target', "perl prints 2: the 5 goes to the freed array.",
  'my $v = [1];\nsub f() {\n    $v = [2];\n    return 0;\n}\nmy $z;\n($v->[f()], $z) = (5, 6);\nsay $v->[0];', 'f()]', INDEX('$v'))
r('assigning-operator', "perl dies: Modification of a read-only value attempted.",
  'my $v = [1];\nsub f() {\n    $v = [2];\n    return 0;\n}\n$v->[f()] .= "x";\nsay $v->[0];', 'f()]', INDEX('$v'))

def write(first, table=None):
    n = first
    for name, why, body, at, message, nth in (T if table is None else table):
        program = f'# kind: refused\n# {why}\nuse v5.42;\n{body}\n'
        path = f't/{n}-fuzz-{name}'
        open(path + '.pl', 'w', encoding='utf-8').write(program)
        k = program.index('use v5.42;')
        for _ in range(nth):
            k = program.index(at, k + 1)
        line = program.count('\n', 0, k) + 1
        col = len(program[program.rfind('\n', 0, k) + 1:k]) + 1
        open(path + '.expected', 'w', encoding='utf-8').write(f'{path}.pl:{line}:{col}: {message}\nexit: 1\n')
        n += 1

if __name__ == '__main__':
    if sys.argv[1] == '--perl':
        for name, why, body, at, message, nth in T:
            r_ = subprocess.run([os.environ.get('CURLY_PERL', 'perl'), '-e', 'use v5.42;\n' + body], capture_output=True, text=True, timeout=10)
            print(f'{name}: exit {r_.returncode}; {r_.stdout!r}; {r_.stderr.strip()[:120]!r}')
    else:
        write(int(sys.argv[1]))
