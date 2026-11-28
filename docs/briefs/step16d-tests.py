#!/usr/bin/env python3
# Writes the tests of what the census's reading asked for (part 1, D250 to
# D253) and of step 16d (part 2) and the freeze's exception (part 3), from
# tables written by hand: a `same` test's program (its .expected is perl's,
# from `make oracle`, never written here), a fault test's program with the
# line it faults on and the message, and a refusal's program with the text
# the message points at (its column counted here, from the program's own
# text) and the message. Nothing here asks the compiler.
#
#     python3 docs/briefs/step16d-tests.py 1        # part 1, tests 6000 to 6099
#     python3 docs/briefs/step16d-tests.py --perl 1 # what perl does with each
import os
import subprocess
import sys

PARTS = {}


def part(n, first_same, first_fault, first_refused, prefix):
    PARTS[n] = {'same': [], 'fault': [], 'refused': [], 'first': (first_same, first_fault, first_refused), 'prefix': prefix}
    return PARTS[n]


def same(p, name, why, body):
    p['same'].append((name, why, body))


def fault(p, name, why, body, at, message, nth=1):
    p['fault'].append((name, why, body, at, message, nth))


def refused(p, name, why, body, at, message, nth=1):
    p['refused'].append((name, why, body, at, message, nth))


# ======================================================================
# Part 1: what the census's reading asked for (D250 to D253)
P1 = part(1, 6000, 6020, 6050, 'census')

same(P1, 'scalar-bare', 'scalar without brackets, of an array, a hash and the whole container through a reference (D250).',
     'my @a = (1, 2, 3);\nmy %h = (a => 1, b => 2);\nmy $r = [4, 5];\nmy $g = {x => 1};\n'
     'say scalar @a;\nsay scalar %h;\nsay scalar keys %h;\nsay scalar values %h;\nsay scalar $r->@*;\nsay scalar @{$r};\n'
     'say scalar %{$g};\nsay scalar $g->%*;\nsay scalar @a == 3 ? "y" : "n";\nsay join ",", (scalar @a, 9);\n'
     'my @n = ();\nsay scalar @n;\nsub count($x, @rest) {\n    return scalar @rest;\n}\nsay count(1, 2, 3);\nmy $f = sub { scalar @a };\npush @a, 4;\nsay $f->();')
same(P1, 'last-index-store', 'the last index set: cut, grown with undefs, -1, a Num cut toward zero, a string of digits, through a reference and through undef (D251).',
     'my @a = (1, 2, 3);\n$#a = 1;\nsay "@a";\n$#a = 3;\nsay scalar(@a), " ", defined $a[3] ? "d" : "u", " ", $#a;\n'
     '$#a = 1.7;\nsay scalar @a;\n$#a = "2";\nsay scalar @a;\n$#a = -1;\nsay scalar @a;\n@a = (1, 2, 3);\n$#a = -0.5;\nsay scalar @a;\n'
     '@a = (1, 2, 3);\n$#a = -1.5;\nsay scalar @a;\nmy @b = (5, 6);\n$#b = $#b - 1;\nsay "@b";\n'
     'my $r = [1, 2, 3];\n$#{$r} = 0;\nsay scalar $r->@*;\n$r->$#* = 4;\nsay scalar $r->@*;\nmy $u;\n$#{$u} = 2;\nsay scalar $u->@*, ref $u;\n'
     'my %h;\n$h{list}->$#* = 1;\nsay scalar $h{list}->@*;\n$#a = 0 if 1;\nsay scalar @a;\nsub cut() {\n    my @l = (1, 2);\n    $#l = 0;\n}\ncut();\nsay "ok";')
same(P1, 'undef-statement', 'undef of a variable, an element, an array, a hash and through a reference, as the assignment it is (D252).',
     'my @a = (1);\nundef $a[3];\nsay scalar @a;\nmy %h;\nundef $h{k};\nsay exists $h{k} ? "e" : "n";\n'
     'my $x = 3;\nundef $x;\nsay defined $x ? "d" : "u";\nmy @b = (1, 2);\nundef @b;\nsay scalar @b;\n'
     'my %g = (a => 1);\nundef(%g);\nsay scalar %g;\nmy $r = [1, 2];\nundef $r->@*;\nsay scalar $r->@*;\nundef $r->[5];\nsay scalar $r->@*;\n'
     'my $u;\nundef $u->[1];\nsay ref $u;\nmy $v;\nundef %{$v};\nsay ref $v;\nmy $w;\nundef @{$w};\nsay ref $w;\n'
     'my $s = \\$x;\n$x = 1;\nundef $s->$*;\nsay defined $x ? "d" : "u";\n$x = 2;\nundef ${$s};\nsay defined $x ? "d" : "u";\n'
     '$x = 3;\nundef $x if $x > 2;\nsay defined $x ? "d" : "u";\nmy $c = 4;\nmy $k = sub { $c // "u" };\nundef $c;\nsay $k->();\n'
     'my $n = {a => {b => 1}};\nundef $n->{a}{b};\nsay exists $n->{a}{b} ? "e" : "n";\nsub clear() {\n    my $y = 1;\n    undef $y;\n}\nclear();\nsay "ok";')
same(P1, 'do-while', 'the block first, then the test: while and until, with and without brackets, a my in the block new each time, a labelled next to the loop round it, a return (D253).',
     'my $i = 5;\ndo {\n    print $i;\n    $i++;\n} while ($i < 3);\nprint "\\n";\n$i = 0;\ndo {\n    $i++;\n} until $i >= 3;\nsay $i;\n'
     'my @s;\n$i = 0;\ndo {\n    my $k = $i;\n    push @s, sub { $k };\n    $i++;\n} while $i < 3;\nsay join ",", map { $_->() } @s;\n'
     'my $j = 0;\nOUT: for my $k (1 .. 3) {\n    do {\n        $j++;\n        next OUT if $j == 2;\n    } while ($j < 5);\n    say "k$k";\n}\nsay "end $j";\n'
     'sub f() {\n    my $n = 0;\n    do {\n        $n++;\n        return $n if $n == 4;\n    } until (false);\n}\nsay f();\n'
     'my @l = (1, 2, 3);\nmy $sum = 0;\ndo {\n    $sum += shift @l;\n} until @l < 2;\nsay "$sum @l";\n'
     'my $t = 0;\ndo { $t++ } while ($t < 2);\nsay $t;')

