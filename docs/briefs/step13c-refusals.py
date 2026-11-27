#!/usr/bin/env python3
# Writes step 13c's refusal tests from a table written by hand: the program,
# the text the message points at (its column is counted here, from the
# program's own text), and the message. Nothing here asks the compiler.
# What perl does with each is in its comment, from perl 5.42 run plain
# (`python3 docs/briefs/step13c-refusals.py --perl` prints each again).
#
#     python3 docs/briefs/step13c-refusals.py 2300
import subprocess
import sys
T = []
def r(name, why, body, at, message, nth=1):
    T.append((name, why, body, at, message, nth))

X = 'my $x = 1;\nmy $r = \\$x;\n'
LATER = "a later part of {} can change {}, which an earlier part names: perl reads it after the change; take the value into a my first"
AFTER_BRACES = 'a subscript after the braces of a dereference is cut (D108): write $r->[...], $r->{...}, or the slice $r->@[...], $r->@{...}'
DOLLARS = '$$ before a name is cut (D108): an element through a reference is written $r->[...] or $r->{...}, and the scalar $r->$* or ${ $r }'
ARROW_POSTFIX = "an arrow after ->$*: going on through a reference that a scalar through a reference holds is not in the language; take the scalar into a my first, my $s = $r->$*; $s->[0]"
ARROW_BRACES = "an arrow after ${ ... }: going on through a reference that a scalar through a reference holds is not in the language; take the scalar into a my first, my $s = ${ $r }; $s->[0]"
LOOP = "this can change {}, which the list of {} it is in names: perl's {} walks the variable itself; take the value into a my before {}"
TAKES = "\\ takes a named array, a named hash or a scalar variable, \\@a, \\%h or \\$x (D110)"

