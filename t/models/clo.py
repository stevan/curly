#!/usr/bin/env python3
"""t/3400 to t/3403, and the faults from t/3420: subs with no name,
closures and calls through a reference (step 14; D160 to D166).

The definition, which is all this file knows of the language:

  sub (PARAMS) { ... }   a sub with no name, where a value may begin; its
  sub { ... }            value a reference to it, holding the variables it
                         uses from outside, the variables themselves
  EXPR->(ARGS)           a call through a reference; after a subscript or
                         another such call the arrow may be left out
  \\&name                a reference to a named sub of the program's
  __SUB__                in a sub with no name, its own reference

**A closure has the variable, not its value**: it reads it when it runs,
and a store from it is a store to the variable. A `my` reached again is
a new variable, so each closure made in a loop or a call has its own,
and one over a C-style `for`'s variable shares the one. **A closure over
a `foreach`'s variable takes a copy, and every array and hash the loop
froze stays frozen for good**: a later store to one is the fault `an
array was changed while a foreach is over it` (D162). A call through a
reference works out its arguments, then what stands before the arrow,
then calls (T370); a wrong count is a fault after the arguments have
run; the caller's context is handed on, so a sub that returns a list to
a call for one value is the fault `... returned a list where one value
is wanted`, `an anonymous sub` for one with no name. Calling undef is
`undef where a reference is wanted`, and anything else that is no sub's
reference `not a reference to a sub` (D164). A sub's reference is true,
defined, `==` to itself, `ref` gives `CODE`; a sub with no name gives a
new value each time it is reached if it uses any variable from outside
it, the file's too, and one value for the whole run otherwise (D161).
Anywhere else a number or a string is wanted it is a fault (D112).

The model is Python, with every variable a closure may use written out
as a `Cell` by hand: Python's own closures bind late and would hide what
the loops do. A closure is a Python function that is handed the cells it
uses when it is made. perl is the second derivation: t/checks.py oracle
holds every .expected of a test without a `kind:` to what perl 5.42
prints, and each fault test's output to the start of it.

3400 counters, shared variables and nesting; 3401 closures in loops;
3402 calls, identity, recursion and context; 3403 closures in data, in
`map`, `grep` and `sort`, and through `die`. 3420 on each fault once.

Every command that writes a file, one a line (t/checks.py runs them all):

    python3 t/models/clo.py --program 3400 > t/3400-clo-counters-and-sharing.pl
    python3 t/models/clo.py 3400 > t/3400-clo-counters-and-sharing.expected
    python3 t/models/clo.py --program 3401 > t/3401-clo-in-loops.pl
    python3 t/models/clo.py 3401 > t/3401-clo-in-loops.expected
    python3 t/models/clo.py --program 3402 > t/3402-clo-calls.pl
    python3 t/models/clo.py 3402 > t/3402-clo-calls.expected
    python3 t/models/clo.py --program 3403 > t/3403-clo-in-data.pl
    python3 t/models/clo.py 3403 > t/3403-clo-in-data.expected
    python3 t/models/clo.py --program 3420 > t/3420-fault-clo-count-too-many.pl
    python3 t/models/clo.py 3420 > t/3420-fault-clo-count-too-many.expected
    python3 t/models/clo.py --program 3421 > t/3421-fault-clo-count-too-few.pl
    python3 t/models/clo.py 3421 > t/3421-fault-clo-count-too-few.expected
    python3 t/models/clo.py --program 3422 > t/3422-fault-clo-count-at-least.pl
    python3 t/models/clo.py 3422 > t/3422-fault-clo-count-at-least.expected
    python3 t/models/clo.py --program 3423 > t/3423-fault-clo-count-of-a-named-sub.pl
    python3 t/models/clo.py 3423 > t/3423-fault-clo-count-of-a-named-sub.expected
    python3 t/models/clo.py --program 3424 > t/3424-fault-clo-odd-arguments.pl
    python3 t/models/clo.py 3424 > t/3424-fault-clo-odd-arguments.expected
    python3 t/models/clo.py --program 3425 > t/3425-fault-clo-call-undef.pl
    python3 t/models/clo.py 3425 > t/3425-fault-clo-call-undef.expected
    python3 t/models/clo.py --program 3426 > t/3426-fault-clo-call-missing-element.pl
    python3 t/models/clo.py 3426 > t/3426-fault-clo-call-missing-element.expected
    python3 t/models/clo.py --program 3427 > t/3427-fault-clo-call-missing-key.pl
    python3 t/models/clo.py 3427 > t/3427-fault-clo-call-missing-key.expected
    python3 t/models/clo.py --program 3428 > t/3428-fault-clo-call-a-call-giving-undef.pl
    python3 t/models/clo.py 3428 > t/3428-fault-clo-call-a-call-giving-undef.expected
    python3 t/models/clo.py --program 3429 > t/3429-fault-clo-call-an-array-reference.pl
    python3 t/models/clo.py 3429 > t/3429-fault-clo-call-an-array-reference.expected
    python3 t/models/clo.py --program 3430 > t/3430-fault-clo-call-a-hash-reference.pl
    python3 t/models/clo.py 3430 > t/3430-fault-clo-call-a-hash-reference.expected
    python3 t/models/clo.py --program 3431 > t/3431-fault-clo-call-a-scalar-reference.pl
    python3 t/models/clo.py 3431 > t/3431-fault-clo-call-a-scalar-reference.expected
    python3 t/models/clo.py --program 3432 > t/3432-fault-clo-call-a-number.pl
    python3 t/models/clo.py 3432 > t/3432-fault-clo-call-a-number.expected
    python3 t/models/clo.py --program 3433 > t/3433-fault-clo-call-a-string.pl
    python3 t/models/clo.py 3433 > t/3433-fault-clo-call-a-string.expected
    python3 t/models/clo.py --program 3434 > t/3434-fault-clo-call-the-result.pl
    python3 t/models/clo.py 3434 > t/3434-fault-clo-call-the-result.expected
    python3 t/models/clo.py --program 3435 > t/3435-fault-clo-call-after-a-subscript.pl
    python3 t/models/clo.py 3435 > t/3435-fault-clo-call-after-a-subscript.expected
    python3 t/models/clo.py --program 3436 > t/3436-fault-clo-index-a-sub.pl
    python3 t/models/clo.py 3436 > t/3436-fault-clo-index-a-sub.expected
    python3 t/models/clo.py --program 3437 > t/3437-fault-clo-key-a-sub.pl
    python3 t/models/clo.py 3437 > t/3437-fault-clo-key-a-sub.expected
    python3 t/models/clo.py --program 3438 > t/3438-fault-clo-scalar-of-a-sub.pl
    python3 t/models/clo.py 3438 > t/3438-fault-clo-scalar-of-a-sub.expected
    python3 t/models/clo.py --program 3439 > t/3439-fault-clo-whole-of-a-sub.pl
    python3 t/models/clo.py 3439 > t/3439-fault-clo-whole-of-a-sub.expected
    python3 t/models/clo.py --program 3440 > t/3440-fault-clo-list-where-one-value.pl
    python3 t/models/clo.py 3440 > t/3440-fault-clo-list-where-one-value.expected
    python3 t/models/clo.py --program 3441 > t/3441-fault-clo-list-where-one-value-array.pl
    python3 t/models/clo.py 3441 > t/3441-fault-clo-list-where-one-value-array.expected
    python3 t/models/clo.py --program 3442 > t/3442-fault-clo-no-value.pl
    python3 t/models/clo.py 3442 > t/3442-fault-clo-no-value.expected
    python3 t/models/clo.py --program 3443 > t/3443-fault-clo-nothing-where-one-value.pl
    python3 t/models/clo.py 3443 > t/3443-fault-clo-nothing-where-one-value.expected
    python3 t/models/clo.py --program 3444 > t/3444-fault-clo-frozen-forever-push.pl
    python3 t/models/clo.py 3444 > t/3444-fault-clo-frozen-forever-push.expected
    python3 t/models/clo.py --program 3445 > t/3445-fault-clo-frozen-forever-store.pl
    python3 t/models/clo.py 3445 > t/3445-fault-clo-frozen-forever-store.expected
    python3 t/models/clo.py --program 3446 > t/3446-fault-clo-frozen-forever-assign.pl
    python3 t/models/clo.py 3446 > t/3446-fault-clo-frozen-forever-assign.expected
    python3 t/models/clo.py --program 3447 > t/3447-fault-clo-frozen-forever-shift.pl
    python3 t/models/clo.py 3447 > t/3447-fault-clo-frozen-forever-shift.expected
    python3 t/models/clo.py --program 3448 > t/3448-fault-clo-frozen-forever-in-the-loop.pl
    python3 t/models/clo.py 3448 > t/3448-fault-clo-frozen-forever-in-the-loop.expected
    python3 t/models/clo.py --program 3449 > t/3449-fault-clo-frozen-forever-values.pl
    python3 t/models/clo.py 3449 > t/3449-fault-clo-frozen-forever-values.expected
    python3 t/models/clo.py --program 3450 > t/3450-fault-clo-frozen-forever-delete.pl
    python3 t/models/clo.py 3450 > t/3450-fault-clo-frozen-forever-delete.expected
    python3 t/models/clo.py --program 3451 > t/3451-fault-clo-frozen-forever-through-a-reference.pl
    python3 t/models/clo.py 3451 > t/3451-fault-clo-frozen-forever-through-a-reference.expected
    python3 t/models/clo.py --program 3452 > t/3452-fault-clo-frozen-forever-from-a-sub.pl
    python3 t/models/clo.py 3452 > t/3452-fault-clo-frozen-forever-from-a-sub.expected
    python3 t/models/clo.py --program 3453 > t/3453-fault-clo-frozen-forever-nested.pl
    python3 t/models/clo.py 3453 > t/3453-fault-clo-frozen-forever-nested.expected
    python3 t/models/clo.py --program 3454 > t/3454-fault-clo-reference-added.pl
    python3 t/models/clo.py 3454 > t/3454-fault-clo-reference-added.expected
    python3 t/models/clo.py --program 3455 > t/3455-fault-clo-reference-negated.pl
    python3 t/models/clo.py 3455 > t/3455-fault-clo-reference-negated.expected
    python3 t/models/clo.py --program 3456 > t/3456-fault-clo-reference-compared.pl
    python3 t/models/clo.py 3456 > t/3456-fault-clo-reference-compared.expected
    python3 t/models/clo.py --program 3457 > t/3457-fault-clo-reference-compared-to-a-number.pl
    python3 t/models/clo.py 3457 > t/3457-fault-clo-reference-compared-to-a-number.expected
    python3 t/models/clo.py --program 3458 > t/3458-fault-clo-reference-stepped.pl
    python3 t/models/clo.py 3458 > t/3458-fault-clo-reference-stepped.expected
    python3 t/models/clo.py --program 3459 > t/3459-fault-clo-reference-multiplied.pl
    python3 t/models/clo.py 3459 > t/3459-fault-clo-reference-multiplied.expected
    python3 t/models/clo.py --program 3460 > t/3460-fault-clo-reference-joined.pl
    python3 t/models/clo.py 3460 > t/3460-fault-clo-reference-joined.expected
    python3 t/models/clo.py --program 3461 > t/3461-fault-clo-reference-said.pl
    python3 t/models/clo.py 3461 > t/3461-fault-clo-reference-said.expected
    python3 t/models/clo.py --program 3462 > t/3462-fault-clo-reference-interpolated.pl
    python3 t/models/clo.py 3462 > t/3462-fault-clo-reference-interpolated.expected
    python3 t/models/clo.py --program 3463 > t/3463-fault-clo-reference-compared-as-a-string.pl
    python3 t/models/clo.py 3463 > t/3463-fault-clo-reference-compared-as-a-string.expected
    python3 t/models/clo.py --program 3464 > t/3464-fault-clo-reference-a-key.pl
    python3 t/models/clo.py 3464 > t/3464-fault-clo-reference-a-key.expected
    python3 t/models/clo.py --program 3465 > t/3465-fault-clo-reference-length.pl
    python3 t/models/clo.py 3465 > t/3465-fault-clo-reference-length.expected
    python3 t/models/clo.py --program 3466 > t/3466-fault-clo-reference-in-join.pl
    python3 t/models/clo.py 3466 > t/3466-fault-clo-reference-in-join.expected
    python3 t/models/clo.py --program 3467 > t/3467-fault-clo-reference-sorted.pl
    python3 t/models/clo.py 3467 > t/3467-fault-clo-reference-sorted.expected
    python3 t/models/clo.py --program 3468 > t/3468-fault-clo-reference-repeated.pl
    python3 t/models/clo.py 3468 > t/3468-fault-clo-reference-repeated.expected
    python3 t/models/clo.py --program 3469 > t/3469-fault-clo-reference-formatted.pl
    python3 t/models/clo.py 3469 > t/3469-fault-clo-reference-formatted.expected
    python3 t/models/clo.py --program 3470 > t/3470-fault-clo-reference-died-among-others.pl
    python3 t/models/clo.py 3470 > t/3470-fault-clo-reference-died-among-others.expected
    python3 t/models/clo.py --program 3471 > t/3471-fault-clo-reference-warned.pl
    python3 t/models/clo.py 3471 > t/3471-fault-clo-reference-warned.expected
    python3 t/models/clo.py --program 3472 > t/3472-fault-clo-reference-uc.pl
    python3 t/models/clo.py 3472 > t/3472-fault-clo-reference-uc.expected
    python3 t/models/clo.py --program 3473 > t/3473-fault-clo-reference-an-index.pl
    python3 t/models/clo.py 3473 > t/3473-fault-clo-reference-an-index.expected
    python3 t/models/clo.py --program 3474 > t/3474-fault-clo-reference-died-uncaught.pl
    python3 t/models/clo.py 3474 > t/3474-fault-clo-reference-died-uncaught.expected
    python3 t/models/clo.py --program 3475 > t/3475-fault-clo-recursion-too-deep.pl
    python3 t/models/clo.py 3475 > t/3475-fault-clo-recursion-too-deep.expected
"""