fault(P1, 'last-index-below-minus-one', "perl empties the array in silence (T660): '3', then nothing.",
      'my @a = (1, 2, 3);\nsay scalar @a;\n$#a = -2;\nsay scalar @a;', '$#a = -2', "an array's last index set below -1")
fault(P1, 'last-index-undef', 'perl warns: Use of uninitialized value in scalar assignment, and leaves one element.',
      'my @a = (1, 2, 3);\nmy $n;\n$#a = $n;\nsay scalar @a;', '$#a = $n', 'undef where a number is wanted')
fault(P1, 'last-index-string', 'perl warns: Argument "abc" isn\'t numeric, and leaves one element.',
      'my @a = (1, 2, 3);\n$#a = "abc";\nsay scalar @a;', '$#a = "abc"', 'not a numeric string')
fault(P1, 'last-index-in-foreach', "perl cuts the array under the loop and stops it: '1'.",
      'my @a = (1, 2, 3);\nfor my $x (@a) {\n    say $x;\n    $#a = 0;\n}', '$#a = 0', 'an array was changed while a foreach is over it')
fault(P1, 'last-index-through-a-hash', 'perl dies: Not an ARRAY reference.',
      'my $r = {};\nsay "a";\n$#{$r} = 1;', '$#{$r}', 'not a reference to an array')
fault(P1, 'last-index-through-a-number', 'perl dies: Can\'t use string ("5") as an ARRAY ref while "strict refs" in use.',
      'my $r = 5;\n$r->$#* = 1;', '$r->$#*', 'not a reference to an array')
fault(P1, 'undef-in-foreach', "perl makes the list's element undef while the loop is over it: '1', then an empty line and a warning (the loop walks the array itself).",
      'my @a = (1, 2);\nfor my $x (@a) {\n    say $x;\n    undef $a[1];\n}', 'undef $a[1]', 'an array was changed while a foreach is over it')
fault(P1, 'undef-whole-in-foreach', "perl empties the array under the loop: '1', then it stops.",
      'my @a = (1, 2);\nfor my $x (@a) {\n    say $x;\n    undef @a;\n}', 'undef @a', 'an array was changed while a foreach is over it')
fault(P1, 'undef-through-a-string', 'perl dies: Can\'t use string ("a") as a HASH ref while "strict refs" in use.',
      'my $r = "a";\nundef $r->{k};', 'undef $r', 'not a reference to a hash')
fault(P1, 'last-index-sub-value', "perl runs it: '0', the assignment's value.", 'my @a = (1, 2);\nsub f() {\n    $#a = 0;\n}\nmy $v = f();\nsay $v;', '$#a = 0', 'f has no value: it does not end in a return or an expression')
fault(P1, 'undef-sub-value', "perl runs it: f gives undef, and 'u'.", 'my $x = 1;\nsub f() {\n    undef $x;\n}\nmy $v = f();\nsay defined $v ? "d" : "u";', 'undef $x', 'f has no value: it does not end in a return or an expression')
fault(P1, 'do-while-test-faults', "perl warns: Use of uninitialized value $n in numeric lt (<), and runs once: '1'. The fault names the line of the do.",
      'my $n;\nmy $i = 0;\ndo {\n    $i++;\n    say $i;\n} while ($i < $n);', 'do {', 'undef where a number is wanted')
fault(P1, 'do-while-block-faults', "perl warns: Use of uninitialized value in addition, twice, and ends: '1', '2'.",
      'my $i = 0;\nmy $u;\ndo {\n    $i++;\n    say $i;\n    say $i + $u if $i == 2;\n} while ($i < 2);', 'say $i + $u', 'undef where a number is wanted')

SCALAR_ON = "scalar @a before '{}': perl reads on for scalar's argument, or does not compile it; write scalar(...)"
refused(P1, 'scalar-reads-on', "perl runs it: '4' (scalar(@a + 1)).", 'my @a = (1, 2, 3);\nsay scalar @a + 1;', 'scalar', SCALAR_ON.format('+'))
refused(P1, 'scalar-reads-on-dot', "perl runs it: '3x'.", 'my @a = (1, 2, 3);\nsay scalar @a . "x";', 'scalar', SCALAR_ON.format('.'))
refused(P1, 'scalar-slice', 'perl warns: Scalar value @a[1] better written as $a[1].', 'my @a = (1, 2, 3);\nsay scalar @a[1];', 'scalar', SCALAR_ON.format('['))
refused(P1, 'scalar-of-a-scalar', "perl runs it: '1'.", 'my $x = 1;\nsay scalar $x;', '$x;', "scalar names an array, found '$x': scalar(@a), or scalar($r->@*)")
refused(P1, 'scalar-of-a-number', "perl runs it: '1'.", 'say scalar 1;', '1;', "scalar without brackets takes an array or a hash, found 1: scalar @a, or scalar(...)")
refused(P1, 'scalar-of-a-list-assignment', "perl runs it: '2'.", 'my @a;\nsay scalar(@a = (1, 2));', '=', "expected ')', found '='")
refused(P1, 'last-index-value', "perl runs it: '0' (the assignment's value).", 'my @a = (1, 2, 3);\nmy $x = ($#a = 0);', '= 0', "$#a = N is a statement of its own here: perl gives it a value, which is not in the language")
refused(P1, 'last-index-plus-equals', "perl runs it: the array is two longer.", 'my @a = (1, 2, 3);\n$#a += 2;', '+=', "'+=' on $#a: the last index is set with =, $#a = N;")
refused(P1, 'last-index-step', "perl runs it: the array is one longer.", 'my @a = (1, 2, 3);\n$#a++;', '++', "expected ';', found '++'")
refused(P1, 'last-index-bracketed', "perl runs it: a list assignment to $#a, which cuts the array.", 'my @a = (1, 2, 3);\n($#a) = 0;', '=', "the left side of '=' is a variable, an element, an array, a hash, or a list of them in brackets", 2)
refused(P1, 'last-index-chained', "perl runs it: both arrays cut.", 'my @a = (1, 2);\nmy @b = (1, 2);\n$#a = $#b = 0;', '= 0', "$#b = N is a statement of its own here: perl gives it a value, which is not in the language")
refused(P1, 'last-index-plus-equals-ref', "perl runs it.", 'my $r = [1];\n$#{$r} += 1;', '+=', "'+=' on $#{...}: the last index is set with =, $#{...} = N;")
refused(P1, 'last-index-in-a-map', "perl runs it: each time round, @a is cut.", 'my @a = (1, 2);\nmy @b = map { $#a = 0 } (1, 2);', '= 0', "$#a = N is a statement of its own here: perl gives it a value, which is not in the language")

