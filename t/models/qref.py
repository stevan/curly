#!/usr/bin/env python3
"""t/2400 to t/2403, and the faults from t/2420: references in a string
(step 13d; D107, D111, D112, D114, T247, T253).

The definition, which is all this file knows of the language:

  In double quotes, `qq` and a heredoc, after a scalar variable, or an
  element of a named array or hash, a chain of subscripts, each after an
  arrow, or hard after the subscript before it with the arrow left out:
  `$r->[0]`, `$r->{k}`, `$a[0][1]`, `$h{k}{w}`, `$r->[1]->[2][0]`. An
  index is a whole number or a scalar variable (D91), a key a word or a
  scalar variable (D99). After the chain, if it comes, one postfix form:
  `->@*`, the array's values joined with one space; `->$#*`, its last
  index; `->$*`, the scalar; `->@[...]`, a slice, its indexes as an
  array's slice in a string takes them. In braces, `@{ CHAIN }`, `$#{
  CHAIN }` and `${ CHAIN }`, CHAIN a scalar variable with or without
  subscripts, blanks round it. What stands after the chain that is not
  `[`, `{`, or an arrow before one of `[ { @ $` is text.

  Each piece is made a string where it stands, as `.` makes one. Reading
  through undef, or through an element or a key that is not there, is a
  fault, `undef where a reference is wanted`; through anything else that
  is not the reference wanted, `not a reference to an array` (`to a
  hash`, `to a scalar`). An undef made a string is `undef where a string
  is wanted`; a reference, `a reference where a string is wanted`.

The model is Python: a reference to an array is a list, to a hash a dict,
to a scalar a `Cell`; a string is what perl prints of the value. perl is
the second derivation: t/checks.py oracle holds every .expected of a test
without a `kind:` to what perl 5.42 prints, and each fault test's output
to the start of it.

2400 chains in double quotes, every head and depth, 2401 the whole
container, the scalar and the slice, 2402 the same in `qq` and heredocs,
2403 a string is a value made where it stands. 2420 on each fault once.

Every command that writes a file, one a line (t/checks.py runs them all):

    python3 t/models/qref.py --program 2400 > t/2400-qref-chains.pl
    python3 t/models/qref.py 2400 > t/2400-qref-chains.expected
    python3 t/models/qref.py --program 2401 > t/2401-qref-whole-scalar-and-slice.pl
    python3 t/models/qref.py 2401 > t/2401-qref-whole-scalar-and-slice.expected
    python3 t/models/qref.py --program 2402 > t/2402-qref-qq-and-heredocs.pl
    python3 t/models/qref.py 2402 > t/2402-qref-qq-and-heredocs.expected
    python3 t/models/qref.py --program 2403 > t/2403-qref-made-where-it-stands.pl
    python3 t/models/qref.py 2403 > t/2403-qref-made-where-it-stands.expected
    python3 t/models/qref.py --program 2420 > t/2420-fault-qref-read-undef.pl
    python3 t/models/qref.py 2420 > t/2420-fault-qref-read-undef.expected
    python3 t/models/qref.py --program 2421 > t/2421-fault-qref-read-undef-key.pl
    python3 t/models/qref.py 2421 > t/2421-fault-qref-read-undef-key.expected
    python3 t/models/qref.py --program 2422 > t/2422-fault-qref-read-missing-element.pl
    python3 t/models/qref.py 2422 > t/2422-fault-qref-read-missing-element.expected
    python3 t/models/qref.py --program 2423 > t/2423-fault-qref-read-missing-key.pl
    python3 t/models/qref.py 2423 > t/2423-fault-qref-read-missing-key.expected
    python3 t/models/qref.py --program 2424 > t/2424-fault-qref-read-missing-named-element.pl
    python3 t/models/qref.py 2424 > t/2424-fault-qref-read-missing-named-element.expected
    python3 t/models/qref.py --program 2425 > t/2425-fault-qref-read-missing-named-key.pl
    python3 t/models/qref.py 2425 > t/2425-fault-qref-read-missing-named-key.expected
    python3 t/models/qref.py --program 2426 > t/2426-fault-qref-whole-of-undef.pl
    python3 t/models/qref.py 2426 > t/2426-fault-qref-whole-of-undef.expected
    python3 t/models/qref.py --program 2427 > t/2427-fault-qref-postfix-whole-of-undef.pl
    python3 t/models/qref.py 2427 > t/2427-fault-qref-postfix-whole-of-undef.expected
    python3 t/models/qref.py --program 2428 > t/2428-fault-qref-last-index-of-undef.pl
    python3 t/models/qref.py 2428 > t/2428-fault-qref-last-index-of-undef.expected
    python3 t/models/qref.py --program 2429 > t/2429-fault-qref-postfix-last-index-of-undef.pl
    python3 t/models/qref.py 2429 > t/2429-fault-qref-postfix-last-index-of-undef.expected
    python3 t/models/qref.py --program 2430 > t/2430-fault-qref-scalar-of-undef.pl
    python3 t/models/qref.py 2430 > t/2430-fault-qref-scalar-of-undef.expected
    python3 t/models/qref.py --program 2431 > t/2431-fault-qref-postfix-scalar-of-undef.pl
    python3 t/models/qref.py 2431 > t/2431-fault-qref-postfix-scalar-of-undef.expected
    python3 t/models/qref.py --program 2432 > t/2432-fault-qref-slice-of-undef.pl
    python3 t/models/qref.py 2432 > t/2432-fault-qref-slice-of-undef.expected
    python3 t/models/qref.py --program 2433 > t/2433-fault-qref-whole-of-missing-element.pl
    python3 t/models/qref.py 2433 > t/2433-fault-qref-whole-of-missing-element.expected
    python3 t/models/qref.py --program 2434 > t/2434-fault-qref-index-a-hash.pl
    python3 t/models/qref.py 2434 > t/2434-fault-qref-index-a-hash.expected
    python3 t/models/qref.py --program 2435 > t/2435-fault-qref-key-an-array.pl
    python3 t/models/qref.py 2435 > t/2435-fault-qref-key-an-array.expected
    python3 t/models/qref.py --program 2436 > t/2436-fault-qref-index-a-string.pl
    python3 t/models/qref.py 2436 > t/2436-fault-qref-index-a-string.expected
    python3 t/models/qref.py --program 2437 > t/2437-fault-qref-index-a-number.pl
    python3 t/models/qref.py 2437 > t/2437-fault-qref-index-a-number.expected
    python3 t/models/qref.py --program 2438 > t/2438-fault-qref-key-an-element-string.pl
    python3 t/models/qref.py 2438 > t/2438-fault-qref-key-an-element-string.expected
    python3 t/models/qref.py --program 2439 > t/2439-fault-qref-whole-of-a-hash.pl
    python3 t/models/qref.py 2439 > t/2439-fault-qref-whole-of-a-hash.expected
    python3 t/models/qref.py --program 2440 > t/2440-fault-qref-last-index-of-a-hash.pl
    python3 t/models/qref.py 2440 > t/2440-fault-qref-last-index-of-a-hash.expected
    python3 t/models/qref.py --program 2441 > t/2441-fault-qref-scalar-of-an-array.pl
    python3 t/models/qref.py 2441 > t/2441-fault-qref-scalar-of-an-array.expected
    python3 t/models/qref.py --program 2442 > t/2442-fault-qref-postfix-scalar-of-a-hash.pl
    python3 t/models/qref.py 2442 > t/2442-fault-qref-postfix-scalar-of-a-hash.expected
    python3 t/models/qref.py --program 2443 > t/2443-fault-qref-slice-of-a-hash.pl
    python3 t/models/qref.py 2443 > t/2443-fault-qref-slice-of-a-hash.expected
    python3 t/models/qref.py --program 2444 > t/2444-fault-qref-whole-of-a-scalar-reference.pl
    python3 t/models/qref.py 2444 > t/2444-fault-qref-whole-of-a-scalar-reference.expected
    python3 t/models/qref.py --program 2445 > t/2445-fault-qref-element-undef.pl
    python3 t/models/qref.py 2445 > t/2445-fault-qref-element-undef.expected
    python3 t/models/qref.py --program 2446 > t/2446-fault-qref-element-past-the-end.pl
    python3 t/models/qref.py 2446 > t/2446-fault-qref-element-past-the-end.expected
    python3 t/models/qref.py --program 2447 > t/2447-fault-qref-key-not-there.pl
    python3 t/models/qref.py 2447 > t/2447-fault-qref-key-not-there.expected
    python3 t/models/qref.py --program 2448 > t/2448-fault-qref-scalar-undef.pl
    python3 t/models/qref.py 2448 > t/2448-fault-qref-scalar-undef.expected
    python3 t/models/qref.py --program 2449 > t/2449-fault-qref-whole-holding-undef.pl
    python3 t/models/qref.py 2449 > t/2449-fault-qref-whole-holding-undef.expected
    python3 t/models/qref.py --program 2450 > t/2450-fault-qref-slice-past-the-end.pl
    python3 t/models/qref.py 2450 > t/2450-fault-qref-slice-past-the-end.expected
    python3 t/models/qref.py --program 2451 > t/2451-fault-qref-element-a-reference.pl
    python3 t/models/qref.py 2451 > t/2451-fault-qref-element-a-reference.expected
    python3 t/models/qref.py --program 2452 > t/2452-fault-qref-key-a-reference.pl
    python3 t/models/qref.py 2452 > t/2452-fault-qref-key-a-reference.expected
    python3 t/models/qref.py --program 2453 > t/2453-fault-qref-whole-holding-a-reference.pl
    python3 t/models/qref.py 2453 > t/2453-fault-qref-whole-holding-a-reference.expected
    python3 t/models/qref.py --program 2454 > t/2454-fault-qref-scalar-holding-a-reference.pl
    python3 t/models/qref.py 2454 > t/2454-fault-qref-scalar-holding-a-reference.expected
    python3 t/models/qref.py --program 2455 > t/2455-fault-qref-slice-holding-a-reference.pl
    python3 t/models/qref.py 2455 > t/2455-fault-qref-slice-holding-a-reference.expected
    python3 t/models/qref.py --program 2456 > t/2456-fault-qref-in-qq.pl
    python3 t/models/qref.py 2456 > t/2456-fault-qref-in-qq.expected
    python3 t/models/qref.py --program 2457 > t/2457-fault-qref-in-a-heredoc.pl
    python3 t/models/qref.py 2457 > t/2457-fault-qref-in-a-heredoc.expected
    python3 t/models/qref.py --program 2458 > t/2458-fault-qref-second-piece.pl
    python3 t/models/qref.py 2458 > t/2458-fault-qref-second-piece.expected
"""

