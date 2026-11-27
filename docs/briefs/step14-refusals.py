#!/usr/bin/env python3
# Writes step 14's refusal tests from a table written by hand: the program,
# the text the message points at (its column is counted here, from the
# program's own text), and the message. Nothing here asks the compiler.
# What perl does with each is in its comment, from perl 5.42 run plain
# (`python3 docs/briefs/step14-refusals.py --perl` prints each again).
#
#     python3 docs/briefs/step14-refusals.py 3500
import subprocess
import sys
T = []
def r(name, why, body, at, message, nth=1):
    T.append((name, why, body, at, message, nth))

F = 'my $f = sub { 1 };\n'
AMP = "'&' before a sub's name or a reference: a call by '&' is cut (D21, D165); call a sub by its name with brackets, name(...), or through a reference, $f->(...)"
OUT = "{} out of a sub with no name: perl leaves the loop of whatever called the sub, and warns (D165); give back a value that says to, and test it in the loop"
TAKES = "a sub with no name takes ${}, the variable of a loop whose list names {}: to perl the sub has the scalar itself, and sees whatever is stored to it later (D166); take the value into a my in the block first, my $y = ${};"
READONLY = "${} is its loop's variable, and read-only: in perl, changing it changes the list's own element; take the value into a my"
LATER = "a later part of {} can change {}, which an earlier part names: perl reads it after the change; take the value into a my first"
LOOP = "this can change {}, which the list of {} it is in names: perl's {} walks the variable itself; take the value into a my before {}"
AFTER_REF = "{} after \\&nm: perl calls nm and takes a reference to what it gives; bracket the reference, (\\&nm)->(...)"
NM = 'sub nm() {\n    return sub { 42 };\n}\n'
BUMP = 'my $x = 1;\nmy $bump = sub { $x = 9; return 0 };\n'