refused(P1, 'undef-value', "perl runs it: $y and $x undef.", 'my $x = 3;\nmy $y = undef $x;', 'undef', "undef before '$x': perl takes what follows undef for its argument; write (undef)")
refused(P1, 'undef-hash-value', "perl runs it.", 'my %h;\nmy $y = (undef %h);', 'undef', "undef before '%h': perl takes what follows undef for its argument; write (undef)")
refused(P1, 'undef-slice', "perl makes only the last element undef (T661): '1  3', and a warning.", 'my @a = (1, 2, 3);\nundef @a[0, 1];', '@a[', 'undef takes a scalar variable, an element, an array or a hash here, found a slice: perl makes only its last element undef')
refused(P1, 'undef-comma', "perl runs it: 'a'.", 'my $x = 1;\nundef $x, say "a";', ',', "undef ... is a statement of its own here: perl gives it a value, which is not in the language; found ',' after it")
refused(P1, 'undef-loop-variable', "perl makes the list's element undef (T9).", 'my @a = (1, 2);\nfor my $x (@a) {\n    undef $x;\n}', 'undef', "$x is its loop's variable, and read-only: in perl, changing it changes the list's own element; take the value into a my")

refused(P1, 'undef-it', "perl makes the list's element undef.", 'my @a = (1, 2);\nfor (@a) {\n    undef $_;\n}', 'undef', "$_ is read-only: in perl, changing it changes the list's own element; take the value into a my")
refused(P1, 'undef-a-in-sort', "perl dies: Modification of a read-only value attempted.", 'my @a = sort { undef $a; 0 } (2, 1);', 'undef', "$a is read-only: in perl, changing it changes the list's own element; take the value into a my")
refused(P1, 'do-while-last', "perl dies: Can't \"last\" outside a loop block.", 'my $i = 0;\ndo {\n    $i++;\n    last if $i == 2;\n} while ($i < 5);', 'last', 'last with no label in do { } while: it is no loop to perl, which leaves the loop round it, or dies; label the loop it is for, and say last NAME')
refused(P1, 'do-while-next-in-a-loop', "perl leaves the for each time next runs, and prints 'end 7' (T64).", 'my $i = 0;\nfor my $k (1 .. 3) {\n    do {\n        $i++;\n        next if $i == 2;\n    } until ($i > 5);\n}\nsay "end $i";', 'next', 'next with no label in do { } until: it is no loop to perl, which leaves the loop round it, or dies; label the loop it is for, and say next NAME')
refused(P1, 'do-while-label', 'perl dies as it runs: Label not found for "last L" (T662).', 'my $i = 0;\nL: do {\n    $i++;\n} while ($i < 3);', 'do', 'a label is on a loop: after L: comes while, until or for')
refused(P1, 'do-while-my-in-test', "perl runs it: '3'.", 'my $i = 0;\ndo {\n    $i++;\n} while (my $z = $i < 3);', 'my $z', 'my in the test of do { } while: perl declares it for what follows the statement')
refused(P1, 'do-while-my-of-the-block', 'perl does not compile it: Global symbol "$j" requires explicit package name.', 'my $i = 0;\ndo {\n    my $j = $i;\n    $i++;\n} while ($j < 3);', '$j < 3', '$j is not declared: my $j')
refused(P1, 'do-while-die', 'perl 5.42 runs it for ever, the block never once (T663).', 'my $i = 0;\ndo {\n    $i++;\n} while (die "x\\n");', 'die', 'die in the test of do { } while: perl 5.42 runs do { } while (die ...) for ever (T663); test in the block, or write the loop with while')
refused(P1, 'do-while-warn', "perl warns 'w at FILE line 3.', the line of the last statement the block ran (T316).", 'my $i = 0;\ndo {\n    $i++;\n} while ($i < 2 && warn "w");', 'warn', "a warn in the test of a while or an until: perl names the line of the last statement the loop's block ran, and the message would carry it; end the message in a newline, or work the test out in the block")
refused(P1, 'do-value', "perl runs it: '2'.", 'my $x = do { 2 };', 'do', "expected a value, found 'do'")
refused(P1, 'do-statement', "perl runs it once.", 'my $i = 0;\ndo {\n    $i++;\n};', ';', "do { ... } is in the language followed by while or until, found ';': do BLOCK as a value is not (D253)", 4)
refused(P1, 'do-for', "perl runs it three times.", 'my $i = 0;\ndo {\n    $i++;\n} for 1 .. 3;', 'for', "do { ... } is in the language followed by while or until, found 'for': do BLOCK as a value is not (D253)")
refused(P1, 'do-if', "perl runs it once.", 'my $i = 0;\ndo {\n    $i++;\n} if 1;', 'if', "do { ... } is in the language followed by while or until, found 'if': do BLOCK as a value is not (D253)")
refused(P1, 'do-while-two-modifiers', 'perl does not compile it: syntax error.', 'my $i = 0;\ndo {\n    $i++;\n} while $i < 3 if 1;', 'if', "a second modifier after do { } while: perl does not compile it")
refused(P1, 'do-while-comma', 'perl runs say for ever: the test is the list, its last value say\'s (T131).', 'my $i = 0;\ndo {\n    $i++;\n} while ($i < 3), say "x";', ',', "expected ';', found ','")