import sys

UNDEF_REF = 'undef where a reference is wanted'
NOT_SUB = 'not a reference to a sub'
NOT_ARRAY = 'not a reference to an array'
NOT_HASH = 'not a reference to a hash'
NOT_SCALAR = 'not a reference to a scalar'
STRING = 'a reference where a string is wanted'
NUMBER = 'a reference where a number is wanted'
FROZEN = 'an array was changed while a foreach is over it'
HFROZEN = 'a hash was changed while a foreach is over it'
LISTED = 'an anonymous sub returned a list where one value is wanted'
NO_VALUE = 'an anonymous sub has no value: it does not end in a return or an expression'

class Cell:
    def __init__(self, v=None):
        self.v = v

class Prog:
    def __init__(self):
        self.lines = []
        self.out = []
        self.subs = []

    def say(self, text, printed):
        self.lines.append(text)
        self.out.append(printed)

    def block(self, f):
        self.lines.append('{')
        f(self)
        self.lines.append('}')

def case_counters(p):
    def counters(p):
        p.subs += ['sub counter($start) {', '    my $n = $start;', '    return sub { return $n++ };', '}']
        # Each call of `counter` is a new `$n`, which its closure holds.
        def counter(start):
            n = Cell(start)
            def f():
                v = n.v
                n.v += 1
                return v
            return f
        c, d = counter(1), counter(10)
        p.lines += ['my $c = counter(1);', 'my $d = counter(10);']
        got = [c(), c(), d(), c(), d()]
        p.say('say(join(",", $c->(), $c->(), $d->(), $c->(), $d->()));', ','.join(map(str, got)))
    p.block(counters)
    def shared(p):
        # Two closures over one variable share it, and see a store from
        # outside made after they were.
        x = Cell(1)
        p.lines += ['my $x = 1;', 'my $get = sub { $x };', 'my $set = sub ($v) { $x = $v; return };']
        p.say('say($get->());', str(x.v))
        x.v = 5
        p.lines.append('$set->(5);')
        p.say('say($get->(), $x);', f'{x.v}{x.v}')
        x.v = 7
        p.lines.append('$x = 7;')
        p.say('say($get->());', str(x.v))
        p.lines.append('$x .= "a";')
        x.v = f'{x.v}a'
        p.say('say($get->());', x.v)
        # A closure over an array and a hash holds the container itself.
        a, h = [1], {'k': 'v'}
        p.lines += ['my @a = (1);', 'my %h = (k => "v");', 'my $push = sub ($e) { push @a, $e; return scalar(@a) };', 'my $put = sub ($k, $v) { $h{$k} = $v; return };']
        a.append(2)
        p.say('say($push->(2));', str(len(a)))
        a.append(3)
        p.lines.append('$push->(3);')
        h['j'] = 'w'
        p.lines.append('$put->("j", "w");')
        p.say('say("@a ", join(",", map { "$_=$h{$_}" } sort keys %h));', ' '.join(map(str, a)) + ' ' + ','.join(f'{k}={h[k]}' for k in sorted(h)))
        p.lines.append('@a = (9);')
        p.say('say($push->(8), " @a");', '2 9 8')
    p.block(shared)
    def nested(p):
        p.lines += ['my $add = sub ($x) { return sub ($y) { return sub ($z) { $x + $y + $z } } };']
        p.say('say($add->(1)->(2)->(3), $add->(10)(20)(30));', f'{1 + 2 + 3}{10 + 20 + 30}')
        # The inner sub uses the outer's parameter and its own: each call
        # of the outer a new one.
        p.lines += ['my $mk = sub ($base) { my $count = 0; return sub ($inc) { $count += $inc; return $base . ":" . $count } };', 'my $p = $mk->("p");', 'my $q = $mk->("q");']
        pc, qc = Cell(0), Cell(0)
        out = []
        for f, base, inc in ((pc, 'p', 1), (pc, 'p', 2), (qc, 'q', 5), (pc, 'p', 3)):
            f.v += inc
            out.append(f'{base}:{f.v}')
        p.say('say(join(",", $p->(1), $p->(2), $q->(5), $p->(3)));', ','.join(out))
        # A parameter's own closure in a default sees the parameter after
        # it is set (D166).
        p.subs += ['sub later($x, $f = sub { $x }) {', '    $x = $x * 10;', '    return $f->();', '}']
        p.say('say(later(4), later(5, sub { "given" }));', '40given')
        # A sub with no signature takes any arguments and sees none (D105).
        p.lines += ['my $any = sub { "any" };']
        p.say('say($any->(), $any->(1, 2, 3));', 'anyany')
    p.block(nested)
    def file_variable(p):
        # A file's variable, used from a sub with no name in a named sub.
        p.subs += ['my $total = 0;', 'sub adder() {', '    return sub ($n) { $total += $n; return $total };', '}']
        p.lines += ['my $a1 = adder();', 'my $a2 = adder();', '$a1->(5);', '$a2->(6);']
        p.say('say($total, " ", $a1 == $a2 ? "same" : "diff");', '11 diff')
    p.block(file_variable)