# ---- cut by D108: no braces, and what may follow the scalar through a reference
r('two-dollars', "perl runs it: '1\\n'.", X + 'say $$r;', '$$', DOLLARS)
r('two-dollars-stored', "perl runs it, and says nothing.", X + '$$r = 5;', '$$', DOLLARS)
r('three-dollars', "perl runs it: '1\\n'.", X + 'my $q = \\$r;\nsay $$$q;', '$$', DOLLARS)
r('key-after-braces', "perl runs it: '1\\n' (${$h}{a} is an element of %$h).", 'my $h = {a => 1};\nsay ${ $h }{a};', '}{', AFTER_BRACES)
r('arrow-after-braces', "perl runs it: '1\\n'.", 'my $a = [1];\nmy $r = \\$a;\nsay ${ $r }->[0];', '}->', ARROW_BRACES)
r('arrow-after-braces-and-a-blank', "perl runs it: '1\\n'.", 'my $a = [1];\nmy $r = \\$a;\nsay ${ $r } ->[0];', '} ->', ARROW_BRACES)
r('subscript-after-postfix', "perl does not compile it: syntax error near '$*['.", 'my $a = [1];\nmy $r = \\$a;\nsay $r->$*[0];', '->', "a subscript after ->$*: perl does not compile it, or dies; take the element through the reference itself, $r->[...]")
r('key-after-postfix', "perl does not compile it: syntax error near '$*{'.", 'my $h = {a => 1};\nmy $r = \\$h;\nsay $r->$*{a};', '->', "a subscript after ->$*: perl does not compile it, or dies; take the element through the reference itself, $r->[...]")
r('arrow-after-postfix', "perl runs it: '1\\n'.", 'my $a = [1];\nmy $r = \\$a;\nsay $r->$*->[0];', '->', ARROW_POSTFIX)
r('postfix-after-postfix', "perl runs it: '1\\n'.", X + 'my $q = \\$r;\nsay $q->$*->$*;', '->', ARROW_POSTFIX)
r('whole-after-postfix', "perl runs it: '1\\n'.", 'my $a = [1];\nmy $r = \\$a;\nsay $r->$*->@*;', '->', ARROW_POSTFIX)
r('arrow-after-postfix-and-a-blank', "perl runs it: '1\\n'.", 'my $a = [1];\nmy $r = \\$a;\nsay $r->$* ->[0];', '->', ARROW_POSTFIX)
# ---- what the braces hold (D108, D114, T254)
r('empty-braces', "perl does not compile it: syntax error.", 'say ${ };', '{', '${} has nothing in its braces: perl does not compile it')
r('brace-first-in-the-braces', "perl does not compile it: syntax error.", 'say ${ {} };', '{ {', "'{' first in the braces of ${ ... }: perl takes it for a block, and does not compile it; write ${ +{ ... } }")
r('word-alone-in-the-braces', "perl runs it: '1\\n' (${true} is $true).", 'my $true = 1;\nsay ${true};', '{true', 'a word alone in ${ ... } is the name of a variable, to perl (${true} is $true): D114 refuses it; name a variable, ${ $r }')
r('word-alone-with-blanks', "perl runs it: '2\\n'.", 'my $name = 2;\nsay ${ name };', '{ name', 'a word alone in ${ ... } is the name of a variable, to perl (${name} is $name): D114 refuses it; name a variable, ${ $r }')
r('comma-in-the-braces', "perl warns: Useless use of private variable in void context.", X + 'my $s = \\$x;\nsay ${ $r, $s };', ', $s', "expected '}', found ','")
# ---- \ (D110)
r('reference-to-it-in-a-loop', "perl runs it, and says nothing: a reference to the list's own element.", 'my @l = (1, 2);\nmy @r;\nfor (@l) {\n    push @r, \\$_;\n}', '\\$_', "\\$_: a reference to $_ is cut (D110): to perl it is the list's own element; take the value into a my first")
r('reference-to-it-in-a-map', "perl runs it, and says nothing: a reference to each element of @l.", 'my @l = (1, 2);\nmy @r = map { \\$_ } @l;', '\\$_', "\\$_: a reference to $_ is cut (D110): to perl it is the list's own element; take the value into a my first")
r('reference-to-a-in-a-sort', "perl runs it, and says nothing.", 'my @l = (2, 1);\nmy @s = sort { my $p = \\$a; $p->$* <=> $b } @l;', '\\$a', "\\$a: a reference to $a is cut (D110): to perl it is the list's own element; take the value into a my first")
r('reference-to-a-loop-variable', "perl runs it, and says nothing: a store through it would change @a (T12).", 'my @a = (1, 2);\nmy @r;\nfor my $x (@a) {\n    push @r, \\$x;\n}', '\\$x', "\\$x: a reference to a loop's variable is cut (D110): to perl it is the list's own element; take the value into a my first")
r('reference-to-postfix', "perl runs it, and says nothing: the reference $r points at.", X + 'my $s = \\$r->$*;', '\\$r', '\\ before a scalar through a reference: a reference to what a reference points at is cut (D110); the reference itself is the reference')
r('reference-to-braces', "perl runs it, and says nothing.", X + 'my $s = \\${ $r };', '\\${', '\\ before a scalar through a reference: a reference to what a reference points at is cut (D110); the reference itself is the reference')
r('reference-to-a-my', "perl runs it, and says nothing.", 'my $s = \\my $x;', '\\my', "\\ before 'my': " + TAKES)
r('reference-to-a-reference', "perl runs it, and says nothing: a reference to a new scalar that holds a reference.", 'my $x = 1;\nmy $s = \\\\$x;', '\\\\', "\\ before '\\': " + TAKES)
r('reference-to-a-call', "perl runs it, and says nothing.", 'sub f() {\n    return 1;\n}\nmy $s = \\f();', '\\f', "\\ before 'f': " + TAKES)
r('reference-to-a-string', "perl runs it, and says nothing.", 'my $s = \\"a";', '\\"', '\\ before "a": ' + TAKES)
r('reference-to-an-undeclared', "perl does not compile it: Global symbol $y requires explicit package name.", 'my $s = \\$y;', '$y', '$y is not declared: my $y')
# ---- what the builtins take
r('push-onto-a-scalar', "perl does not compile it: Experimental push on scalar is now forbidden.", X + 'push $r->$*, 1;', '$r->', "push names an array, found '$r': push(@a, ...), or push($r->@*, ...)")
r('keys-of-a-scalar', "perl does not compile it: Experimental keys on scalar is now forbidden.", 'my $h = {};\nmy $r = \\$h;\nsay keys $r->$*;', '$r->', "keys names a hash, found '$r': keys %h, or keys $r->%*")
r('chomp-of-a-scalar-through-a-reference', "perl runs it, and says nothing.", X + 'chomp($r->$*);', '$r->', "chomp takes one scalar variable here, chomp($x): its value, an array, a hash, an element and $_ are not in the language (D130)")
r('list-stored-through', "perl runs it, and says nothing (the last value).", X + '$r->$* = (1, 2);', '(1, 2)', 'a list where one value is wanted: perl gives its last value, and warns of the others')
# ---- D76, D77, D57, D69 and T230's rule with what references reach (D109)
r('list-then-store-by-name', "perl runs it: '55' (T235).", X + 'say(${ $r }, ($x = 5));', '= 5', LATER.format("say's list", 'what references reach'))
r('list-then-store-through', "perl runs it: '55' (T235).", X + 'say($x, (${ $r } = 5));', '= 5', LATER.format("say's list", 'what references reach'))
r('operand-then-store', "perl runs it: '10' (T346).", X + 'say(${ $r } + ($x = 5));', '= 5', LATER.format("'+'", 'what references reach'))
r('arguments-then-store', "perl runs it: '55' (T346).", X + 'sub pair($p, $q) {\n    return "$p$q";\n}\nsay(pair($r->$*, ($x = 5)));', '= 5', LATER.format('the arguments of pair', 'what references reach'))
r('concatenation-then-store', "perl runs it: '5a5' (T346).", X + 'my $s = ${ $r } . "a" . ($x = 5);', '= 5', 'a later piece of a concatenation changes what references reach, which an earlier piece reads: perl joins the pieces as one operation and reads each late; make the change a statement of its own')
r('concatenation-then-a-sub', "perl runs it, and says nothing: the piece is read after the sub has stored.", X + 'sub set5() {\n    $x = 5;\n    return 1;\n}\nmy $s = $r->$* . set5();', 'set5();', 'a later piece of a concatenation calls set5, which can change what references reach, which an earlier piece reads: perl joins the pieces as one operation and reads each late; make the call a statement of its own')
r('loop-over-it-stores-by-name', "perl runs it: '9\\n' (T347).", X + 'for my $v (${ $r }) {\n    $x = 9;\n    say $v;\n}', '= 9', LOOP.format('a scalar that a reference reaches', 'the loop', 'loop', 'the loop'))
r('loop-over-a-taken-scalar-stores-through', "perl runs it: '9\\n' (T347).", X + 'for my $v ($x) {\n    ${ $r } = 9;\n    say $v;\n}', '= 9', LOOP.format('a scalar that a reference reaches', 'the loop', 'loop', 'the loop'))
r('map-over-it-stores-through', "perl runs it, and says nothing: $_ is $x itself, which the block stores 9 to.", X + 'my @m = map { $r->$* = 9; $_ } ($x);', '= 9', LOOP.format('a scalar that a reference reaches', 'the map', 'map', 'the map'))
r('loop-over-it-calls-a-sub-that-stores', "perl runs it: '9\\n'.", X + 'sub set9() {\n    $x = 9;\n    return;\n}\nfor my $v ($r->$*) {\n    set9();\n    say $v;\n}', 'set9();', LOOP.format('a scalar that a reference reaches', 'the loop', 'loop', 'the loop'))
r('loop-over-it-replaces-the-reference', "perl runs it: '1\\n'.", X + 'my $y = 2;\nfor my $v (${ $r }) {\n    $r = \\$y;\n    say $v;\n}', '= \\$y', LOOP.format('$r', 'the loop', 'loop', 'the loop'))
r('reference-changes-what-the-concatenation-reads', "perl runs it, and says nothing: $x is 0v (T348).", 'my $x;\nmy @a = (\\$x);\nmy $i = 5;\n${ $a[$i = 0] } = $i . "v";', '= 0', "the reference changes $i, which the concatenation on the right reads: perl joins its pieces as it stores, after the reference is worked out; take the string into a my first")
r('makes-what-the-right-side-took', "perl runs it, and says nothing: ${ $r } holds a reference (T349).", 'my $r;\n(${ $r }, my $z) = ($r, 1);', '${', 'the store makes what $r holds, which the right side has already taken: perl takes it after it is made; take the value into a my first')