# ---- part 1, items 5 to 7 (D260 to D262), asked for by the examples track
same(P1, 'or-die', "a statement joined to a die, a return, a last or a next by or and and: perl's meaning, the second run when the first's value says so (D260).",
     'my %ops = (a => 1, b => 0);\nmy $f = $ops{a} or die "no a\\n";\nsay $f;\nsub get($k) {\n    my $v = $ops{$k} or return "none";\n    return "got $v";\n}\nsay get("a"), " ", get("b"), " ", get("c");\n'
     'for my $i (1 .. 4) {\n    my $v = $i % 2 or next;\n    $i < 3 or last;\n    say "odd $i $v";\n}\nmy $n = 0;\nOUT: for my $i (1 .. 3) {\n    for my $j (1 .. 3) {\n        $n++;\n        $j == 2 and next OUT;\n    }\n}\nsay $n;\n'
     'my @l = (1);\nscalar(@l) or die "empty\\n";\n$ops{b} and die "b is true\\n";\nmy $g = $ops{b} || "default" or die "never\\n";\nsay $g;\nsub check($x) {\n    $x > 0 or return;\n    return $x;\n}\nsay check(3);')
same(P1, 'sort-brackets', 'sort with its bracket hard against the word: the bracketed list, sorted, as without them (D262).',
     'my @x = (3, 1, 2);\nmy %h = (b => 1, a => 2);\nsay join "", sort(@x);\nsay join "", sort(@x, 0);\nsay join ",", sort(keys %h);\nsay join ",", sort(values %h);\n'
     'say join "", sort({ $b <=> $a } @x);\nsay join ",", sort(reverse @x);\nsay join ",", sort(map { $_ * 2 } @x);\nmy @s = (sort(@x), 9);\nsay "@s";\n@x = sort(@x);\nsay "@x";\nfor my $k (sort(keys %h)) {\n    say $k;\n}')
fault(P1, 'or-die-message', "perl dies with the message, which ends in a newline: no line added. A dies test would do; the fault is the undef on the left.",
      'my %h = (a => 1);\nmy $u;\nmy $f = $h{a} or die "no\\n";\nsay $f;\nmy $g = $u + 1 or die "no\\n";', '$u + 1', 'undef where a number is wanted')
fault(P1, 'die-sprintf-newline', "perl warns of the undef in the sprintf, and dies 'has 1' with no line (E24-die-sprintf); the fault is the undef.",
      'my $n = 1;\nmy $u;\nsay "before";\ndie sprintf("has %d %s\\n", $n, $u)\n    if $n;', 'die sprintf', 'undef where a string is wanted')
REFUSE_JOINED = "'{}' after a statement joins it to what follows, to perl, which binds '{}' more loosely than '=': write it as an if"
refused(P1, 'or-say', "perl runs it: 'yes', and warns: Found = in conditional.", 'my %h;\n$h{a} = 3 and say "yes";', 'and', REFUSE_JOINED.format('and', 'and'))
refused(P1, 'and-assign', "perl runs both assignments, and warns: Found = in conditional (D56).", 'my ($x, $y);\n$x = 1 and $y = 2;', 'and', REFUSE_JOINED.format('and', 'and'))
refused(P1, 'or-die-constant', "perl warns: Found = in conditional, should be ==, and dies 'no'.", 'my $x = 0 or die "no\\n";', '=', "'=' where a value is tested, with nothing but a constant on its right: perl warns that == was meant")
refused(P1, 'or-die-list-assignment', "perl tests the count of the right side, 1, and does not die.", 'my ($p) = (0) or die "e\\n";', 'or', "'or die' after an assignment of a list: perl tests the count of its right side; test what was assigned in a statement of its own")
refused(P1, 'or-die-modifier', "perl runs it: the modifier is over the whole.", 'my %h = (a => 1);\nmy $f = $h{a} or die "no\\n" if 1;', 'if', "'if' after 'or die ...': a statement joined by or ends there here; write it as two statements, or with an if")
refused(P1, 'or-die-its-own-variable', 'perl does not compile it: Global symbol "$f" (the my is declared after the statement).', 'my $y = 2;\nmy $f = $y or die "f is $f\\n";', '$f\\n', '$f is not declared: my $f; in a string, \\$ is the character, and ${name} ends a name sooner')
refused(P1, 'or-die-two-lines', "perl names line 4, the statement's second line: 'x at FILE line 4.' (D150).", 'my $y = 1;\nmy $z = $y - 1\n  or die "x";', 'die', 'a die in a statement, a test or a header over more than one line: perl names a line of its own choosing there, and the message would carry it; put it on one line, or end the message in a newline')
refused(P1, 'or-return-outside-a-sub', 'perl dies when it gets to it: Can\'t return outside a subroutine.', 'my $x = 1;\n$x or return;', 'return', 'return outside a sub: perl dies there, when it gets to it')
refused(P1, 'sort-blank-bracket', "perl warns: sort (...) interpreted as function (T190).", 'my @a = (2, 1);\nmy @s = (sort (@a), 9);', '(@a)', 'sort, a blank and a bracket: perl warns that it is read as a function, and the brackets hold all of its list; write sort(...) or sort LIST')
refused(P1, 'sort-brackets-word-first', "perl sorts ('cab') by l, a sub that compares: 'cab', and warns of l.", 'sub l($w) {\n    return $w;\n}\nmy @s = sort(l ("cab"));', 'l (', 'l first after sort: perl takes a word there for the name of a sub that compares, or for a string; put a + before it, or give sort a block')
refused(P1, 'sort-brackets-scalar-first', "perl sorts @x by $by: '1'.", 'my @x = (1);\nmy $by = sub { 0 };\nmy @s = sort($by @x);', '$by @x', '$by first after sort: perl takes a scalar there for a sub that compares; put a + before it, or give sort a block')
refused(P1, 'sort-brackets-subscript', 'perl does not compile it: syntax error near ")[".', 'my @x = (1);\nmy @s = (sort(@x)[0]);', '[0]', "'[' after sort(...): perl does not compile it; bracket the whole, (sort(...))[...]")
refused(P1, 'die-join-two-lines', "perl dies 'a b' and adds no line, its last item ending in a newline; the language does not look into a join's list (D261), and refuses it.", 'my @l = ("a", "b\\n");\ndie join(" ", @l)\n    if @l;', 'die', 'a die in a statement, a test or a header over more than one line: perl names a line of its own choosing there, and the message would carry it; put it on one line, or end the message in a newline')
refused(P1, 'die-sprintf-two-lines', "perl names its own line: the format's newline is not its last character.", 'my $n = 1;\ndie sprintf("has\\n%d", $n)\n    if $n;', 'die', 'a die in a statement, a test or a header over more than one line: perl names a line of its own choosing there, and the message would carry it; put it on one line, or end the message in a newline')
same(P1, 'die-newline-through-pieces', "a die over two lines whose message ends in a newline through a concatenation or a sprintf: caught, and printed as perl makes it (D261).",
     'my @l = (1, 2);\ntry {\n    die "cycle among: " . join(" ", @l) . "\\n"\n        if @l;\n}\ncatch ($e) {\n    print "caught: $e";\n}\nmy $n = 3;\ntry {\n    die sprintf("has %d\\n", $n)\n        if $n;\n}\ncatch ($e) {\n    print "caught: $e";\n}\ntry {\n    die "a" . ("b" . "\\n")\n        if $n;\n}\ncatch ($e) {\n    print "caught: $e";\n}')