def case_loops(p):
    def foreach(p):
        p.lines += ['my @s;', 'for my $i (1 .. 3) {', '    push @s, sub { return $i * 10 };', '}']
        p.say('say(join(",", map { $_->() } @s));', ','.join(str(i * 10) for i in (1, 2, 3)))
        p.lines += ['my @t;', 'for (my $i = 0; $i < 3; $i++) {', '    push @t, sub { $i };', '}']
        # One variable for the whole loop: 3 when they are called.
        p.say('say(join(",", map { $_->() } @t));', '3,3,3')
        p.lines += ['my @u;', 'for my $i (1 .. 3) {', '    my $j = $i;', '    push @u, sub { return $j++ };', '}']
        js = [Cell(1), Cell(2), Cell(3)]
        out = []
        for k in (0, 0, 1, 2, 0):
            out.append(js[k].v)
            js[k].v += 1
        p.say('say(join(",", $u[0]->(), $u[0]->(), $u[1]->(), $u[2]->(), $u[0]->()));', ','.join(map(str, out)))
        p.lines += ['my @w;', 'my $n = 0;', 'while ($n < 3) {', '    my $k = $n++;', '    push @w, sub { $k };', '}']
        p.say('say(join(",", map { $_->() } @w));', '0,1,2')
        p.lines += ['my @q = ("a", "b");', 'my @v;', 'while (my $e = shift @q) {', '    push @v, sub { $e };', '}']
        p.say('say(join(",", map { $_->() } @v));', 'a,b')
    p.block(foreach)
    def over_arrays(p):
        # The loop's variable taken from an array is a copy (D162), and the
        # array is frozen for good after: so nothing here stores to it.
        p.lines += ['my @a = (4, 5, 6);', 'my @s;', 'for my $x (@a) {', '    push @s, sub { $x + 1 };', '}']
        p.say('say(join(",", map { $_->() } @s), " ", scalar(@a), " $a[0]");', '5,6,7 3 4')
        # Over the keys of a hash nothing is frozen: they are copies.
        p.lines += ['my %h = (a => 1, b => 2);', 'my @k;', 'for my $key (sort keys %h) {', '    push @k, sub { $key };', '}', 'delete $h{a};', '$h{c} = 3;']
        p.say('say(join(",", map { $_->() } @k), " ", join(",", sort keys %h));', 'a,b b,c')
        # Nested loops: each inner variable its own, the outer's shared by
        # the inner closures of one time round.
        p.lines += ['my @g;', 'for my $i (1 .. 2) {', '    for my $j (1 .. 2) {', '        push @g, sub { "$i$j" };', '    }', '}']
        p.say('say(join(",", map { $_->() } @g));', '11,12,21,22')
        # A closure made in a `map`, over a `my` of the block.
        p.lines += ['my @m = map { my $v = $_ * 2; sub { $v } } (1, 2, 3);']
        p.say('say(join(",", map { $_->() } @m));', '2,4,6')
    p.block(over_arrays)
    def stores(p):
        # A closure made in a loop that stores to a variable outside it.
        p.lines += ['my $sum = 0;', 'my @add;', 'for my $i (1 .. 3) {', '    push @add, sub { $sum += $i; return $sum };', '}']
        s = 0
        out = []
        for i in (3, 1, 2):
            s += i
            out.append(s)
        p.say('say(join(",", $add[2]->(), $add[0]->(), $add[1]->()), " ", $sum);', ','.join(map(str, out)) + f' {s}')
    p.block(stores)