# ---- cut by D21 and D165
r('amp-call', "perl runs it, and says nothing.", F + '&$f();', '&$', AMP)
r('amp-braces', "perl runs it, and says nothing.", F + '&{$f}();', '&{', AMP)
r('amp-name', "perl runs it, and says nothing.", 'sub g() {\n    return 1;\n}\n&g();', '&g', AMP)
r('amp-name-alone', "perl runs it, and says nothing: g is called with the caller's @_.", 'sub g() {\n    return 1;\n}\n&g;', '&g', AMP)
r('arrow-amp-star', "perl runs it, and says nothing.", F + '$f->&*;', '->', "->&*: a call by '&' is cut (D21, D165): call through the reference with its brackets, $f->(...)")
r('arrow-amp-name', "perl dies: Undefined subroutine &main::g (a call of g with $f first, as a lexical method is called).", F + '$f->&g();', '->', "'->&' and a name: a lexical method call, and classes are not in the language yet (step 17)")
r('sort-by-a-sub', "perl runs it: '1 2'.", 'my $by = sub { $a <=> $b };\nmy @s = sort $by 2, 1;\nsay "@s";', '$by 2', '$by first after sort: perl takes a scalar there for a sub that compares; put a + before it, or give sort a block')
r('last-out-of-a-sub', "perl runs it: '1', and warns: Exiting subroutine via last (T365).", 'for my $i (1 .. 2) {\n    say $i;\n    my $f = sub { last };\n    $f->();\n}', 'last', OUT.format('last'))
r('next-out-of-a-sub', "perl runs it, prints nothing, and warns twice: Exiting subroutine via next.", 'for my $i (1 .. 2) {\n    my $f = sub { next; };\n    $f->();\n    say $i;\n}', 'next', OUT.format('next'))
r('last-labelled-out-of-a-sub', "perl runs it: '1', and warns: Exiting subroutine via last.", 'LOOP: for my $i (1 .. 2) {\n    say $i;\n    my $f = sub { last LOOP; };\n    $f->();\n}', 'last', OUT.format('last'))
r('attribute', "perl runs it, and says nothing.", 'my $f = sub :lvalue { 1 };', ':lvalue', "after sub comes its signature or its block, found ':': a prototype or an attribute is not in the language (D165)")
r('wantarray', "perl runs it: '1'.", 'my $f = sub { wantarray };\nmy @l = $f->();\nsay @l;', 'wantarray', "'wantarray' is not in the language")
r('arguments-array', "perl runs it: '2'.", 'my $f = sub { scalar(@_) };\nsay $f->(1, 2);', '@_', '@_ is not in the language: a sub has a signature (D17)')
r('named-sub-in-a-sub-with-no-name', "perl runs it, and warns of nothing: g is named once, for good (T31).", 'my $f = sub {\n    sub g() {\n        return 1;\n    }\n    return g();\n};', 'sub g', 'a sub stands at the top level of the file: not in a block, a loop or another sub')
r('named-sub-as-a-value', "perl does not compile it: Illegal declaration of subroutine main::g.", 'my $f = sub g { 1 };', 'g {', 'sub g as a value: a named sub stands at the top level of the file, as a statement; a sub with no name is sub (...) { ... }')
# ---- not built (D160)
r('my-sub', "perl dies: Undefined subroutine &main::fact (T369).", 'my sub fact($n) {\n    return $n <= 1 ? 1 : $n * fact($n - 1);\n}\nsay fact(5);', 'sub', "after 'my', expected a variable, found 'sub'")
r('state', "perl runs it: '121' (T369).", 'my @s;\nfor my $i (1 .. 2) {\n    push @s, sub { state $n = 0; return ++$n };\n}', 'state', "'state' is not in the language")
# ---- how a call through a reference is written (T373, T374)
r('reference-then-arrow', "perl runs it: 'SCALAR' (T373).", NM + 'my $r = \\&nm->();\nsay ref($r);', '->()', AFTER_REF.format("'->'"))
r('reference-then-bracket', "perl dies: Too many arguments for subroutine 'main::nm': it calls nm(1).", NM + 'my $r = \\&nm(1);', '(1)', AFTER_REF.format("'('"))
r('reference-then-subscript', "perl does not compile it: syntax error.", NM + 'my $r = \\&nm[0];', '[0]', AFTER_REF.format("'['"))
r('reference-of-no-sub', "perl runs it, and dies when it is called: Undefined subroutine &main::none.", 'my $r = \\&none;', '\\&', '\\&none: the program has no sub called none')
r('reference-of-a-word', "perl does not compile it: syntax error.", 'my $r = \\&say;', '&', "\\& before 'say': \\& takes the name of one of the program's subs, hard against it, \\&name")
r('call-after-a-call-by-name', "perl does not compile it: syntax error (T374).", 'sub mk2() {\n    return sub { 12 };\n}\nsay mk2()();', '();\n', 'a bracket after a call by name: perl does not compile name()(...) (T374); write name()->(...)')
r('call-after-brackets', "perl does not compile it: syntax error (T374).", F + 'say(($f)(1));', '(1)', 'a bracket after brackets: perl does not compile (...)(...) (T374); a call through a reference is (...)->(...)')
r('call-after-a-variable', "perl dies: Not a GLOB reference ($f is a file handle there).", F + 'say $f(1);', '(1)', "$f(...) is not perl's: a call through a reference is $f->(...)")
r('blank-before-the-call', "perl runs it: '3'.", 'my %h = (add => sub ($x, $y) { $x + $y });\nsay $h{add} (1, 2);', '(1, 2)', "a blank before the bracket of a call through a reference: perl takes it, and reads on; write it hard against what it calls, $h{f}(...)")
r('key-after-a-call', "perl runs it: '5'.", 'my $g = sub { return {a => 5} };\nsay $g->(){a};', '{a}', "'{' hard after a call through a reference: perl takes it for a key of what the call gives; write the arrow, ->{...}")
r('sub-with-no-name-alone', "perl warns: Useless use of anonymous subroutine in void context.", 'sub { 1 };', 'sub', 'this statement only has a value, and nothing is done with it: perl warns that it is useless')
# ---- __SUB__ (D166)
r('current-sub-at-the-top', "perl runs it: 'u' (undef there).", 'say defined(__SUB__) ? "d" : "u";', '__SUB__', "__SUB__ outside a sub with no name: perl gives undef at the top of the file and the sub itself in a named one; write the sub's name, or \\&name")
r('current-sub-in-a-named-sub', "perl runs it: '120'.", 'sub fact($n) {\n    return $n <= 1 ? 1 : $n * __SUB__->($n - 1);\n}\nsay fact(5);', '__SUB__', "__SUB__ outside a sub with no name: perl gives undef at the top of the file and the sub itself in a named one; write the sub's name, or \\&name")
r('current-sub-with-brackets', "perl runs it, and says nothing.", 'my $f = sub { __SUB__() };', '()', '__SUB__ is written without brackets: __SUB__->(...) calls the sub')
# ---- what a sub with no name sees (D55, D162; T362, T376)
r('itself-in-its-my', "perl does not compile it: Global symbol \"$f\" requires explicit package name (T376).", 'my $f = sub { $f->() };', '$f->', '$f is not declared yet: a my is seen from the statement after it (D55), and the sub is made before the store; write my $f; $f = sub { ... };, or __SUB__ for the sub itself')
r('it-in-a-map', "perl runs it: 'undef' (T362).", 'my @a = (1, 2);\nmy @s = map { sub { $_ } } @a;\nsay defined($s[0]->()) ? "def" : "undef";', '$_ }', "$_ in a sub with no name: to perl it is the global $_, read when the sub runs, and not the for's, map's or grep's round it (D162); take the value into a my first")
r('it-in-a-loop', "perl runs it, and warns: Use of uninitialized value $_.", 'my @s;\nfor (1, 2) {\n    push @s, sub { $_ + 1 };\n}\nsay $s[0]->();', '$_ +', "$_ in a sub with no name: to perl it is the global $_, read when the sub runs, and not the for's, map's or grep's round it (D162); take the value into a my first")
r('a-in-a-sort', "perl runs it, and says nothing.", 'my @s = sort { my $f = sub { $a }; $f->() <=> $b } (2, 1);', '$a }', "$a in a sub with no name: to perl it is the global $a, read when the sub runs, and not the sort's round it (D162); take the value into a my first")
# ---- the variable of a loop a closure takes (D162, D166; T371, T372)
r('loop-over-scalars', "perl runs it: '9' (T361).", 'my ($p, $q) = (1, 2);\nmy @s;\nfor my $x ($p, $q) {\n    push @s, sub { $x };\n}\n$p = 9;\nsay $s[0]->();', '$x }', TAKES.format('x', '$p', 'x'))
r('loop-over-a-choice', "perl runs it: '9' (T371).", 'my ($p, $q, $c) = (1, 2, 1);\nmy @s;\nfor my $x ($c ? $p : $q) {\n    push @s, sub { $x };\n}\n$p = 9;\nsay $s[0]->();', '$x }', TAKES.format('x', '$c', 'x'))
r('loop-over-a-range-to-a-scalar', "perl runs it: '12'.", 'my $n = 2;\nmy @s;\nfor my $i (1 .. $n) {\n    push @s, sub { $i };\n}\nsay $s[0]->(), $s[1]->();', '$i }', TAKES.format('i', '$n', 'i'))
r('loop-through-a-reference', "perl runs it: '1'.", 'my $r = [1, 2];\nmy @s;\nfor my $x ($r->@*) {\n    push @s, sub { $x };\n}\nsay $s[0]->();', '$x }', TAKES.format('x', '$r', 'x'))
r('loop-over-a-scalar-through-a-reference', "perl runs it: '9'.", 'my $v = 1;\nmy %h = (s => \\$v);\nmy @s;\nfor my $x (${ $h{s} }) {\n    push @s, sub { $x };\n}', '$x }', TAKES.format('x', 'a scalar through a reference', 'x'))
r('inner-loop-over-grep', "perl runs it: '9' (T371).", 'my @a = (1, 2);\nmy @s;\nfor my $x (@a) {\n    for my $y (grep { 1 } $x) {\n        push @s, sub { $y };\n    }\n}', '$y }', TAKES.format('y', '$x', 'y'))
r('store-to-a-taken-loop-variable', "perl runs it: '5 2' (T372).", 'my @a = (1, 2);\nmy @s;\nfor my $x (@a) {\n    push @s, sub { $x = 5 };\n}', '= 5', READONLY.format('x'))
r('step-a-taken-loop-variable', "perl runs it, and says nothing: @a is (2, 3).", 'my @a = (1, 2);\nmy @s;\nfor my $x (@a) {\n    push @s, sub { $x++ };\n}', '++', READONLY.format('x'))
r('store-in-a-nested-sub', "perl runs it, and says nothing: $a[0] is 5.", 'my @a = (1, 2);\nmy @s;\nfor my $x (@a) {\n    push @s, sub { return sub { $x = 5 } };\n}', '= 5', READONLY.format('x'))
r('store-in-a-default', "perl runs it, and says nothing: $a[0] is 5.", 'my @a = (1, 2);\nmy @s;\nfor my $x (@a) {\n    push @s, sub ($y = ($x = 5)) { $y };\n}', '= 5', READONLY.format('x'))
# ---- a call through a reference is a call of any such sub (D163; T364)
r('list-then-a-call-that-stores', "perl runs it: '9 0' (T364).", BUMP + 'my @l = ($x, $bump->());\nsay "@l";', '$bump->', LATER.format('this list', '$x'))
r('concatenation-then-a-call', "perl runs it, and says nothing: the piece is read after the sub has stored.", BUMP + 'my $s = $x . $bump->();', '$bump->', 'a later piece of a concatenation calls a sub through a reference, which can change $x, which an earlier piece reads: perl joins the pieces as one operation and reads each late; make the call a statement of its own')
r('loop-calls-one-that-stores', "perl runs it: '9'.", BUMP + 'for my $v ($x) {\n    $bump->();\n    say $v;\n}', '$bump->', LOOP.format('$x', 'the loop', 'loop', 'the loop'))
r('any-sub-may-be-called', "perl runs it: '1' (the call is of the sub that does not store; D163 asks of every one).", BUMP + 'my $quiet = sub { 0 };\nfor my $v ($x) {\n    $quiet->();\n    say $v;\n}', '$quiet->', LOOP.format('$x', 'the loop', 'loop', 'the loop'))
r('a-named-sub-by-reference', "perl runs it: '9'.", 'my $x = 1;\nsub set9() {\n    $x = 9;\n    return 0;\n}\nmy $r = \\&set9;\nfor my $v ($x) {\n    $r->();\n    say $v;\n}', '$r->', LOOP.format('$x', 'the loop', 'loop', 'the loop'))
r('head-after-a-list-of-arguments', "perl runs it: '5 2' (T370: the arguments are in place before mk runs).", 'my $x = 1;\nmy @a = (2);\nsub mk() {\n    $x = 5;\n    return sub (@l) { "@l" };\n}\nsay mk()->($x, @a);', 'mk()->', LATER.format('a call through a reference', '$x'))
r('a-captured-variable-in-a-sub', "perl runs it: '5 0' (the closure stores to g's own $n, which the list named first).", 'sub g() {\n    my $n = 2;\n    my $set = sub { $n = 5; return 0 };\n    my @l = ($n, $set->());\n    return "@l";\n}\nsay g();', '$set->', LATER.format('this list', '$n'))