import sys


class Cell:
    def __init__(self, v):
        self.v = v


UNDEF_REF = 'undef where a reference is wanted'
NOT_ARRAY = 'not a reference to an array'
NOT_HASH = 'not a reference to a hash'
NOT_SCALAR = 'not a reference to a scalar'
STRING = 'a reference where a string is wanted'
UNDEF_STR = 'undef where a string is wanted'

# ---- what every program declares, in perl and here

DECLARED = [
    'my $i = 1;',
    'my $j = -1;',
    'my $k = "k";',
    'my $w = "w";',
    'my @a = ([1, 2, [3, 4]], {k => "ak", w => [5]}, "a2");',
    'my %h = (k => [6, 7], w => {k => "hk", w => {k => "hkk"}});',
    'my $r = [8, [9, 10, [11]], {k => "rk", w => [12, 13]}];',
    'my $q = {k => "qk", w => [14, {k => "qwk"}], x => {k => [15, 16]}};',
    'my $v = "sv";',
    'my $s = \\$v;',
    'my $n = [\\$v, {k => \\$v}];',
]


def world():
    v = Cell('sv')
    return {
        '@a': [[1, 2, [3, 4]], {'k': 'ak', 'w': [5]}, 'a2'],
        '%h': {'k': [6, 7], 'w': {'k': 'hk', 'w': {'k': 'hkk'}}},
        '$r': [8, [9, 10, [11]], {'k': 'rk', 'w': [12, 13]}],
        '$q': {'k': 'qk', 'w': [14, {'k': 'qwk'}], 'x': {'k': [15, 16]}},
        '$s': v,
        '$n': [v, {'k': v}],
    }