def case_calls(p):
    def dispatch(p):
        p.lines += ['my %d = (add => sub ($x, $y) { $x + $y }, mul => sub ($x, $y) { $x * $y }, neg => sub ($x) { -$x });',
                    'my @fs = (sub { "zero" }, sub ($v) { "one:$v" });']
        p.say('say($d{add}->(2, 3), " ", $d{mul}(4, 5), " ", $d{neg}->(6), " ", $fs[0](), " ", $fs[1]->("x"));', '5 20 -6 zero one:x')
        p.lines += ['my $t = {ops => [sub ($n) { $n + 1 }, sub ($n) { $n * 2 }]};']
        p.say('say($t->{ops}[0]->(5), $t->{ops}->[1](5), $t->{ops}[1](5));', '61010')
        p.lines += ['my $mk = sub { return [sub { "in" }] };']
        p.say('say($mk->()[0]->(), $mk->()->[0](), sub { 3 }->());', 'inin3')
    p.block(dispatch)
    def named(p):
        p.subs += ['sub twice($f, $v) {', '    return $f->($f->($v));', '}', 'sub inc($n) {', '    return $n + 1;', '}']
        p.lines += ['my $r = \\&inc;']
        p.say('say(twice($r, 1), twice(\\&inc, 5), " ", ref($r), " ", $r == \\&inc ? "same" : "diff", " ", (\\&inc)->(9));', '37 CODE same 10')
        p.say('say(twice(sub ($x) { $x . "!" }, "a"));', 'a!!')
    p.block(named)
    def identity(p):
        # D161: new each time if it uses an outside variable, else one.
        p.subs += ['my $g = 1;', 'sub plain() {', '    return sub { 1 };', '}', 'sub uses() {', '    return sub { $g };', '}']
        p.lines += ['my @c;', 'my @o;', 'for my $i (1 .. 2) {', '    push @c, sub { 2 };', '    push @o, sub { $i };', '}']
        p.say('say($c[0] == $c[1] ? "same" : "diff", $o[0] == $o[1] ? "same" : "diff", plain() == plain() ? "same" : "diff", uses() == uses() ? "same" : "diff");', 'samediffsamediff')
        p.lines += ['my $f = sub { 1 };', 'my $h = $f;']
        p.say('say($f == $h ? "same" : "diff", $f != sub { 5 } ? "diff" : "same", $f ? "true" : "false", defined($f) ? "d" : "u", ref(sub { }), "|", ref(\\$f));', 'samedifftruedCODE|REF')
    p.block(identity)
    def recursion(p):
        p.lines += ['my $fact = sub ($n) { return $n <= 1 ? 1 : $n * __SUB__->($n - 1) };']
        p.say('say($fact->(10));', str(3628800))
        p.lines += ['my $fib;', '$fib = sub ($n) { return $n < 2 ? $n : $fib->($n - 1) + $fib->($n - 2) };']
        def fib(n):
            return n if n < 2 else fib(n - 1) + fib(n - 2)
        p.say('say($fib->(15));', str(fib(15)))
        p.lines += ['my $walk = sub ($t) { return ref($t) ? join("", map { __SUB__->($_) } $t->@*) : $t };']
        p.say('say($walk->([1, [2, [3, 4]], 5]));', '12345')
    p.block(recursion)
    def context(p):
        p.lines += ['my $list = sub { return (1, 2, 3) };', 'my $one = sub { return 7 };', 'my @l = $list->();', 'my ($first) = $list->();']
        p.say('say(scalar(@l), $first, " ", $one->() + 1, " ", join(",", $list->(), $one->()));', '31 8 1,2,3,7')
        p.lines += ['my $none = sub { return };', 'my @n = ($none->(), 1);', 'my $u = $none->();']
        p.say('say(scalar(@n), defined($u) ? "d" : "u");', '1u')
        p.lines += ['my $sl = sub ($x, @rest) { return scalar(@rest) . $x };', 'my $hs = sub (%o) { return join(",", map { "$_$o{$_}" } sort keys %o) };']
        p.say('say($sl->(1, 2, 3), " ", $hs->(b => 2, a => 1), " ", $sl->(@l));', '21 a1,b2 21')
        p.lines += ['my $dflt = sub ($x, $y = 5, $z //= 6) { return "$x$y$z" };']
        p.say('say($dflt->(1), $dflt->(1, 2), $dflt->(1, 2, undef), $dflt->(1, 2, 3));', '156126126123')
    p.block(context)
    def order(p):
        # The arguments, then what stands before the arrow, then the call
        # (T370); an argument that is a variable is read when the sub
        # copies it.
        p.subs += ['my @log;', 'sub arg($v) {', '    push @log, "arg$v";', '    return $v;', '}', 'sub fn($w) {', '    push @log, "fn$w";', '    return sub ($v) { push @log, "call$v"; return $v };', '}']
        p.lines += ['fn(1)->(arg(2));', 'my $i = 0;', 'my @fs = (sub { "zero" }, sub { "one" });']
        p.say('say("@log ", $fs[$i]->($i = 1));', 'arg2 fn1 call2 one')
        p.lines += ['my $total = 5;', 'my $step = sub { $total += 100; return 1 };']
        p.say('say($total + $step->());', '106')
    p.block(order)