# ---- four more, which the breakages of the step showed no test reached
# (briefs/step14-mutations.py)
r('only-a-value-in-a-sub-with-no-name', "perl warns: Useless use of a constant (2) in void context (it folds 1 + 1).", 'my $f = sub {\n    1 + 1;\n    return 2;\n};', '1 + 1', 'this statement only has a value, and nothing is done with it: perl warns that it is useless')
r('head-that-stores', "perl runs it: '5 0' (the head is worked out after the list's first item is named).", 'my $x = 1;\nsub mk() {\n    $x = 5;\n    return sub { 0 };\n}\nmy @l = ($x, mk()->());\nsay "@l";', 'mk()->', LATER.format('this list', '$x'))
r('sub-that-calls-through-a-reference', "perl runs it: '9 0'.", BUMP + 'sub go() {\n    return $bump->();\n}\nmy @l = ($x, go());\nsay "@l";', 'go());', LATER.format('this list', '$x'))
r('argument-and-a-default-that-stores', "perl hands the second parameter 9: the default ran before it was copied (T149, D76).", 'my @a = (1, 2);\nsub bump() {\n    $a[1] = 9;\n    return 5;\n}\nmy $f = sub ($x //= bump(), $y = 0) { return $x . "," . $y };\nsay $f->(undef, $a[1]);', '$f->', LATER.format('a call through a reference', '@a'))

def write(first, table=None):
    n = first
    for name, why, body, at, message, nth in (T if table is None else table):
        program = f'# kind: refused\n# {why}\nuse v5.42;\n{body}\n'
        path = f't/{n}-clo-{name}'
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
