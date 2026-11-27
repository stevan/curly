#!/usr/bin/env python3
# Writes step 13b's refusal tests from a table written by hand: the program,
# the text the message points at (its column is counted here, from the
# program's own text), and the message. Nothing here asks the compiler.
# What perl does with each is in its comment, from perl 5.42 run plain
# (`python3 docs/briefs/step13b-refusals.py --perl` prints each again).
#
#     python3 docs/briefs/step13b-refusals.py 2110
import subprocess
import sys
T = []
def r(name, why, body, at, message, nth=1):
    T.append((name, why, body, at, message, nth))

R = 'my $r = [1, 2];\n'
H = 'my $h = {a => 1};\n'
LATER = "a later part of {} can change {}, which an earlier part names: perl reads it after the change; take the value into a my first"
AFTER_BRACES = 'a subscript after the braces of a dereference is cut (D108): write $r->[...], $r->{...}, or the slice $r->@[...], $r->@{...}'

# ---- cut by D108: a subscript after the braces, and after a postfix form
r('subscript-after-braces', "perl runs it: '1\\n'.", R + 'say @{$r}[0];', '}[', AFTER_BRACES)
r('subscript-after-braces-and-a-blank', "perl runs it: '1\\n'.", R + 'say @{$r} [0];', '} [', AFTER_BRACES)
r('key-after-braces', "perl runs it: '1\\n'.", H + 'say %{$h}{"a"};', '}{', AFTER_BRACES)
r('arrow-after-braces', "perl dies: Can't use an array as a reference.", R + 'say @{$r}->[0];', '}->', "an arrow after the braces of a dereference: to perl it is an array used as a reference, which dies (D108); write the arrow after the reference itself")
r('subscript-after-postfix', "perl does not compile it: syntax error near '@*['.", R + 'say $r->@*[0];', '->', "a subscript after ->@*: perl does not compile it, or dies; take the element through the reference itself, $r->[...]")
r('arrow-after-postfix', "perl dies: Can't use an array as a reference.", R + 'say $r->@*->[0];', '->', "a subscript after ->@*: perl does not compile it, or dies; take the element through the reference itself, $r->[...]")
r('key-after-postfix-hash', "perl does not compile it: syntax error near '%*{'.", H + 'say $h->%*{a};', '->', "a subscript after ->%*: perl does not compile it, or dies; take the element through the reference itself, $r->[...]")
r('subscript-after-last-index', "perl does not compile it: syntax error near '$#*['.", R + 'say $r->$#*[0];', '->', "a subscript after ->$#*: perl does not compile it, or dies; take the element through the reference itself, $r->[...]")
r('postfix-slice-and-a-blank', "perl does not compile it: syntax error.", R + 'my @c = $r->@ [0];', '->', "after '->' comes '[' or '{', hard against it: $r->[0], $r->{k}")
# ---- what the braces hold (D108, D114, T254)
r('empty-braces', "perl does not compile it: syntax error near '@{ }'.", 'my @c = @{ };', '{', '@{} has nothing in its braces: perl does not compile it')
r('brace-first-in-the-braces', "perl does not compile it: Unmatched right curly bracket.", 'my @k = keys %{ {} };', '{ {', "'{' first in the braces of %{ ... }: perl takes it for a block, and does not compile it; write %{ +{ ... } }")
r('word-alone-in-the-braces', "perl runs it: '1\\n' (@{true} is @true).", 'my @true = (1);\nsay scalar(@{true});', '{true', 'a word alone in @{ ... } is the name of a variable, to perl (@{true} is @true): D114 refuses it; name a variable, @{ $r }')
r('word-alone-with-blanks', "perl runs it: '2\\n'.", 'my @name = (1, 2);\nsay scalar(@{ name });', '{ name', 'a word alone in @{ ... } is the name of a variable, to perl (@{name} is @name): D114 refuses it; name a variable, @{ $r }')
r('word-alone-in-last-index', "perl runs it: '-1\\n'.", 'my @a;\nsay $#{a};', '{a', 'a word alone in $#{ ... } is the name of a variable, to perl ($#{a} is $#a): D114 refuses it; name a variable, $#{ $r }')
r('word-alone-across-lines', "perl runs it: '1\\n'.", 'my %h = (a => 1);\nsay scalar(%{\n    h\n});', '{\n', 'a word alone in %{ ... } is the name of a variable, to perl (%{h} is %h): D114 refuses it; name a variable, %{ $r }')
r('word-alone-undef', "perl does not compile it: Global symbol @undef requires explicit package name.", 'my @c = @{undef};', '{undef', 'a word alone in @{ ... } is the name of a variable, to perl (@{undef} is @undef): D114 refuses it; name a variable, @{ $r }')
r('comma-in-the-braces', "perl warns: Useless use of private variable in void context.", R + 'my $s = [3];\nmy @c = @{$r, $s};', ', $s', "expected '}', found ','")
# ---- \ (D110)
r('reference-to-postfix', "perl runs it, and says nothing: a list of a reference to each element.", R + 'my @refs = \\$r->@*;', '\\$r', '\\ before a dereference: perl makes a list of a reference to each element, which is cut (D110); the reference itself is the reference')
r('reference-to-braces', "perl runs it, and says nothing: a list of a reference to each element.", R + 'my @refs = \\@{$r};', '\\@', '\\ before a dereference: perl makes a list of a reference to each element, which is cut (D110); the reference itself is the reference')
r('reference-to-postfix-slice', "perl runs it, and says nothing.", R + 'my @refs = \\$r->@[0, 1];', '\\$r', '\\ before a dereference: perl makes a list of a reference to each element, which is cut (D110); the reference itself is the reference')
# ---- what the builtins take
r('scalar-of-last-index', "perl runs it: '1\\n'.", R + 'say scalar($r->$#*);', '$r->', 'scalar names an array, found \'$r\': scalar(@a), or scalar($r->@*)')
r('keys-of-an-array', "perl runs it: '01\\n' (an array's indexes).", R + 'say keys $r->@*;', '$r->', "keys names a hash, found '$r': keys %h, or keys $r->%*")
r('push-onto-a-hash', "perl does not compile it: Type of arg 1 to push must be array (not hash dereference).", H + 'push $h->%*, 1;', '$h->', "push names an array, found '$h': push(@a, ...), or push($r->@*, ...)")
r('push-onto-a-call', "perl does not compile it: Experimental push on scalar is now forbidden.", 'sub f() {\n    return [];\n}\npush f(), 1;', 'f()', "push names an array, found 'f': push(@a, ...), or push($r->@*, ...)", 2)
r('push-with-nothing', "perl warns: Useless use of push with no values.", R + 'push $r->@*;', ';', 'push needs a value to add: push $r->@*, ...', 3)
r('pop-before-an-operator', "perl does not compile it: Experimental pop on scalar is now forbidden.", R + 'my $x = pop $r->@* + 1;', 'pop', 'pop $r->@* before \'+\': perl reads on for the array, or does not compile it; write pop($r->@*)')
r('splice-without-brackets', "perl runs it, and says nothing.", R + 'splice $r->@*, 0;', 'splice', 'splice needs brackets: splice(@a, ...)')
r('defined-of-postfix', "perl does not compile it: Can't use 'defined(@array)'.", R + 'say defined $r->@*;', 'defined', 'defined of an array: perl refuses it; scalar(@a) is how many it holds')
r('length-of-braces', "perl runs it: '1\\n', and warns: length() used on @array.", R + 'say length(@{$r});', 'length', 'length of an array: perl warns, and means the length of its count; scalar(@a) is how many it holds')
r('defined-of-a-hash', "perl does not compile it: Can't use 'defined(%hash)'.", H + 'say defined(%{$h});', 'defined', 'defined of a hash: perl refuses it; scalar(%h) is how many it holds')
r('exists-of-a-slice', "perl does not compile it: exists argument is not a HASH or ARRAY element.", H + 'say exists $h->@{a};', '$h->', "exists takes an element of a hash, found '$h': exists $h{...}")
r('delete-of-an-array-slice', "perl runs it, and says nothing.", R + 'delete $r->@[0];', '$r->', "delete takes an element of a hash, found '$r': delete $h{...}")
r('slice-with-no-index', "perl does not compile it: syntax error.", R + 'my @c = $r->@[];', '[]', 'a slice with no index: perl refuses it')
r('slice-with-no-key', "perl does not compile it: syntax error.", H + 'my @c = $h->@{};', '{}', 'a slice with no key: perl refuses it')
# ---- where they stand
r('slice-where-one-value-is-wanted', "perl runs it, and says nothing (the last element).", R + 'my $x = $r->@[0, 1];', '$r->', 'a slice where one value is wanted: perl gives its last element; write the element, $a[...]')
r('hash-slice-where-one-value-is-wanted', "perl runs it, and says nothing (the last value).", H + 'my $x = $h->@{"a"};', '$h->', 'a slice where one value is wanted: perl gives its last element; write the element, $h{...}')
r('assign-to-last-index', "perl runs it, and says nothing: the array is cut to one element.", R + '$r->$#* = 0;', '= 0', "the left side of '=' is a variable, an element, an array, a hash, or a list of them in brackets")
r('add-to-an-array', "perl does not compile it: Can't modify array dereference in addition (+).", R + '$r->@* += 1;', '+=', "'+=' on an array: an array is assigned with =")
r('array-not-the-last-target', "perl runs it, and says nothing: the array takes every value.", R + 'my $x;\n($r->@*, $x) = (1, 2);', '$r->', 'an array among the targets takes every value that is left: it is the last target')
r('slice-beside-another-target', "perl runs it, and says nothing.", R + 'my $x;\n($x, $r->@[0]) = (1, 2);', '$r->', 'a target of a list assignment is a variable, an element, undef, or, last, an array or a hash')
r('assign-to-an-array-as-a-value', "perl runs it, and says nothing ($n is the count of the right side, 2).", R + 'my $n = ($r->@* = (5, 6));', '= (5', 'an assignment of a list is a statement: perl gives the count of its right side as its value (D78)')
r('assign-in-a-for-part', "perl runs it, and says nothing.", R + 'for ($r->@* = (); 0;) {\n}', '= ()', 'an array is assigned in a statement of its own, not in a part of a for')
r('sort-scalar-and-a-blank', "perl runs it: '12\\n'.", R + 'say sort $r ->@*;', '$r', '$r first after sort: perl takes a scalar there for a sub that compares; put a + before it, or give sort a block', 2)
r('step-of-last-index', "perl runs it, and says nothing.", R + '$r->$#*++;', '++', "expected ';', found '++'")
r('step-before-postfix', "perl does not compile it: Can't modify array dereference in preincrement (++).", R + '++$r->@*;', '++', "'++' is for a variable or an element: ++$x")
# ---- D76, D77, D57 and D69 with what references reach (D109)
r('list-then-push', "perl runs it, and says nothing.", R + 'my @l = ($r->@*, push($r->@*, 3));', 'push', LATER.format('this list', 'what references reach'))
r('list-then-replace', "perl crashes: a segmentation fault (T342).", R + 'my @l = ($r->@*, ($r = [9])->[0]);', '= [9]', LATER.format('this list', '$r'))
r('push-then-replace', "perl crashes: a segmentation fault (T342).", R + 'push $r->@*, ($r = [9]);', '= [9]', LATER.format('push', '$r'))
r('values-then-store', "perl runs it, and says nothing.", H + 'my @l = (values $h->%*, $h->{a} = 9);', '= 9', LATER.format('this list', 'what references reach'))
r('slice-then-store', "perl runs it, and says nothing.", R + 'my @l = ($r->@[0, 1], $r->[0] = 9);', '= 9', LATER.format('this list', 'what references reach'))
r('arguments-then-push', "perl runs it: '3'.", R + 'sub f(@x) {\n    return scalar(@x);\n}\nsay f($r->@*, push($r->@*, 3));', 'push', LATER.format('the arguments of f', 'what references reach'))
r('loop-assigns-the-reference', "perl runs it: '1\\n2\\n' over the old array.", R + 'for my $x ($r->@*) {\n    $r = [7];\n    say $x;\n}', '= [7]', "this can change $r, which the list of the loop it is in names: perl's loop walks the variable itself; take the value into a my before the loop")
r('loop-pushes-through-its-name', "perl runs it, and says nothing.", R + 'for my $x ($r->@*) {\n    push $r->@*, 3;\n    last;\n}', 'push', "this can change $r, which the list of the loop it is in names: perl's loop walks the variable itself; take the value into a my before the loop")
r('map-assigns-the-reference', "perl crashes: a segmentation fault (T342).", R + 'my @m = map { $r = [7]; $_ } @{$r};', '= [7]', "this can change $r, which the list of the map it is in names: perl's map walks the variable itself; take the value into a my before the map")
r('loop-sub-assigns-the-reference', "perl runs it, and says nothing.", R + 'sub swap() {\n    $r = [7];\n    return;\n}\nfor my $x ($r->@*) {\n    swap();\n}', 'swap();', "this can change $r, which the list of the loop it is in names: perl's loop walks the variable itself; take the value into a my before the loop")
r('makes-what-the-right-side-took', "perl runs it, and says nothing.", 'my $r;\n$r->@* = ($r);', '$r->', 'the store makes what $r holds, which the right side has already taken: perl takes it after it is made; take the value into a my first')
r('concatenation-then-push', "perl runs it, and says nothing.", R + 'my $s = $r->[0] . push($r->@*, 3);', 'push', 'a later piece of a concatenation changes $r, which an earlier piece reads: perl joins the pieces as one operation and reads each late; make the change a statement of its own')
r('concatenation-then-a-sub', "perl runs it, and says nothing.", R + 'sub grow() {\n    push $r->@*, 3;\n    return 1;\n}\nmy $s = $r->[0] . grow();', 'grow();', 'a later piece of a concatenation calls grow, which can change what references reach, which an earlier piece reads: perl joins the pieces as one operation and reads each late; make the call a statement of its own')