def text(v):
    assert isinstance(v, (int, str)), v
    return str(v)


class Spell:
    """Turns, so that each shape is written every way in time: an index as
    a number or `$i`/`$j`, a key as a word or `$k`/`$w`, the arrow
    between two subscripts written or left out."""
    def __init__(self):
        self.n = 0

    def turn(self, k):
        self.n += 1
        return self.n % k

    def index(self, i, length):
        if i == 1 and self.turn(2):
            return '$i'
        if i == length - 1 and self.turn(2):
            return '$j' if self.turn(2) else '-1'
        return str(i)

    def key(self, k):
        if k in ('k', 'w') and self.turn(2):
            return '$' + k
        return k


def paths(value, depth):
    """Every way down from a container: (subscripts, what it reaches)."""
    out = [((), value)]
    if depth == 0:
        return out
    if isinstance(value, list):
        for i, x in enumerate(value):
            out += [(((i, len(value)),) + p, v) for p, v in paths(x, depth - 1)]
    elif isinstance(value, dict):
        for k in sorted(value):
            out += [((k,) + p, v) for p, v in paths(value[k], depth - 1)]
    return out


def spell(sp, head, subs):
    """A chain as a string writes it: a variable's head takes an arrow, a
    named container's first subscript none."""
    out = head
    for n, s in enumerate(subs):
        arrow = '->' if (n == 0 and head[0] == '$' and head not in ('$a', '$h')) or (n > 0 and sp.turn(2)) else ''
        out += arrow + ('[' + sp.index(*s) + ']' if isinstance(s, tuple) else '{' + sp.key(s) + '}')
    return out