# ======================================================================
# Part 2: step 16d (D254 to D258)
P2 = part(2, 6100, 6130, 6160, '16d')

same(P2, 'substr4', 'substr of four arguments, as a statement: the piece three would take, replaced (D254).',
     'my $s = "abcdef";\nsubstr($s, 1, 2, "XYZ");\nsay $s;\nsubstr($s, -2, 1, "");\nsay $s;\nsubstr($s, 0, 0, "<");\nsay $s;\nmy $t = "abc";\nsubstr($t, 3, 1, "x");\nsay $t;\n'
     'substr($t, 1, -1, "Q");\nsay $t;\nsubstr($t, 1, 99, "");\nsay $t;\nmy $n = 12345;\nsubstr($n, 1, 1, 9);\nsay $n + 1;\nsubstr($t, 0, 1, "Z") if 1;\nsay $t;\n'
     'my $u = "hello";\nmy $k = substr($u, 1, 3);\nsubstr($u, 1, 3, "EEE");\nsay "$k $u";\nsub up($w) {\n    my $c = $w;\n    substr($c, 0, 1, uc(substr($c, 0, 1)));\n    return $c;\n}\nsay up("word");')
same(P2, 'scalar-reverse', 'scalar reverse: the list joined, its characters reversed (D258).',
     'my $s = "abc";\nsay scalar reverse $s;\nsay scalar reverse("ab", "cd");\nsay scalar(reverse("x", "y"));\nsay scalar reverse "dlrow ,", "olleH";\nmy @a = ("x", "yz");\nsay scalar reverse @a;\n'
     'say lc scalar reverse "AB";\nsay scalar reverse 12, 3.5;\nmy @e = ("");\nsay "[", scalar reverse(@e), "]";\nsub rev($w) {\n    return scalar reverse $w;\n}\nsay rev("stressed");')
same(P2, 'case-escapes', 'the case escapes in double quotes, qq and a heredoc (D256).',
     'my $x = "fOO";\nsay "\\U$x\\E-\\L$x\\E-\\u$x-\\l$x-\\u\\L$x\\E-\\L\\u$x\\E-\\Qa.b\\E";\nmy $y = "fOO bar";\nsay "a\\Uxy$y z\\Ew";\nmy $e = "";\nsay "\\u${e}d";\nsay "\\Ua${e}b\\E";\n'
     'say "\\uab\\Ucd";\nsay "\\u\\lABC";\nsay "\\l\\uabc";\nsay "\\U\\uabc\\E";\nsay "x\\L\\uABC\\E-\\uyz";\nsay "a\\u";\nsay "\\Q\\E|";\nmy @a = ("ab", "cd");\nsay "\\u@a";\nsay "\\U$a[0]\\E$a[1]";\n'
     'say qq{\\Ux\\E}, qq(\\u$x);\nprint <<"END";\n\\Uhere $x\\E done \\Q[.]\\E\nEND\nsay "\\Q$y\\E";\nsay quotemeta("a.b"), " ", quotemeta("-_x1 ");')
same(P2, 'line-and-file', '__LINE__, the line of the token itself, and __FILE__, the path perl was given (D255).',
     'say __LINE__;\nsay "a",\n  __LINE__,\n  "b";\nsay __LINE__\n  + 1;\nmy $l = 0 +\n  __LINE__;\nsay $l;\nsay __LINE__ . __LINE__;\nmy %h = (__LINE__ => 1);\nsay sort keys %h;\nsay __FILE__;\nmy $s = "__LINE__ __FILE__";\nsay $s;\nsub where() {\n    return __LINE__;\n}\nsay where();')
same(P2, 'pod-and-end', 'POD where a statement may begin, to =cut or the end; __END__ (D255).',
     'say 1;\n\n=head1 NAME\n\npod-and-end: say ? not perl\n\n=cut\n\nsay 2;\n=pod\n=cutting is not the end\nsay "no";\n=cut back to code\nsay 3;\nif (1) {\n\n=begin comment\n\ninside a block\n\n=end comment\n\n=cut\n\n    say 4;\n}\n=cut\nthis is POD too, to the next =cut\n=cut\nsay 5;\n__END__\nsay 6; not perl ( {')
same(P2, 'case-past-ascii', "uc, lc, ucfirst and lcfirst past ASCII, by perl's own tables (D257).",
     'use utf8;\nuse open ":std", ":encoding(UTF-8)";\nsay uc("é"), lc("É"), uc("ß"), ucfirst("ß"), lc("İ"), length lc("İ");\nsay ucfirst("ǆx"), uc("ǆ"), uc("ŉ"), uc("ﬃ"), lcfirst("ÉCOLE"), uc("straße");\n'
     'say lc("ΑΣ"), uc("ω"), lc("Ω"), uc("ǰ"), ucfirst("ǳ"), lcfirst("Ǳ");\nsay uc("ÿ"), lc("Ÿ"), uc("ı"), lc("K"), uc("ꞵ"), lc(chr(0x10400)) eq chr(0x10428) ? "deseret" : "no";\nsay "\\Uéa\\E \\uéa \\Lǅ\\E", ucfirst(""), uc(1.5);')
same(P2, 'quotemeta-past-ascii', "quotemeta past ASCII, by perl's own table: some characters are quoted, most are not (D256).",
     'use utf8;\nuse open ":std", ":encoding(UTF-8)";\nsay quotemeta("é-ß");\nsay length quotemeta(chr(0xAD)), length quotemeta(chr(0x2028)), length quotemeta(chr(0x263A)), length quotemeta(chr(0x10FFFD));\nsay "\\Qa b\\E";')