def case_data(p):
    def higher(p):
        p.subs += ['sub apply($f, @l) {', '    return map { $f->($_) } @l;', '}', 'sub compose($f, $g) {', '    return sub ($x) { $f->($g->($x)) };', '}']
        p.say('say(join(",", apply(sub ($x) { $x * $x }, 1, 2, 3)));', '1,4,9')
        p.lines += ['my $h = compose(sub ($x) { $x + 1 }, sub ($x) { $x * 2 });']
        p.say('say($h->(5), compose($h, $h)->(1));', f'{5 * 2 + 1}{((1 * 2 + 1) * 2) + 1}')
        p.lines += ['my $by = sub ($p, $q) { $q <=> $p };', 'my @s = sort { $by->($a, $b) } (3, 1, 2);', 'my $odd = sub ($n) { $n % 2 };', 'my @o = grep { $odd->($_) } (1 .. 6);']
        p.say('say("@s @o");', '3 2 1 1 3 5')
        p.lines += ['my %reg;', 'for my $name ("a", "b") {', '    my $tag = uc($name);', '    $reg{$name} = sub ($v) { "$tag$v" };', '}']
        p.say('say($reg{a}->(1), $reg{b}->(2));', 'A1B2')
    p.block(higher)
    def thrown(p):
        p.lines += ['my $boom = sub ($m) { die "$m\\n" };', 'my $r = "none";', 'try {', '    $boom->("bang");', '}', 'catch ($e) {', '    chomp $e;', '    $r = $e;', '}']
        p.say('say($r);', 'bang')
        p.lines += ['my $safe = sub ($f) { try { return $f->() } catch ($e) { return "caught" } };']
        p.say('say($safe->(sub { 5 }), $safe->(sub { die "x\\n" }));', '5caught')
        p.lines += ['my $code = sub { 1 };', 'try {', '    die $code;', '}', 'catch ($e) {', '    say(ref($e), " ", $e == $code ? "same" : "diff", " ", $e->());', '}']
        p.out.append('CODE same 1')
    p.block(thrown)
    def kept(p):
        # A closure is all that holds what it captured, and a cycle of a
        # closure and its own variable is no matter: perl and here agree
        # on what each prints.
        p.lines += ['my @keep;', 'for my $i (1 .. 3) {', '    my @a = ($i) x $i;', '    push @keep, sub { scalar(@a) . ":" . join("", @a) };', '}']
        p.say('say(join(",", map { $_->() } @keep));', '1:1,2:22,3:333')
        p.lines += ['my $self;', '$self = sub ($n) { return $n ? $self->($n - 1) + 1 : 0 };']
        p.say('say($self->(4));', '4')
    p.block(kept)