# Text after a chain that perl leaves as text, and so does the language.
AFTER = ['', ' [0]', '->x', '-', '->', '::x', ' {k}', '->%*', '.', ',', '}', ']']


def chains(sp, w):
    """Every chain from every head down to a value that prints."""
    out = []
    for name in ('$r', '$q', '@a', '%h'):
        head = {'@a': '$a', '%h': '$h'}.get(name, name)
        for subs, v in paths(w[name], 4):
            if not subs or isinstance(v, (list, dict, Cell)):
                continue
            if name in ('@a', '%h') and len(subs) == 1:
                continue        # an element of a named container is 11a's and 12b's
            out.append((spell(sp, head, subs), text(v)))
    return out


def containers(sp, w):
    """Every chain from every head to an array, and the head itself."""
    out = []
    for name in ('$r', '$q', '@a', '%h'):
        head = {'@a': '$a', '%h': '$h'}.get(name, name)
        for subs, v in paths(w[name], 3):
            if isinstance(v, list) and (subs or name[0] == '$') and all(not isinstance(x, (list, dict)) for x in v):
                out.append((spell(sp, head, subs), v))
            elif isinstance(v, list) and (subs or name[0] == '$'):
                out.append((spell(sp, head, subs), None))   # holds references: its count alone
    return out


class Prog:
    def __init__(self):
        self.lines = []
        self.out = []

    def say(self, line, printed):
        self.lines.append(line)
        self.out.append(printed)


def case_chains(p):
    sp = Spell()
    w = world()
    for n, (chain, v) in enumerate(chains(sp, w)):
        after = AFTER[n % len(AFTER)]
        p.say(f'say "<{chain}{after}>";', f'<{v}{after}>')
    # two in one string, and one hard after another's end
    found = chains(sp, w)
    for n in range(0, len(found) - 1, 3):
        (c1, v1), (c2, v2) = found[n], found[n + 1]
        p.say(f'say "{c1}{c2}|{c1} {c2}";', f'{v1}{v2}|{v1} {v2}')
    # through a scalar's reference, at the head and on the way
    p.say('say "${$s} ${ $s } $s->$* $n->[0]->$* ${$n->[1]{k}} $n->[1]->{k}->$*.";', 'sv sv sv sv sv sv.')