fault(P2, 'substr4-outside', 'perl dies: substr outside of string.', 'my $s = "abc";\nsay $s;\nsubstr($s, 4, 1, "x");', 'substr($s, 4', 'substr outside of string')
fault(P2, 'substr4-before', "perl inserts at the start for -4, 'xabc', and dies for -6, which starts and ends before the beginning.", 'my $s = "abc";\nsubstr($s, -4, 1, "x");\nsay $s;\nsubstr($s, -6, 1, "y");', 'substr($s, -6', 'substr outside of string')
fault(P2, 'scalar-reverse-empty', "perl reverses $_ for a list with nothing in it (T672): 'cba', where $_ is abc.", 'for my $w ("abc") {\n    my @e;\n    say "[", scalar reverse(@e), "]";\n}', 'say', 'scalar reverse of an empty list: perl reverses $_')
fault(P2, 'substr4-at-the-end', "perl appends: 'abcx', then dies past the end.", 'my $s = "abc";\nsubstr($s, 3, 1, "x");\nsay $s;\nsubstr($s, 5, 0, "y");', 'substr($s, 5', 'substr outside of string')
fault(P2, 'substr4-undef', "perl warns: Use of uninitialized value $s in substr, and makes 'x'.", 'my $s;\nsubstr($s, 0, 0, "x");\nsay $s;', 'substr($s', 'undef where a string is wanted')
fault(P2, 'substr4-undef-replacement', "perl warns: Use of uninitialized value, and makes 'bc'.", 'my $s = "abc";\nmy $u;\nsubstr($s, 0, 1, $u);\nsay $s;', 'substr($s', 'undef where a string is wanted')
fault(P2, 'substr4-reference', "perl makes a string of the reference's address.", 'my $s = [1];\nsubstr($s, 0, 1, "x");', 'substr($s', 'a reference where a string is wanted')
fault(P2, 'substr4-freeze', "perl changes the element the loop is over: 'ab', then 'xb'.", 'my @a = ("ab", "cd");\nfor my $e (@a) {\n    say $e;\n    my $s = $e;\n    substr($s, 0, 1, "x");\n    @a = ($s);\n}', '@a = ($s)', 'an array was changed while a foreach is over it')
fault(P2, 'uc-two-ypogegrammeni', 'perl makes one capital iota of the two (T664): 1 character.', 'say "a";\nmy $s = uc(chr(0x345) . chr(0x345));\nsay length $s;', 'my $s', 'uc of two U+0345 together: perl makes them one character')
fault(P2, 'case-escape-undef', "perl warns: Use of uninitialized value $x in uc, and prints 'a'.", 'my $x;\nsay "a\\U$x";', 'say "a', 'undef where a string is wanted')
fault(P2, 'case-escape-reference', "perl uppercases the reference's address.", 'my $r = [1];\nsay "\\L$r";', 'say', 'a reference where a string is wanted')
fault(P2, 'scalar-reverse-undef', "perl warns: Use of uninitialized value in reverse, and prints 'ba'.", 'my $u;\nsay scalar reverse("a", $u, "b");', 'say', 'undef where a string is wanted')
fault(P2, 'uc-past-ascii-printed', 'perl prints the one byte of a capital E with an acute, with no use open, and warns of nothing; the language faults (D39).', 'say uc(chr(0xE9));', 'say', "a character past ASCII printed without 'use open'")

refused(P2, 'substr4-value', "perl gives the piece taken out: 'a Xbc'.", 'my $s = "abc";\nmy $old = substr($s, 0, 1, "X");', 'substr', 'substr of 4 arguments is a statement of its own here, substr($s, ...);: perl gives it a value too, which is not in the language')
refused(P2, 'substr4-element', "perl changes the element: 'Zb'.", 'my @a = ("ab");\nsubstr($a[0], 0, 1, "Z");', '$a[0]', 'substr of 4 arguments changes its first, which is a scalar variable here: $s')
refused(P2, 'substr4-loop-variable', "perl changes the list's elements: 'Zbc Zef'.", 'my @a = ("abc", "def");\nfor my $x (@a) {\n    substr($x, 0, 1, "Z");\n}', 'substr($x', "$x is its loop's variable, and read-only: in perl, changing it changes the list's own element; take the value into a my")
refused(P2, 'substr4-modifier-value', "perl runs it.", 'my $s = "abc";\nsay substr($s, 0, 1, "X");', 'substr', 'substr of 4 arguments is a statement of its own here, substr($s, ...);: perl gives it a value too, which is not in the language')
refused(P2, 'substr-lvalue', "perl stores through the substr: 'aZZc' (D254: cut).", 'my $s = "abc";\nsubstr($s, 1, 1) = "ZZ";', '=', "the left side of '=' is a variable, an element, an array, a hash, or a list of them in brackets", 2)
refused(P2, 'substr-five', 'perl does not compile it: Too many arguments for substr.', 'my $s = "abc";\nsubstr($s, 0, 1, "x", 2);', 'substr', 'substr takes 2 to 3 arguments, and here are 5')
refused(P2, 'reverse-one-value', "perl gives 'olleh': reverse where one value is wanted reverses characters (T23).", 'my $x = reverse "hello";', 'reverse', 'reverse where one value is wanted: perl joins its arguments and reverses the characters there, which is another function')
refused(P2, 'scalar-reverse-nothing', "perl reverses $_, and warns of the undef.", 'my $x = scalar reverse;', 'reverse', 'reverse of nothing')
refused(P2, 'case-fold', "perl folds the case: 'ss'.", 'say "\\Fß";', '\\F', '\\F, the fold case, is not in the language: lc says it for most strings, and perl folds some characters to more than one (D256)')
refused(P2, 'case-end-alone', 'perl warns: Useless use of \\E.', 'say "x\\E";', '\\E', '\\E with no \\U, \\L or \\Q before it to end: perl warns that it is useless')
refused(P2, 'case-run-in-run', "perl ends the \\U at the \\L: 'ABcdef'.", 'say "\\Uab\\Lcd\\Eef";', '\\Lcd', '\\L inside a \\U that has not ended: perl\'s rules for these are its own; end the first with \\E')
refused(P2, 'case-quote-in-run', "perl quotes inside the \\U: 'AB\\.CD.E'.", 'say "\\Ua\\Qb.c\\Ed.e";', '\\Qb', '\\Q inside a \\U that has not ended: perl\'s rules for these are its own; end the first with \\E')
refused(P2, 'case-first-in-run', "perl gives 'hELLO' (\\l of the rest, inside the \\U).", 'say "\\Uh\\lello";', '\\l', "\\l inside a run of \\U, \\L or \\Q, after its start: perl's rules for these are its own; put it before the run")
refused(P2, 'case-in-single-quotes-is-text', "perl prints '\\Uab' as it is: no refusal there; this one is the line call.", 'say __LINE__();', '(', '__LINE__ is written without brackets')
refused(P2, 'end-mid-statement', 'perl does not compile it: syntax error.', 'say 1 . __END__;', '__END__', '__END__ in the middle of a statement: perl ends the program there, and does not compile what came before it')
refused(P2, 'pod-mid-statement', 'perl does not compile it: syntax error near "=".', 'say(1,\n=pod\nx\n=cut\n2);', '=pod', 'a line that begins = and a word in the middle of a statement: perl takes it for POD only where a statement may begin, and does not compile it here')
refused(P2, 'pod-line-directive', "perl reads the line directive in the POD: 'here at x line 202.' (T667).", '=pod\n\n# line 200 "x"\n\n=cut\ndie "here";', '# line', "a line '# line' and a number in POD: perl takes it for a line directive even there, which changes the line and the file a die names: reword it")
refused(P2, 'data-handle', 'perl reads the lines after __DATA__: <DATA> is not in the language (D20).', 'my @l = <DATA>;\n__DATA__\nx', '<', "expected a value, found '<'")
refused(P2, 'pod-in-a-hash', 'perl does not compile it: syntax error.', 'my %h = (\n=pod\nx\n=cut\na => 1);', '=pod', 'a line that begins = and a word in the middle of a statement: perl takes it for POD only where a statement may begin, and does not compile it here')