SAME = {
    '3400': ('clo-counters-and-sharing', case_counters),
    '3401': ('clo-in-loops', case_loops),
    '3402': ('clo-calls', case_calls),
    '3403': ('clo-in-data', case_data),
}

# ---- the faults: each program says 1, does the one thing, and says 2.

FAULTS = []

def fault(name, lines, message, at=None):
    FAULTS.append((name, lines, message, at))

# A wrong count, after the arguments have run (D72, D164).
fault('count-too-many', ['my $f = sub () { 42 };', 'say($f->(1));'], 'too many arguments for an anonymous sub: got 1, expected 0')
fault('count-too-few', ['my $f = sub ($x, $y) { $x };', '$f->(1);'], 'too few arguments for an anonymous sub: got 1, expected 2')
fault('count-at-least', ['my $f = sub ($x, @r) { $x };', '$f->();'], 'too few arguments for an anonymous sub: got 0, expected at least 1')
fault('count-of-a-named-sub', ['sub one($x) {', '    return $x;', '}', 'my $r = \\&one;', '$r->(1, 2);'], 'too many arguments for one: got 2, expected 1')
fault('odd-arguments', ['my $f = sub (%o) { 1 };', '$f->(1);'], "an odd number of arguments for an anonymous sub's hash")
# Calling what is not a sub's reference (D164).
fault('call-undef', ['my $f;', '$f->();'], UNDEF_REF)
fault('call-missing-element', ['my @fs;', '$fs[3]();'], UNDEF_REF)
fault('call-missing-key', ['my %d;', '$d{add}->(1, 2);'], UNDEF_REF)
fault('call-a-call-giving-undef', ['sub none() {', '    return undef;', '}', 'none()->();'], UNDEF_REF)
fault('call-an-array-reference', ['my $f = [1];', '$f->();'], NOT_SUB)
fault('call-a-hash-reference', ['my $f = {};', '$f->();'], NOT_SUB)
fault('call-a-scalar-reference', ['my $x = 1;', 'my $f = \\$x;', '$f->();'], NOT_SUB)
fault('call-a-number', ['my $f = 5;', '$f->();'], NOT_SUB)
fault('call-a-string', ['my $f = "main::x";', '$f->();'], NOT_SUB)
fault('call-the-result', ['my $f = sub { 1 };', '$f->()->();'], NOT_SUB)
fault('call-after-a-subscript', ['my $f = [[1]];', '$f->[0](1);'], NOT_SUB)
# A sub's reference as anything else (D107).
fault('index-a-sub', ['my $f = sub { 1 };', 'say($f->[0]);'], NOT_ARRAY)
fault('key-a-sub', ['my $f = sub { 1 };', 'say($f->{k});'], NOT_HASH)
fault('scalar-of-a-sub', ['my $f = sub { 1 };', 'say($f->$*);'], NOT_SCALAR)
fault('whole-of-a-sub', ['my $f = sub { 1 };', 'say(scalar($f->@*));'], NOT_ARRAY)
# The caller's context (D18).
fault('list-where-one-value', ['my $f = sub { return (1, 2, 3) };', 'my $c = $f->();'], LISTED, 0)
fault('list-where-one-value-array', ['my @a = (1, 2);', 'my $f = sub { return @a };', 'say($f->() + 1);'], LISTED, 1)
fault('no-value', ['my $f = sub ($x) { if ($x) { return 1; } };', 'my $v = $f->(0);'], NO_VALUE, 0)
fault('nothing-where-one-value', ['my $f = sub { my @l = (1, 2) };', 'my $v = $f->();'], NO_VALUE, 0)
# What a loop froze stays frozen for good once a closure takes its
# variable (D162).
fault('frozen-forever-push', ['my @a = (1, 2);', 'my @s;', 'for my $x (@a) {', '    push @s, sub { $x };', '}', 'push @a, 3;'], FROZEN)
fault('frozen-forever-store', ['my @a = (1, 2);', 'my @s;', 'for my $x (@a) {', '    push @s, sub { $x };', '}', '$a[0] = 9;'], FROZEN)
fault('frozen-forever-assign', ['my @a = (1, 2);', 'my @s;', 'for my $x (@a) {', '    push @s, sub { $x };', '}', '@a = ();'], FROZEN)
fault('frozen-forever-shift', ['my @a = (1, 2);', 'my @s;', 'for my $x (@a) {', '    push @s, sub { $x };', '}', 'shift @a;'], FROZEN)
fault('frozen-forever-in-the-loop', ['my @a = (1, 2);', 'my @s;', 'for my $x (@a) {', '    push @s, sub { $x };', '    $a[1] = 0;', '}'], FROZEN, 4)
fault('frozen-forever-values', ['my %h = (a => 1);', 'my @s;', 'for my $v (sort values %h) {', '    push @s, sub { $v };', '}', '$h{a} = 9;'], HFROZEN)
fault('frozen-forever-delete', ['my %h = (a => 1);', 'my @s;', 'for my $v (sort values %h) {', '    push @s, sub { $v };', '}', 'delete $h{a};'], HFROZEN)
fault('frozen-forever-through-a-reference', ['my %h = (l => [1, 2]);', 'my $r = $h{l};', 'my @s;', 'for my $x ($h{l}->@*) {', '    push @s, sub { $x };', '}', 'push $r->@*, 3;'], FROZEN)
fault('frozen-forever-from-a-sub', ['my @a = (1);', 'sub more() {', '    push @a, 2;', '    return;', '}', 'my @s;', 'for my $x (@a) {', '    push @s, sub { $x };', '}', 'more();'], FROZEN, 2)
fault('frozen-forever-nested', ['my @a = (1, 2);', 'my @s;', 'for my $x (@a) {', '    push @s, sub { sub { $x } };', '}', '$a[0] = 3;'], FROZEN)
# A sub's reference where a number or a string is wanted (D112).
for name, code, message in (
        ('added', 'say($f + 1);', NUMBER), ('negated', 'say(-$f);', NUMBER), ('compared', 'say($f < 1 ? "y" : "n");', NUMBER),
        ('compared-to-a-number', 'say($f == 1 ? "y" : "n");', NUMBER), ('stepped', '$f++;', NUMBER), ('multiplied', 'say(2 * $f);', NUMBER),
        ('joined', 'say($f . "x");', STRING), ('said', 'say($f);', STRING), ('interpolated', 'say("f=$f");', STRING),
        ('compared-as-a-string', 'say($f eq "x" ? "y" : "n");', STRING), ('a-key', 'my %h = ($f => 1);', STRING),
        ('length', 'say(length($f));', STRING), ('in-join', 'say(join(",", $f, 1));', STRING),
        ('sorted', 'my @l = ($f, sub { 2 });\nmy @s = sort @l;', STRING), ('repeated', 'say($f x 2);', STRING),
        ('formatted', 'say(sprintf("%s", $f));', STRING), ('died-among-others', 'die "x", $f;', STRING),
        ('warned', 'warn $f;', STRING), ('uc', 'say(uc($f));', STRING), ('an-index', 'my @a = (1);\nsay($a[$f]);', NUMBER)):
    fault(f'reference-{name}', ['my $f = sub { 1 };'] + code.split('\n'), message)