def case_whole(p):
    sp = Spell()
    w = world()
    for n, (chain, v) in enumerate(containers(sp, w)):
        last = str(len(w_get(w, chain)) - 1)
        p.say(f'say "{chain}->$#* $#{{{chain}}} $#{{ {chain} }}";', f'{last} {last} {last}')
        if v is None:
            continue
        joined = ' '.join(text(x) for x in v)
        p.say(f'say "<{chain}->@*> <@{{{chain}}}> <@{{ {chain} }}>";', f'<{joined}> <{joined}> <{joined}>')
        k = len(v)
        picks = [k - 1, 0] if k > 1 else [0]
        ix = ', '.join(str(x) for x in picks)
        p.say(f'say "<{chain}->@[{ix}]> <{chain}->@[0 .. {k - 1}]> <{chain}->@[$i - 1 .. 0]>";'.replace('$i - 1 .. 0', '0,'),
              f'<{" ".join(text(v[x]) for x in picks)}> <{joined}> <{text(v[0])}>')
    # what perl leaves as text after each form
    p.say('say "@{$r->[1][2]} [0]|@{$r->[1][2]}x|$r->[1][2]->@* [0]|$r->[1][2]->@*x|$r->[1][2]->@*::x|$r->[1][2]->@*->x";',
          '11 [0]|11x|11 [0]|11x|11::x|11->x')
    p.say('say "$#{$r}::x|$r->$#*->x|${$s}::x|$s->$*->x|$s->$*-|$r->[2]{w}->@[1]::x";', '2::x|2->x|sv::x|sv->x|sv-|13::x')
    p.say('say "${$s}x ${ $n->[0] }-$n->[0]->$*";', 'svx sv-sv')
    # an empty array, and an array of one
    p.lines += ['my $e = [];', 'my $one = [7];']
    p.say('say "<@{$e}> <$e->@*> $#{$e} $e->$#* <$one->@*> $one->$#*";', '<> <> -1 -1 <7> 0')


def w_get(w, chain):
    """The container a chain the model wrote reaches, read back."""
    import re
    m = re.match(r'(\$\w+)', chain)
    head = m.group(1)
    v = {'$a': w['@a'], '$h': w['%h']}.get(head, w.get(head))
    for sub in re.findall(r'\[([^\]]*)\]|\{([^}]*)\}', chain[len(head):]):
        idx, key = sub
        if idx != '':
            i = {'$i': 1, '$j': -1}.get(idx)
            v = v[int(idx) if i is None else i]
        else:
            v = v[{'$k': 'k', '$w': 'w'}.get(key, key)]
    return v


def case_quotes(p):
    p.say('say qq{$r->[2]{k} @{$r->[1][2]} $q->{w}[1]{k}};', 'rk 11 qwk')
    p.say('say qq[$r->[1][1] $a[0][2][0]];', '10 3')
    # (Not `->` in `qq<...>`: its `>` ends the string, to perl, T352.)
    p.say('say qq<@{$h{k}} $h{w}{w}{k} $a[1]{w}[0]>;', '6 7 hkk 5')
    p.say('say qq($r->[1]->$#* ${$s});', '2 sv')
    p.lines += ['print <<"END";', '$r->[0] $q->{k}', '@{$r->[2]{w}} $r->[2]{w}->@[1, 0]', '$#{$q->{w}} $s->$*', 'END']
    p.out += ['8 qk', '12 13 13 12', '1 sv']
    p.lines += ['print <<~EOT;', '    $a[1]{w}[0] $h{k}[1]', '      $n->[1]{k}->$*', '    EOT']
    p.out += ['5 7', '  sv']
    p.lines += ["print <<'RAW';", '$r->[0] @{$r}', 'RAW']
    p.out += ['$r->[0] @{$r}']


def case_made(p):
    # Each string is made where it stands (T196, T235): a later part of
    # the list, or a later piece of a concatenation, that stores through
    # the reference changes nothing of it.
    p.lines += ['my $m = [3, [4]];', 'my $g = {k => "a"};']
    p.say('say "$m->[0]", ($m->[0] = 5);', '35')
    p.say('say "<$m->[0]>" . ($m->[0] = 6);', '<5>6')
    p.say('say "@{$m->[1]}-" . push($m->[1]->@*, 9);', '4-2')
    p.say('say "$g->{k}|", ($g->{k} = "b"), "|$g->{k}";', 'a|b|b')
    p.lines += ['sub bump($c) {', '    $c->[0] += 1;', '    return $c->[0];', '}']
    p.say('say "$m->[0]:", bump($m), ":$m->[0]";', '6:7:7')
    p.say('say "$m->[1]->$#*" + bump($m);', '9')
    # a loop over strings walks copies: the block may change what they
    # were made from
    p.lines += ['my @seen;', 'for my $t ("$m->[0]", "@{$m->[1]}", "$#{$m}") {', '    push $m->[1]->@*, 0;', '    $m->[0] = 0;', '    push @seen, $t;', '}']
    p.say('say join("|", @seen), " ", $m->[1]->$#*;', '8|4 9|1 4')
    p.say('say join(",", map { "$m->[1][$_]" } 0 .. 1);', '4,9')
    p.lines += ['my @l = map { $m->[0]++; "$m->[0]" } (1, 2);']
    p.say('say "@l";', '1 2')
    # an element of a reference in a string as a key and in a join
    p.lines += ['my %by = ("$g->{k}" => 1, "$m->[1][0]x" => 2);']
    p.say('say join(",", map { "$_=$by{$_}" } sort keys %by);', '4x=2,b=1')
    # a string made of what a sub's own reference holds
    p.lines += ['sub tag($c) {', '    return "<$c->{k}>";', '}']
    p.say('say tag($g), tag({k => "z"});', '<b><z>')
    # what a later part puts in the variable a string read through
    p.lines += ['my $z = [3];']
    p.say('say "$z->[0]", ($z = [5])->[0];', '35')
    p.lines += ['my @y = ("@{$z}", ($z = [7, 8])->[1]);']
    p.say('say "@y";', '5 8')