# ---- four more, which the breakages of the step showed no test reached
# (briefs/step13c-mutations.py); each but the last a WRONG without its rule
r('stored-then-store-by-name', "perl runs it: '77' (the assignment is the scalar itself, read late).", X + 'say(($r->$* = 5), ($x = 7));', '= 7', LATER.format("say's list", 'what references reach'))
r('list-assignment-in-a-sub', "perl runs it: '51'.", X + 'sub swap() {\n    (${ $r }, my $z) = (5, 6);\n    return 1;\n}\nsay(${ $r }, swap());', 'swap())', LATER.format("say's list", 'what references reach'))
r('makes-what-the-scalar-is', "perl runs it, and says nothing: $x->[0] is an array, $x itself.", 'my $x;\nmy $r = \\$x;\n$x->[0] = $r->$*;', '$x->', 'the store makes what it goes through, which the right side has already taken: perl takes it after it is made; take the value into a my first')
r('octal-in-the-braces', "perl dies: Can't use an undefined value as a SCALAR reference ($a[15]).", X + 'my @a = ($r);\nsay ${ $a[017] };', '017', '017 starts with a zero: perl reads that as octal, which the language writes 0o17')

def write(first, table=None):
    n = first
    for name, why, body, at, message, nth in (T if table is None else table):
        program = f'# kind: refused\n# {why}\nuse v5.42;\n{body}\n'
        path = f't/{n}-sref-{name}'
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