fault('reference-died-uncaught', ['die sub { 1 };'], STRING)
# A loop that only the fault ends is counted by something the fault
# doesn't touch (T131): the depth of a call through a reference.
fault('recursion-too-deep', ["no warnings 'recursion';", 'my $deep = sub ($n) { return $n > 50000 ? $n : __SUB__->($n + 1) };', '$deep->(0);'], 'recursion too deep', 1)

def commands():
    out = []
    for number, (name, _) in SAME.items():
        out.append(f'    python3 t/models/clo.py --program {number} > t/{number}-{name}.pl')
        out.append(f'    python3 t/models/clo.py {number} > t/{number}-{name}.expected')
    for n, (name, _, _, _) in enumerate(FAULTS):
        number = 3420 + n
        out.append(f'    python3 t/models/clo.py --program {number} > t/{number}-fault-clo-{name}.pl')
        out.append(f'    python3 t/models/clo.py {number} > t/{number}-fault-clo-{name}.expected')
    return '\n'.join(out) + '\n'

HEAD = '# model: t/models/clo.py\nuse v5.42;\n'

def main(argv):
    if argv == ['--commands']:
        sys.stdout.write(commands())
        return
    assert commands() in __doc__, 'the commands in the docstring are not the tests: python3 t/models/clo.py --commands'
    want_program = argv[0] == '--program'
    number = argv[-1]
    if number in SAME:
        name, case = SAME[number]
        p = Prog()
        case(p)
        indent = 0
        body = []
        for line in p.subs + p.lines:
            for l in line.split('\n'):
                t = l.strip()
                if t.startswith('}'):
                    indent -= 1
                body.append('    ' * indent + t)
                if t.endswith('{'):
                    indent += 1
        sys.stdout.write(HEAD + '\n'.join(body) + '\n' if want_program else '\n'.join(p.out) + '\n')
        return
    n = int(number) - 3420
    name, lines, message, at = FAULTS[n]
    # (A pragma goes at the top, before the first `say`: the lines keep
    # their numbers.)
    pragma = lines[0] + '\n' if lines[0].startswith('no warnings') else ''
    rest = lines[1:] if pragma else lines
    program = '# kind: fault\n' + HEAD + pragma + 'say(1);\n' + '\n'.join(rest) + '\nsay(2);\n'
    if want_program:
        sys.stdout.write(program)
        return
    # The line of the statement that faults: the last of `lines`, or the
    # one `at` says (a sub's own, for what its body does).
    line = 5 + (at if at is not None else len(lines) - 1)
    sys.stdout.write(f'1\nfault: {message} at t/{number}-fault-clo-{name}.pl line {line}.\nexit: 1\n')

if __name__ == '__main__':
    main(sys.argv[1:])