SAME = {
    '2400': ('qref-chains', case_chains),
    '2401': ('qref-whole-scalar-and-slice', case_whole),
    '2402': ('qref-qq-and-heredocs', case_quotes),
    '2403': ('qref-made-where-it-stands', case_made),
}

# ---- the faults, each once: (name, lines, message, the line that faults)

FAULTS = []


def fault(name, lines, message, at=None):
    FAULTS.append((name, lines, message, at))


# Reading through undef, or what is not there (D107).
fault('read-undef', ['my $u;', 'say "<$u->[0]>";'], UNDEF_REF)
fault('read-undef-key', ['my $u;', 'say "<$u->{k}>";'], UNDEF_REF)
fault('read-missing-element', ['my $r = [1];', 'say "<$r->[1][0]>";'], UNDEF_REF)
fault('read-missing-key', ['my $r = {};', 'say "<$r->{a}{b}>";'], UNDEF_REF)
fault('read-missing-named-element', ['my @a = (1);', 'say "<$a[3][0]>";'], UNDEF_REF)
fault('read-missing-named-key', ['my %h;', 'say "<$h{a}{b}>";'], UNDEF_REF)
fault('whole-of-undef', ['my $u;', 'say "<@{$u}>";'], UNDEF_REF)
fault('postfix-whole-of-undef', ['my $u;', 'say "<$u->@*>";'], UNDEF_REF)
# perl prints -1 here, and makes $u an array in silence
fault('last-index-of-undef', ['my $u;', 'say "<$#{$u}>";'], UNDEF_REF)
fault('postfix-last-index-of-undef', ['my $u;', 'say "<$u->$#*>";'], UNDEF_REF)
fault('scalar-of-undef', ['my $u;', 'say "<${$u}>";'], UNDEF_REF)
fault('postfix-scalar-of-undef', ['my $u;', 'say "<$u->$*>";'], UNDEF_REF)
fault('slice-of-undef', ['my $u;', 'say "<$u->@[0, 1]>";'], UNDEF_REF)
fault('whole-of-missing-element', ['my $r = [];', 'say "<@{$r->[0]}>";'], UNDEF_REF)
# Through what is not the reference wanted.
fault('index-a-hash', ['my $r = {};', 'say "<$r->[0]>";'], NOT_ARRAY)
fault('key-an-array', ['my $r = [];', 'say "<$r->{k}>";'], NOT_HASH)
fault('index-a-string', ['my $r = "x";', 'say "<$r->[0]>";'], NOT_ARRAY)
fault('index-a-number', ['my $r = [5];', 'say "<$r->[0][0]>";'], NOT_ARRAY)
fault('key-an-element-string', ['my %h = (a => 1);', 'say "<$h{a}{b}>";'], NOT_HASH)
fault('whole-of-a-hash', ['my $r = {};', 'say "<@{$r}>";'], NOT_ARRAY)
fault('last-index-of-a-hash', ['my $r = {};', 'say "<$r->$#*>";'], NOT_ARRAY)
fault('scalar-of-an-array', ['my $r = [];', 'say "<${$r}>";'], NOT_SCALAR)
fault('postfix-scalar-of-a-hash', ['my $r = {};', 'say "<$r->$*>";'], NOT_SCALAR)
fault('slice-of-a-hash', ['my $r = {};', 'say "<$r->@[0]>";'], NOT_ARRAY)
fault('whole-of-a-scalar-reference', ['my $v = 1;', 'my $r = \\$v;', 'say "<$r->@*>";'], NOT_ARRAY)
# What is made a string (D48, D112).
fault('element-undef', ['my $r = [undef];', 'say "<$r->[0]>";'], UNDEF_STR)
fault('element-past-the-end', ['my $r = [1];', 'say "<$r->[1]>";'], UNDEF_STR)
fault('key-not-there', ['my $r = {};', 'say "<$r->{k}>";'], UNDEF_STR)
fault('scalar-undef', ['my $v;', 'my $r = \\$v;', 'say "<${$r}>";'], UNDEF_STR)
fault('whole-holding-undef', ['my $r = [1, undef];', 'say "<@{$r}>";'], UNDEF_STR)
fault('slice-past-the-end', ['my $r = [1];', 'say "<$r->@[0, 1]>";'], UNDEF_STR)
fault('element-a-reference', ['my $r = [[1]];', 'say "<$r->[0]>";'], STRING)
fault('key-a-reference', ['my $r = {k => {}};', 'say "<$r->{k}>";'], STRING)
fault('whole-holding-a-reference', ['my $r = [1, [2]];', 'say "<$r->@*>";'], STRING)
fault('scalar-holding-a-reference', ['my $v = [1];', 'my $r = \\$v;', 'say "<$r->$*>";'], STRING)
fault('slice-holding-a-reference', ['my $r = [1, {}];', 'say "<$r->@[1]>";'], STRING)
fault('in-qq', ['my $u;', 'say qq{<$u->[0]>};'], UNDEF_REF)
fault('in-a-heredoc', ['my $r = {};', 'print <<"END";', '$r->[0]', 'END'], NOT_ARRAY, 1)
fault('second-piece', ['my $r = [1];', 'my $u;', 'say "<$r->[0]$u->[0]>";'], UNDEF_REF)


