#!/usr/bin/env python3
# Writes step 13d's refusal tests from a table written by hand: the program,
# the text the message points at (its column is counted here, from the
# program's own text), and the message. Nothing here asks the compiler.
# What perl does with each is in its comment, from perl 5.42 run plain
# (`python3 docs/briefs/step13d-refusals.py --perl` prints each again).
#
#     python3 docs/briefs/step13d-refusals.py 2500
import subprocess
import sys
T = []
def r(name, why, body, at, message, nth=1):
    T.append((name, why, body, at, message, nth))

r('dollar-dollar-element', "perl runs it: '1\\n'.", 'my $r = [1];\nsay "$$r[0]";', '$$r', '$$ in a string: a dereference without braces is cut (D108); write ${ $r } or $r->$*, and $r->[0] for an element')
r('at-dollar', "perl runs it: '1\\n'.", 'my $r = [1];\nsay "@$r";', '@$r', '@$ in a string: a dereference without braces is cut (D108); write @{ $r } or $r->@*')
r('last-dollar', "perl runs it: '0\\n'.", 'my $r = [1];\nsay "$#$r";', '$#$', '$#$ in a string: a dereference without braces is cut (D108); write $#{ $r } or $r->$#*')
r('code-scalar-blank', "perl runs it: '1\\n'.", 'my $x = 1;\nsay "${ \\$x }";', '${ ', '${\\ in a string puts code in it, which is cut (D111): work the value out before the string, into a my, and put that in it')
r('code-array-blank', "perl runs it: '1 2\\n'.", 'say "@{ [1, 2] }";', '@{ ', '@{[ in a string puts code in it, which is cut (D111): work the value out before the string, into a my, and put that in it')
r('code-last', "perl runs it: '1\\n'.", 'say "$#{[1, 2]}";', '$#{', '$#{[ in a string puts code in it, which is cut (D111): work the value out before the string, into a my, and put that in it')
r('index-after-braces', "perl runs it: '1\\n'.", 'my $r = [1];\nsay "@{$r}[0]";', '[0]', "'[' hard after @{$r} in a string: a subscript after the whole array through a reference is refused (D114; perl reads on after braces, and after a postfix form it is text); write @{$r}\\[")
r('key-after-braces', 'perl dies: Not a HASH reference', 'my $r = [1];\nsay "@{$r}{a}";', '{a}', "'{' hard after @{$r} in a string: a subscript after the whole array through a reference is refused (D114; perl reads on after braces, and after a postfix form it is text); write @{$r}\\{")
r('index-after-scalar-braces', 'perl dies: Not an ARRAY reference', 'my $a = [1];\nmy $s = \\$a;\nsay "${$s}[0]";', '[0]', "'[' hard after ${$s} in a string: a subscript after the scalar through a reference is refused (D114; perl reads on after braces, and after a postfix form it is text); write ${$s}\\[")
r('key-after-scalar-braces', 'perl dies: Not a HASH reference', 'my $h = {a => 1};\nmy $s = \\$h;\nsay "${$s}{a}";', '{a}', "'{' hard after ${$s} in a string: a subscript after the scalar through a reference is refused (D114; perl reads on after braces, and after a postfix form it is text); write ${$s}\\{")
r('arrow-after-braces', "perl runs it: '1\\n'.", 'my $a = [1];\nmy $s = \\$a;\nsay "${$s}->[0]";', '->[', "'->[' hard after ${$s} in a string: a subscript after the scalar through a reference is refused (D114; perl reads on after braces, and after a postfix form it is text); write ${$s}\\->[")
r('arrow-after-array-braces', "perl dies: Can't use an array as a reference", 'my $r = [1];\nsay "@{$r}->[0]";', '->[', "'->[' hard after @{$r} in a string: a subscript after the whole array through a reference is refused (D114; perl reads on after braces, and after a postfix form it is text); write @{$r}\\->[")
r('index-after-last-braces', 'perl does not compile it: syntax error at -e line 3, near "}["', 'my $r = [1];\nsay "$#{$r}[0]";', '[0]', "'[' hard after $#{$r} in a string: a subscript after a last index through a reference is refused (D114; perl reads on after braces, and after a postfix form it is text); write $#{$r}\\[")
r('index-after-postfix-whole', "perl runs it: '1[0]\\n'.", 'my $r = [1];\nsay "$r->@*[0]";', '[0]', "'[' hard after $r->@* in a string: a subscript after the whole array through a reference is refused (D114; perl reads on after braces, and after a postfix form it is text); write $r->@*\\[")
r('arrow-after-postfix-whole', "perl runs it: 'ARRAY(0x...)->[0]\\n'.", 'my $r = [[1]];\nsay "$r->@*->[0]";', '->[', "'->[' hard after $r->@* in a string: a subscript after the whole array through a reference is refused (D114; perl reads on after braces, and after a postfix form it is text); write $r->@*\\->[")
r('index-after-postfix-last', "perl runs it: '0[0]\\n'.", 'my $r = [1];\nsay "$r->$#*[0]";', '[0]', "'[' hard after $r->$#* in a string: a subscript after a last index through a reference is refused (D114; perl reads on after braces, and after a postfix form it is text); write $r->$#*\\[")
r('index-after-postfix-scalar', "perl runs it: 'ARRAY(0x...)[0]\\n'.", 'my $a = [1];\nmy $s = \\$a;\nsay "$s->$*[0]";', '[0]', "'[' hard after $s->$* in a string: a subscript after the scalar through a reference is refused (D114; perl reads on after braces, and after a postfix form it is text); write $s->$*\\[")
r('arrow-after-postfix-scalar', "perl runs it: 'ARRAY(0x...)->[0]\\n'.", 'my $a = [1];\nmy $s = \\$a;\nsay "$s->$*->[0]";', '->[', "'->[' hard after $s->$* in a string: a subscript after the scalar through a reference is refused (D114; perl reads on after braces, and after a postfix form it is text); write $s->$*\\->[")
r('key-after-postfix-scalar', "perl runs it: 'HASH(0x...){a}\\n'.", 'my $h = {a => 1};\nmy $s = \\$h;\nsay "$s->$*{a}";', '{a}', "'{' hard after $s->$* in a string: a subscript after the scalar through a reference is refused (D114; perl reads on after braces, and after a postfix form it is text); write $s->$*\\{")
r('index-after-slice', 'perl does not compile it: syntax error at -e line 3, near "]["', 'my $r = [[1]];\nsay "$r->@[0][0]";', '[0]', "'[' hard after $r->@[0] in a string: a subscript after a slice is refused (D114; perl reads on after braces, and after a postfix form it is text); write $r->@[0]\\[", 2)
r('arrow-after-slice', "perl runs it: '1\\n'.", 'my $r = [[1]];\nsay "$r->@[0]->[0]";', '->[', "'->[' hard after $r->@[0] in a string: a subscript after a slice is refused (D114; perl reads on after braces, and after a postfix form it is text); write $r->@[0]\\->[")
r('key-after-slice', 'perl does not compile it: syntax error at -e line 3, near "]{a"', 'my $r = [{a => 1}];\nsay "$r->@[0]{a}";', '{a}', "'{' hard after $r->@[0] in a string: a subscript after a slice is refused (D114; perl reads on after braces, and after a postfix form it is text); write $r->@[0]\\{")
r('hash-slice', "perl runs it: '1\\n'.", 'my $q = {k => 1};\nsay "$q->@{k}";', '->@', "'->@{' hard after $q in a string: a slice of a hash through a reference, which is not in a string (D99, D111): join it first; or write $q\\->@{")
r('arrow-array-name', "perl runs it: '1->2\\n'.", 'my $r = [1];\nmy @x = (2);\nsay "$r->[0]->@x";', '->@', "'->@' hard after $r->[0] in a string: perl reads on, into a dereference or a variable after the arrow, and the language takes ->@*, ->$#*, ->$* and ->@[...] there (D111); write $r->[0]\\->@")
r('arrow-scalar-name', "perl runs it: 'ARRAY(0x...)->2\\n'.", 'my $r = [1];\nmy $x = 2;\nsay "$r->$x";', '->$', "'->$' hard after $r in a string: perl reads on, into a dereference or a variable after the arrow, and the language takes ->@*, ->$#*, ->$* and ->@[...] there (D111); write $r\\->$")
r('arrow-at-alone', "perl runs it: 'ARRAY(0x...)->@ \\n'.", 'my $r = [1];\nsay "$r->@ ";', '->@', "'->@' hard after $r in a string: perl reads on, into a dereference or a variable after the arrow, and the language takes ->@*, ->$#*, ->$* and ->@[...] there (D111); write $r\\->@")
r('arrow-dollar-hash', 'perl does not compile it: Global symbol "@x" requires explicit package name (did you forget to declare "my @x"?)', 'my $r = [1];\nsay "$r->$#x";', '->$', "'->$' hard after $r in a string: perl reads on, into a dereference or a variable after the arrow, and the language takes ->@*, ->$#*, ->$* and ->@[...] there (D111); write $r\\->$")
r('index-sum', "perl runs it: '2\\n'.", 'my $r = [1, 2];\nmy $i = 0;\nsay "$r->[$i+1]";', '+1]', 'in a string an index is a whole number or a scalar variable (D91): take the index into a my first')
r('index-octal', "perl runs it: '2\\n'.", 'my $r = [1, 2];\nsay "$r->[01]";', '01]', '01 in an index in a string: a leading zero makes it octal, to perl; write the number without it')
r('index-word', 'perl does not compile it: Bareword "x" not allowed while "strict subs" in use', 'my $r = [1, 2];\nsay "$r->[x]";', 'x]"', 'in a string an index is a whole number or a scalar variable (D91): take the index into a my first')
r('index-last-index', "perl runs it: '1\\n'.", 'my $r = [1, 2];\nmy @a = (1);\nsay "$r->[$#a]";', '$#a', 'in a string an index is a whole number or a scalar variable (D91): take the index into a my first')
r('index-not-closed', 'perl does not compile it: Missing right curly or square bracket at -e line 3, within string', 'my $r = [1, 2];\nsay "$r->[0";', '[0"', 'an index in a string that does not close: write \\[ for the character')
r('key-blank', "perl runs it: '1\\n'.", 'my $q = {k => 1};\nsay "$q->{ k }";', ' k ', 'in a string a key is a word or a scalar variable, hard against its braces (D99): take the key into a my first')
r('key-quoted', "perl runs it: '1\\n'.", 'my $q = {k => 1};\nsay "$q->{\'k\'}";', "'k'", 'in a string a key is a word or a scalar variable, hard against its braces (D99): take the key into a my first')
r('key-minus', "perl runs it: '1\\n'.", 'my $q = {-k => 1};\nsay "$q->{-k}";', '-k}', 'in a string a key is a word or a scalar variable, hard against its braces (D99): take the key into a my first')
r('key-number', "perl runs it: '1\\n'.", 'my $q = {1 => 1};\nsay "$q->{1}";', '1}"', 'in a string a key is a word or a scalar variable, hard against its braces (D99): take the key into a my first')
r('key-second-blank', "perl runs it: '1\\n'.", 'my $q = {k => {k => 1}};\nsay "$q->{k}{ k }";', ' k ', 'in a string a key is a word or a scalar variable, hard against its braces (D99): take the key into a my first')
r('key-word-and-more', "perl does not compile it: Bareword found where operator expected.", 'my $q = {k => 1};\nsay "$q->{k j}";', ' j}', 'in a string a key is a word or a scalar variable, hard against its braces (D99): take the key into a my first')
r('key-variable-and-a-blank', "perl runs it: '1\\n'.", 'my $q = {k => {k => 1}};\nmy $k = "k";\nsay "$q->{k}{$k }";', ' }', 'in a string a key is a word or a scalar variable, hard against its braces (D99): take the key into a my first')
r('braces-blank-before-arrow', "perl runs it: '1\\n'.", 'my $r = [[1]];\nsay "@{$r ->[0]}";', '->[', 'in a string what stands in @{ ... } is a scalar variable, with subscripts or without (D111): take the reference into a my first')
r('braces-blank-before-index', "perl runs it: '2\\n'.", 'my $r = [[1]];\nmy @r = ([2]);\nsay "@{$r [0]}";', '[0]', 'in a string what stands in @{ ... } is a scalar variable, with subscripts or without (D111): take the reference into a my first')
r('braces-blank-inside-chain', "perl runs it: '1\\n'.", 'my $r = [[[1]]];\nsay "@{$r->[0] ->[0]}";', '->[', 'in a string what stands in @{ ... } is a scalar variable, with subscripts or without (D111): take the reference into a my first', 2)
r('braces-two', 'perl runs it, and warns: Useless use of private variable in void context', 'my $r = [1];\nmy $q = [2];\nsay "@{$r, $q}";', ', $', 'in a string what stands in @{ ... } is a scalar variable, with subscripts or without (D111): take the reference into a my first')
r('braces-postfix', 'perl dies: Can\'t use string ("1") as an ARRAY ref while "strict refs" in use', 'my $r = [1];\nsay "@{$r->@*}";', '$r-', 'in a string what stands in @{ ... } is a scalar variable, with subscripts or without (D111): a postfix form there is refused; take the reference into a my first')
r('braces-call', "perl runs it: '1\\n'.", 'sub f() {\n    return [1];\n}\nsay "@{f()}";', '@{f', 'in a string what stands in @{ ... } is a scalar variable, with subscripts or without (D111), or a name hard against both braces, @{name}')
r('braces-new-line', "perl runs it: '1\\n'.", 'my $r = [1];\nsay "@{\n$r}";', '@{\n', 'in a string what stands in @{ ... } is a scalar variable, with subscripts or without (D111), or a name hard against both braces, @{name}')
r('braces-not-closed', 'perl does not compile it: Missing right curly or square bracket at -e line 3, within string', 'my $r = [1];\nsay "@{$r";', '@{$', '@{ ... } in a string that does not close')
r('braces-word-blank', "perl runs it: '1\\n'.", 'my @name = (1);\nsay "@{ name }";', '@{ ', 'in a string a name in braces is hard against both of them: @{name}')
r('braces-dollar-dollar', "perl runs it: '1\\n'.", 'my $r = [1];\nmy $t = \\$r;\nsay "@{$$t}";', '$$t', 'in a string what stands in braces after a sigil is a scalar variable, with subscripts or without (D111): take the reference into a my first')
r('qq-angle-arrow', 'perl does not compile it: syntax error at -e line 3, near "qq<$q->{k"', 'my $q = {k => 1};\nsay qq<$q->{k}>;', '>;\n', 'what stands in this string runs past its end: perl ends the string first, and does not compile the rest')
r('undeclared-head', 'perl does not compile it: Global symbol "$r" requires explicit package name (did you forget to declare "my $r"?)', 'my @r = (1);\nsay "$r->[0]";', '$r-', '$r is not declared: my $r; in a string, \\$ is the character, and ${name} ends a name sooner')
r('underscore-element', 'perl runs it, and warns: Use of uninitialized value $_[0] in string', 'for (1) {\n    say "$_[0]";\n}', '$_[', "$_[ is an element of perl's own @_ or %_, which are not in the language")
r('t230-through', "perl runs it, and says nothing: $a[0] is a0, the pieces joined after the index has stored (T230, T238).", 'my $r = [3];\nmy @a;\n$a[$r->[0] = 0] = "a$r->[0]";', '= 0', 'the index changes $r, which the concatenation on the right reads: perl joins its pieces as it stores, after the index is worked out; take the string into a my first')
r('t198-through', "perl runs it, and says nothing: $u is never assigned (T198).", 'my $r = [3];\nmy $u;\nmy $t = "t";\n$t .= ($u = "a$r->[0]");', '= "', "'.=' of an assignment of an interpolated string: perl makes one operation of them and never assigns $u; make the assignment a statement of its own", 2)
r('past-ascii-after-head', 'perl runs it, and warns: Wide character in say', 'use utf8;\nmy $r = [1];\nsay "$r→[0]";', '→[0', 'a character past ASCII (U+2192) hard after $r in a string: perl takes a letter, a digit or a mark there into the name; write ${r}')
r('braces-empty', 'perl does not compile it: syntax error at -e line 2, near "${}"', 'say "${}";', '${}', 'in a string what stands in ${ ... } is a scalar variable, with subscripts or without (D111), or a name hard against both braces, ${name}')

def write(first, table=None):
    n = first
    for name, why, body, at, message, nth in (T if table is None else table):
        program = f'# kind: refused\n# {why}\nuse v5.42;\n{body}\n'
        path = f't/{n}-qref-{name}'
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
        import os
        for name, why, body, at, message, nth in T:
            r_ = subprocess.run([os.environ.get('CURLY_PERL', 'perl'), '-e', 'use v5.42;\n' + body], capture_output=True, text=True, timeout=10)
            print(f'{name}: exit {r_.returncode}; {r_.stdout!r}; {r_.stderr.strip()[:200]!r}')
    else:
        write(int(sys.argv[1]))