# ---- six more, which the breakages of the step showed no test reached
# (briefs/step13b-mutations.py)
r('subscript-after-a-postfix-slice', "perl does not compile it: syntax error near '][' .", 'my $r = [[1, 2]];\nsay $r->@[0][1];', '[1]', 'a subscript after a slice: perl takes it for an element of what the slice gives; take the slice into an array first')
r('list-then-push-by-name', "perl runs it: '1 2 3' (the list holds the array's own elements).", 'my @a = (1, 2);\nmy $r = \\@a;\nmy @l = ($r->@*, push(@a, 3));', 'push', LATER.format('this list', 'what references reach'))
r('loop-assigns-through-its-name', "perl runs it, and says nothing.", R + 'for my $x ($r->@*) {\n    $r->@* = (1);\n    last;\n}', '= (1)', "this can change $r, which the list of the loop it is in names: perl's loop walks the variable itself; take the value into a my before the loop")
r('values-then-delete-slice', "perl runs it: '3'.", H + 'my @l = (values $h->%*, delete $h->@{"a"});', 'delete', LATER.format('this list', 'what references reach'))
r('loop-list-assigns-through-its-name', "perl runs it: '2'.", R + 'for my $x ($r->@*) {\n    my $y;\n    ($y, $r->@*) = (1, 2);\n    last;\n}', '= (1, 2)', "this can change $r, which the list of the loop it is in names: perl's loop walks the variable itself; take the value into a my before the loop")
r('octal-in-the-braces', "perl runs it: '15'.", 'my @c = @{ [017] };', '017', '017 starts with a zero: perl reads that as octal, which the language writes 0o17')
r('list-then-push-makes-its-head', "perl runs it: 'd' (the list holds $h itself, which the push made a hash).", 'my $h;\nmy @l = ($h, push($h->{m}->@*, 1));\nsay defined $l[0] ? "d" : "u";', 'push', LATER.format('this list', '$h'))
r('arguments-scalar-then-change', "perl runs it: '5 2 5'.", 'sub f(@a) {\n    return "@a";\n}\nmy $x = 1;\nmy $r = [2];\nsay f($x, $r->@*, ($x = 5));', '= 5', LATER.format('the arguments of f', '$x'))

def write(first, table=None):
    n = first
    for name, why, body, at, message, nth in (T if table is None else table):
        program = f'# kind: refused\n# {why}\nuse v5.42;\n{body}\n'
        path = f't/{n}-whole-{name}'
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