def commands():
    out = []
    for number, (name, _) in SAME.items():
        out.append(f'    python3 t/models/qref.py --program {number} > t/{number}-{name}.pl')
        out.append(f'    python3 t/models/qref.py {number} > t/{number}-{name}.expected')
    for n, (name, _, _, _) in enumerate(FAULTS):
        number = 2420 + n
        out.append(f'    python3 t/models/qref.py --program {number} > t/{number}-fault-qref-{name}.pl')
        out.append(f'    python3 t/models/qref.py {number} > t/{number}-fault-qref-{name}.expected')
    return '\n'.join(out) + '\n'


HEAD = '# model: t/models/qref.py\nuse v5.42;\n'


def main(argv):
    if argv == ['--commands']:
        sys.stdout.write(commands())
        return
    assert commands() in __doc__, 'the commands in the docstring are not the tests: python3 t/models/qref.py --commands'
    want_program = argv[0] == '--program'
    number = argv[-1]
    if number in SAME:
        name, case = SAME[number]
        p = Prog()
        case(p)
        indent = 0
        body = []
        heredoc = None
        for line in DECLARED + p.lines:
            t = line if heredoc else line.strip()
            if heredoc is not None:
                body.append(line)
                if line.strip() == heredoc:
                    heredoc = None
                continue
            if t.startswith('}'):
                indent -= 1
            body.append('    ' * indent + t)
            if t.endswith('{'):
                indent += 1
            if '<<' in t:
                heredoc = t.split('<<')[1].lstrip('~').strip('";\'')
        sys.stdout.write(HEAD + '\n'.join(body) + '\n' if want_program else '\n'.join(p.out) + '\n')
        return
    n = int(number) - 2420
    name, lines, message, at = FAULTS[n]
    program = '# kind: fault\n' + HEAD + 'say(1);\n' + '\n'.join(lines) + '\nsay(2);\n'
    if want_program:
        sys.stdout.write(program)
        return
    line = 5 + (at if at is not None else len(lines) - 1)
    sys.stdout.write(f'1\nfault: {message} at t/{number}-fault-qref-{name}.pl line {line}.\nexit: 1\n')


if __name__ == '__main__':
    main(sys.argv[1:])