# ======================================================================
# Part 3: the freeze's exception for a lone range (D259)
P3 = part(3, 6200, 6220, 6250, 'freeze')

same(P3, 'lone-range', "a loop over one range whose ends name an array or a hash, the block changing it: perl works the ends out once (D259, T668).",
     'my @a = (1, 2, 3);\nfor my $i (0 .. $#a) {\n    $a[$i] *= 2;\n    push @a, 9 if $i == 0;\n}\nsay "@a";\n@a = (1, 2, 3);\nmy $n = 0;\nfor my $i (0 .. $#a) {\n    shift @a;\n    $n++;\n}\nsay "$n ", scalar(@a);\n'
     '@a = (1, 2, 3);\n$n = 0;\nfor my $i (1 .. @a) {\n    push @a, 1;\n    $n++;\n}\nsay $n;\nmy %h = (a => 1, b => 2);\n$n = 0;\nfor my $i (1 .. scalar(keys %h)) {\n    $h{$i} = 1;\n    $n++;\n}\nsay $n, " ", scalar(%h);\n'
     'my $r = [1, 2, 3];\nfor my $i (0 .. $#{$r}) {\n    push $r->@*, $i;\n}\nsay scalar $r->@*;\n@a = (1, 2, 3);\nfor my $i (0 .. $#a) {\n    $#a = 0 if $i == 0;\n    say $a[$i] // "u";\n}\n'
     'my @b = (5, 1, 4, 2);\nfor my $i (1 .. $#b) {\n    my $v = $b[$i];\n    my $j = $i - 1;\n    while ($j >= 0 && $b[$j] > $v) {\n        $b[$j + 1] = $b[$j];\n        $j--;\n    }\n    $b[$j + 1] = $v;\n}\nsay "@b";\n'
     'my @c = (1, 2, 3);\n$c[$_] *= 10 for 0 .. $#c;\nsay "@c";\n'
     'for my $i (+(0 .. $#c)) {\n    push @c, $i;\n}\nsay scalar(@c);\nfor (reverse 0 .. 1) {\n    say $_;\n}')
same(P3, 'range-end-changed', "a lone range's scalar end changed in the block: perl fixed the ends as the loop began (T172).",
     'my $n = 3;\nfor my $i (1 .. $n) {\n    $n = 1;\n    print $i;\n}\nprint "\\n";\nmy ($lo, $hi) = (1, 4);\nfor my $i ($lo .. $hi) {\n    $lo++;\n    $hi--;\n    print $i;\n}\nprint "\\n";\nsub bump($x) {\n    $n = $x;\n    return 0;\n}\nfor my $i (1 .. $n + 1) {\n    bump($i);\n    print $i;\n}\nprint " $n\\n";')
same(P3, 'range-closures', "a sub with no name over the variable of a loop over a range with a scalar end: each sub its own number (T669).",
     'my $n = 3;\nmy @s;\nfor my $i (1 .. $n) {\n    push @s, sub { $i * 10 };\n}\n$n = 9;\nsay join ",", map { $_->() } @s;\nmy @a = (4, 5);\nmy @t;\nfor my $i (0 .. $#a) {\n    push @t, sub { $a[$i] };\n}\npush @a, 6;\nsay join ",", map { $_->() } @t;')

fault(P3, 'list-not-lone', "perl walks the array itself and pushes once: the loop's list is a range and a value, so the array its end names is frozen.", 'my @a = (1, 2);\nfor my $i (0 .. $#a, 5) {\n    say $i;\n    push @a, 1 if $i == 0;\n}', 'push', 'an array was changed while a foreach is over it')
fault(P3, 'array-itself', "perl walks the array itself (T13): it is frozen, as ever.", 'my @a = (1, 2);\nfor my $x (@a) {\n    say $x;\n    push @a, 3;\n    last;\n}', 'push', 'an array was changed while a foreach is over it')
fault(P3, 'reversed-range', "a range under reverse is a list, and is frozen as one: perl's reverse takes the range's values once all the same.", 'my @a = (1, 2);\nfor my $i (reverse 0 .. $#a) {\n    say $i;\n    $a[$i] = 0;\n}', '$a[$i] = 0', 'an array was changed while a foreach is over it')
fault(P3, 'closure-froze-for-good', "the closure over a loop over the array itself freezes it for good (D162): perl pushes.", 'my @a = (1);\nmy @s;\nfor my $x (@a) {\n    push @s, sub { $x };\n}\nsay "made";\npush @a, 2;', 'push @a', 'an array was changed while a foreach is over it')

refused(P3, 'list-end-changed', "perl prints 12: the list is a range and a value, and D77 holds for it.", 'my $n = 2;\nfor my $i (1 .. $n, 9) {\n    $n = 1;\n}', '= 1', "this can change $n, which the list of the loop it is in names: perl's loop walks the variable itself; take the value into a my before the loop")
refused(P3, 'closure-list-scalar', "perl's subs share the scalar: '9,2' (T371).", 'my $n = 1;\nmy @s;\nfor my $i ($n, 2) {\n    push @s, sub { $i };\n}', '$i }', 'a sub with no name takes $i, the variable of a loop whose list names $n: to perl the sub has the scalar itself, and sees whatever is stored to it later (D166); take the value into a my in the block first, my $y = $i;')
refused(P3, 'range-variable-stored', "perl changes its own copy: 2, 3.", 'my $n = 2;\nfor my $i (1 .. $n) {\n    $i++;\n}', '++', "$i is its loop's variable, and read-only: in perl, changing it changes the list's own element; take the value into a my")
fault(P3, 'map-over-range', "perl's map has the range's values once, too; the exception is the loop's alone, and a map's list is frozen: perl prints 0, 1.", 'my @a = (1, 2);\nsay "start";\nmy @b = map { push @a, 1; $_ } 0 .. $#a;', 'my @b', 'an array was changed while a foreach is over it')


# ---- a hole the breakages showed (briefs/step16d-mutations.py): a
# concatenation over two lines whose last piece is no newline.
refused(P1, 'die-concat-two-lines', "perl names its own line: 'a1 at FILE line 5.'", 'my $n = 1;\ndie "a" . $n\n    if $n;', 'die', 'a die in a statement, a test or a header over more than one line: perl names a line of its own choosing there, and the message would carry it; put it on one line, or end the message in a newline')

refused(P1, 'last-index-makes-a-listed-scalar', "perl makes $r an array as the loop walks it, and its alias $x sees it: 'd', 'd' (D109: $#{$r} = N may make its head).", 'my $r;\nfor my $x ($r, 1) {\n    $#{$r} = 1;\n    say defined $x ? "d" : "u";\n}', '= 1', "this can change $r, which the list of the loop it is in names: perl's loop walks the variable itself; take the value into a my before the loop")


def write(n):
    p = PARTS[n]
    s0, f0, r0 = p['first']
    pre = p['prefix']
    for k, (name, why, body) in enumerate(p['same']):
        path = f't/{s0 + k}-{pre}-{name}'
        open(path + '.pl', 'w', encoding='utf-8').write(f'# {why}\nuse v5.42;\n{body}\n')
    for k, (name, why, body, at, message, nth) in enumerate(p['fault']):
        path = f't/{f0 + k}-{pre}-{name}'
        program = f'# kind: fault\n# {why}\nuse v5.42;\n{body}\n'
        open(path + '.pl', 'w', encoding='utf-8').write(program)
        k2 = program.index('use v5.42;')
        for _ in range(nth):
            k2 = program.index(at, k2 + 1)
        line = program.count('\n', 0, k2) + 1
        # What it printed before the fault is the program's own: perl's
        # start, which the oracle check holds it to; written by hand here as
        # the lines of `say` before the faulting line are worked out by the
        # test's author in `printed`.
        printed = PRINTED.get((n, name), '')
        open(path + '.expected', 'w', encoding='utf-8').write(f'{printed}fault: {message} at {path}.pl line {line}.\nexit: 1\n')
    for k, (name, why, body, at, message, nth) in enumerate(p['refused']):
        path = f't/{r0 + k}-{pre}-{name}'
        program = f'# kind: refused\n# {why}\nuse v5.42;\n{body}\n'
        open(path + '.pl', 'w', encoding='utf-8').write(program)
        k2 = program.index('use v5.42;')
        for _ in range(nth):
            k2 = program.index(at, k2 + 1)
        line = program.count('\n', 0, k2) + 1
        col = len(program[program.rfind('\n', 0, k2) + 1:k2]) + 1
        open(path + '.expected', 'w', encoding='utf-8').write(f'{path}.pl:{line}:{col}: {message}\nexit: 1\n')


# What each fault test prints before its fault, worked out by hand.
PRINTED = {
    (2, 'substr4-outside'): 'abc\n',
    (2, 'substr4-at-the-end'): 'abcx\n',
    (2, 'substr4-freeze'): 'ab\n',
    (2, 'uc-two-ypogegrammeni'): 'a\n',
    (3, 'list-not-lone'): '0\n',
    (3, 'array-itself'): '1\n',
    (3, 'reversed-range'): '1\n',
    (3, 'closure-froze-for-good'): 'made\n',
    (3, 'map-over-range'): 'start\n',
    (2, 'substr4-before'): 'xabc\n',
    (2, 'scalar-reverse-empty'): '',
    (1, 'last-index-below-minus-one'): '3\n',
    (1, 'last-index-in-foreach'): '1\n',
    (1, 'last-index-through-a-hash'): 'a\n',
    (1, 'undef-in-foreach'): '1\n',
    (1, 'undef-whole-in-foreach'): '1\n',
    (1, 'do-while-test-faults'): '1\n',
    (1, 'do-while-block-faults'): '1\n2\n',
    (1, 'or-die-message'): '1\n',
    (1, 'die-sprintf-newline'): 'before\n',
}

if __name__ == '__main__':
    if sys.argv[1] == '--perl':
        p = PARTS[int(sys.argv[2])]
        for kind in ('same', 'fault', 'refused'):
            for row in p[kind]:
                name, why, body = row[0], row[1], row[2]
                try:
                    r_ = subprocess.run([os.environ.get('CURLY_PERL', 'perl'), '-e', 'use v5.42;\n' + body], capture_output=True, text=True, timeout=5)
                except subprocess.TimeoutExpired:
                    print(f'{kind} {name}: does not end in 5 seconds')
                    continue
                print(f'{kind} {name}: exit {r_.returncode}; {r_.stdout!r}; {r_.stderr.strip()[:200]!r}')
    else:
        write(int(sys.argv[1]))
