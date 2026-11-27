#!/usr/bin/env python3
"""t/2200 to t/2203, and the faults from t/2220: references to scalars
(step 13c; D107, D108, D110, D112, D114).

The definition, which is all this file knows of the language:

  \\$x                 a reference to the scalar variable $x (a `my`, a
                      parameter, a catch's variable; not a loop's
                      variable, `$_`, `$a` or `$b`)
  EXPR->$*  ${ EXPR }  the scalar a reference points at

The scalar through a reference stands where a scalar variable may: read,
the target of `=`, of every assigning operator and of `++` and `--`, a
target of a list assignment. `ref` of a reference to a scalar is
`SCALAR`, or `REF` when the scalar holds a reference now. Two references
to one scalar are `==`. **Reading through undef, or through an element
or a key that is not there, is a fault**, `undef where a reference is
wanted`, and through anything else that is not a reference to a scalar
`not a reference to a scalar`. **A store makes the scalar** where the
head is undef or not there, as a store through an element does (T248):
the variable at the head, or an element on the way; not a loop's
variable, `$_`, `$a` or `$b`, which is a fault (T250), nor anything but a
variable or an element (T252). **A `my` that is reached again is a new
variable** to every reference taken (T240); a file's variable is one
from the start (T255). A reference to a scalar where a number or a string
is wanted is a fault, as every reference is (D112).

The model is Python: a scalar whose reference is taken is a `Cell`, and
a reference to it is the cell itself, compared by identity. `show`
prints a value in a form the test's own `show` sub prints too. perl is
the second derivation: t/checks.py oracle holds every .expected of a test
without a `kind:` to what perl 5.42 prints, and each fault test's output
to the start of it.

2200 reads and stores through a reference to a scalar, 2201 what a store
makes, 2202 cells and scopes, 2203 lists, loops and subs. 2220 on each
fault once.

Every command that writes a file, one a line (t/checks.py runs them all):

    python3 t/models/sref.py --program 2200 > t/2200-sref-reads-and-stores.pl
    python3 t/models/sref.py 2200 > t/2200-sref-reads-and-stores.expected
    python3 t/models/sref.py --program 2201 > t/2201-sref-made.pl
    python3 t/models/sref.py 2201 > t/2201-sref-made.expected
    python3 t/models/sref.py --program 2202 > t/2202-sref-cells-and-scopes.pl
    python3 t/models/sref.py 2202 > t/2202-sref-cells-and-scopes.expected
    python3 t/models/sref.py --program 2203 > t/2203-sref-in-lists-loops-and-subs.pl
    python3 t/models/sref.py 2203 > t/2203-sref-in-lists-loops-and-subs.expected
    python3 t/models/sref.py --program 2220 > t/2220-fault-sref-read-undef.pl
    python3 t/models/sref.py 2220 > t/2220-fault-sref-read-undef.expected
    python3 t/models/sref.py --program 2221 > t/2221-fault-sref-read-undef-braces.pl
    python3 t/models/sref.py 2221 > t/2221-fault-sref-read-undef-braces.expected
    python3 t/models/sref.py --program 2222 > t/2222-fault-sref-read-undef-defined.pl
    python3 t/models/sref.py 2222 > t/2222-fault-sref-read-undef-defined.expected
    python3 t/models/sref.py --program 2223 > t/2223-fault-sref-read-undef-tested.pl
    python3 t/models/sref.py 2223 > t/2223-fault-sref-read-undef-tested.expected
    python3 t/models/sref.py --program 2224 > t/2224-fault-sref-read-undef-in-a-list.pl
    python3 t/models/sref.py 2224 > t/2224-fault-sref-read-undef-in-a-list.expected
    python3 t/models/sref.py --program 2225 > t/2225-fault-sref-read-undef-argument.pl
    python3 t/models/sref.py 2225 > t/2225-fault-sref-read-undef-argument.expected
    python3 t/models/sref.py --program 2226 > t/2226-fault-sref-read-undef-in-a-loop.pl
    python3 t/models/sref.py 2226 > t/2226-fault-sref-read-undef-in-a-loop.expected
    python3 t/models/sref.py --program 2227 > t/2227-fault-sref-read-through-missing-index.pl
    python3 t/models/sref.py 2227 > t/2227-fault-sref-read-through-missing-index.expected
    python3 t/models/sref.py --program 2228 > t/2228-fault-sref-read-through-missing-key.pl
    python3 t/models/sref.py 2228 > t/2228-fault-sref-read-through-missing-key.expected
    python3 t/models/sref.py --program 2229 > t/2229-fault-sref-read-through-missing-hop.pl
    python3 t/models/sref.py 2229 > t/2229-fault-sref-read-through-missing-hop.expected
    python3 t/models/sref.py --program 2230 > t/2230-fault-sref-read-a-call-giving-undef.pl
    python3 t/models/sref.py 2230 > t/2230-fault-sref-read-a-call-giving-undef.expected
    python3 t/models/sref.py --program 2231 > t/2231-fault-sref-read-an-array-reference.pl
    python3 t/models/sref.py 2231 > t/2231-fault-sref-read-an-array-reference.expected
    python3 t/models/sref.py --program 2232 > t/2232-fault-sref-read-a-hash-reference.pl
    python3 t/models/sref.py 2232 > t/2232-fault-sref-read-a-hash-reference.expected
    python3 t/models/sref.py --program 2233 > t/2233-fault-sref-read-a-number.pl
    python3 t/models/sref.py 2233 > t/2233-fault-sref-read-a-number.expected
    python3 t/models/sref.py --program 2234 > t/2234-fault-sref-read-a-string.pl
    python3 t/models/sref.py 2234 > t/2234-fault-sref-read-a-string.expected
    python3 t/models/sref.py --program 2235 > t/2235-fault-sref-read-an-element-as-a-scalar.pl
    python3 t/models/sref.py 2235 > t/2235-fault-sref-read-an-element-as-a-scalar.expected
    python3 t/models/sref.py --program 2236 > t/2236-fault-sref-read-a-scalar-as-an-array.pl
    python3 t/models/sref.py 2236 > t/2236-fault-sref-read-a-scalar-as-an-array.expected
    python3 t/models/sref.py --program 2237 > t/2237-fault-sref-read-a-scalar-as-a-hash.pl
    python3 t/models/sref.py 2237 > t/2237-fault-sref-read-a-scalar-as-a-hash.expected
    python3 t/models/sref.py --program 2238 > t/2238-fault-sref-store-through-an-array-reference.pl
    python3 t/models/sref.py 2238 > t/2238-fault-sref-store-through-an-array-reference.expected
    python3 t/models/sref.py --program 2239 > t/2239-fault-sref-store-through-a-hash-reference.pl
    python3 t/models/sref.py 2239 > t/2239-fault-sref-store-through-a-hash-reference.expected
    python3 t/models/sref.py --program 2240 > t/2240-fault-sref-store-through-empty-string.pl
    python3 t/models/sref.py 2240 > t/2240-fault-sref-store-through-empty-string.expected
    python3 t/models/sref.py --program 2241 > t/2241-fault-sref-store-through-false.pl
    python3 t/models/sref.py 2241 > t/2241-fault-sref-store-through-false.expected
    python3 t/models/sref.py --program 2242 > t/2242-fault-sref-step-through-a-number.pl
    python3 t/models/sref.py 2242 > t/2242-fault-sref-step-through-a-number.expected
    python3 t/models/sref.py --program 2243 > t/2243-fault-sref-hop-of-the-other-kind.pl
    python3 t/models/sref.py 2243 > t/2243-fault-sref-hop-of-the-other-kind.expected
    python3 t/models/sref.py --program 2244 > t/2244-fault-sref-push-through-a-scalar-reference.pl
    python3 t/models/sref.py 2244 > t/2244-fault-sref-push-through-a-scalar-reference.expected
    python3 t/models/sref.py --program 2245 > t/2245-fault-sref-store-through-a-call.pl
    python3 t/models/sref.py 2245 > t/2245-fault-sref-store-through-a-call.expected
    python3 t/models/sref.py --program 2246 > t/2246-fault-sref-store-through-or.pl
    python3 t/models/sref.py 2246 > t/2246-fault-sref-store-through-or.expected
    python3 t/models/sref.py --program 2247 > t/2247-fault-sref-store-through-a-choice.pl
    python3 t/models/sref.py 2247 > t/2247-fault-sref-store-through-a-choice.expected
    python3 t/models/sref.py --program 2248 > t/2248-fault-sref-store-through-loop-variable.pl
    python3 t/models/sref.py 2248 > t/2248-fault-sref-store-through-loop-variable.expected
    python3 t/models/sref.py --program 2249 > t/2249-fault-sref-step-through-it.pl
    python3 t/models/sref.py 2249 > t/2249-fault-sref-step-through-it.expected
    python3 t/models/sref.py --program 2250 > t/2250-fault-sref-store-through-it-in-a-map.pl
    python3 t/models/sref.py 2250 > t/2250-fault-sref-store-through-it-in-a-map.expected
    python3 t/models/sref.py --program 2251 > t/2251-fault-sref-reference-added.pl
    python3 t/models/sref.py 2251 > t/2251-fault-sref-reference-added.expected
    python3 t/models/sref.py --program 2252 > t/2252-fault-sref-reference-negated.pl
    python3 t/models/sref.py 2252 > t/2252-fault-sref-reference-negated.expected
    python3 t/models/sref.py --program 2253 > t/2253-fault-sref-reference-compared.pl
    python3 t/models/sref.py 2253 > t/2253-fault-sref-reference-compared.expected
    python3 t/models/sref.py --program 2254 > t/2254-fault-sref-reference-compared-to-a-number.pl
    python3 t/models/sref.py 2254 > t/2254-fault-sref-reference-compared-to-a-number.expected
    python3 t/models/sref.py --program 2255 > t/2255-fault-sref-reference-stepped.pl
    python3 t/models/sref.py 2255 > t/2255-fault-sref-reference-stepped.expected
    python3 t/models/sref.py --program 2256 > t/2256-fault-sref-reference-joined.pl
    python3 t/models/sref.py 2256 > t/2256-fault-sref-reference-joined.expected
    python3 t/models/sref.py --program 2257 > t/2257-fault-sref-reference-said.pl
    python3 t/models/sref.py 2257 > t/2257-fault-sref-reference-said.expected
    python3 t/models/sref.py --program 2258 > t/2258-fault-sref-reference-interpolated.pl
    python3 t/models/sref.py 2258 > t/2258-fault-sref-reference-interpolated.expected
    python3 t/models/sref.py --program 2259 > t/2259-fault-sref-reference-compared-as-a-string.pl
    python3 t/models/sref.py 2259 > t/2259-fault-sref-reference-compared-as-a-string.expected
    python3 t/models/sref.py --program 2260 > t/2260-fault-sref-reference-a-key.pl
    python3 t/models/sref.py 2260 > t/2260-fault-sref-reference-a-key.expected
    python3 t/models/sref.py --program 2261 > t/2261-fault-sref-reference-length.pl
    python3 t/models/sref.py 2261 > t/2261-fault-sref-reference-length.expected
    python3 t/models/sref.py --program 2262 > t/2262-fault-sref-reference-in-join.pl
    python3 t/models/sref.py 2262 > t/2262-fault-sref-reference-in-join.expected
    python3 t/models/sref.py --program 2263 > t/2263-fault-sref-reference-sorted.pl
    python3 t/models/sref.py 2263 > t/2263-fault-sref-reference-sorted.expected
    python3 t/models/sref.py --program 2264 > t/2264-fault-sref-reference-repeated.pl
    python3 t/models/sref.py 2264 > t/2264-fault-sref-reference-repeated.expected
    python3 t/models/sref.py --program 2265 > t/2265-fault-sref-reference-formatted.pl
    python3 t/models/sref.py 2265 > t/2265-fault-sref-reference-formatted.expected
    python3 t/models/sref.py --program 2266 > t/2266-fault-sref-reference-died-among-others.pl
    python3 t/models/sref.py 2266 > t/2266-fault-sref-reference-died-among-others.expected
    python3 t/models/sref.py --program 2267 > t/2267-fault-sref-reference-warned.pl
    python3 t/models/sref.py 2267 > t/2267-fault-sref-reference-warned.expected
    python3 t/models/sref.py --program 2268 > t/2268-fault-sref-reference-died-uncaught.pl
    python3 t/models/sref.py 2268 > t/2268-fault-sref-reference-died-uncaught.expected
    python3 t/models/sref.py --program 2269 > t/2269-fault-sref-frozen-on-the-way.pl
    python3 t/models/sref.py 2269 > t/2269-fault-sref-frozen-on-the-way.expected
    python3 t/models/sref.py --program 2270 > t/2270-fault-sref-frozen-on-a-chain.pl
    python3 t/models/sref.py 2270 > t/2270-fault-sref-frozen-on-a-chain.expected
"""

import sys

UNDEF_REF = 'undef where a reference is wanted'
NOT_SCALAR = 'not a reference to a scalar'
NOT_ARRAY = 'not a reference to an array'
NOT_HASH = 'not a reference to a hash'
STRING = 'a reference where a string is wanted'
NUMBER = 'a reference where a number is wanted'
FROZEN = 'an array was changed while a foreach is over it'
HFROZEN = 'a hash was changed while a foreach is over it'

# ---- values: an int, a str, None for undef, a Cell (a reference to a
# scalar), a list or a dict (a reference to an array or a hash).

class Cell:
    def __init__(self, v=None):
        self.v = v

def show(v):
    """What the test's `show` sub prints of a value."""
    if v is None:
        return 'u'
    if isinstance(v, Cell):
        return '\\' + show(v.v)
    if isinstance(v, list):
        return '[' + ','.join(show(x) for x in v) + ']'
    if isinstance(v, dict):
        return '{' + ','.join(f'{k}:{show(v[k])}' for k in sorted(v)) + '}'
    return str(v)

SHOW = [
    'sub show($v) {',
    '    return "u" unless defined $v;',
    '    return "\\\\" . show($v->$*) if ref($v) eq "SCALAR" || ref($v) eq "REF";',
    '    return "[" . join(",", map { show($_) } $v->@*) . "]" if ref($v) eq "ARRAY";',
    '    return "{" . join(",", map { $_ . ":" . show($v->{$_}) } sort keys $v->%*) . "}" if ref($v) eq "HASH";',
    '    return $v;',
    '}',
]

def ref(v):
    if isinstance(v, Cell):
        return 'REF' if isinstance(v.v, (Cell, list, dict)) else 'SCALAR'
    if isinstance(v, list):
        return 'ARRAY'
    if isinstance(v, dict):
        return 'HASH'
    return ''

def lit(v):
    if v is None:
        return 'undef'
    if isinstance(v, int):
        return str(v)
    return f'"{v}"'

def true(v):
    return not (v is None or v == 0 or v == '' or v == '0')

def num(v):
    return 0 if v is None else int(v)

def text(v):
    return '' if v is None else str(v)

# The assigning operators, each with what it makes of what the scalar
# holds and the right side: on whole numbers and strings that perl takes
# in silence, an undef on the left only where perl takes one (D56).
OPS = {
    '+=': lambda a, b: num(a) + b,
    '-=': lambda a, b: num(a) - b,
    '*=': lambda a, b: a * b,
    '%=': lambda a, b: a % b,
    '**=': lambda a, b: a ** b,
    '.=': lambda a, b: text(a) + str(b),
    'x=': lambda a, b: str(a) * b,
    '||=': lambda a, b: a if true(a) else b,
    '&&=': lambda a, b: b if true(a) else a,
    '//=': lambda a, b: a if a is not None else b,
}

# ---- a program and what it prints

class Prog:
    def __init__(self):
        self.lines = []
        self.out = []
        self.subs = []
        self.n = 0

    def say(self, text, printed):
        self.lines.append(text)
        self.out.append(printed)

    def block(self, f):
        self.lines.append('{')
        f(self)
        self.lines.append('}')

    def through(self, head):
        """`HEAD->$*` or `${ HEAD }`, by turns."""
        self.n += 1
        return f'{head}->$*' if self.n % 2 else f'${{ {head} }}'

def case_reads(p):
    def one(p, start, rhs):
        x = Cell(start)
        p.lines += [f'my $x = {lit(start)};', 'my $r = \\$x;']
        p.say(f'say(ref($r), " ", show({p.through("$r")}), " ", show({p.through("$r")}));', f'{ref(x)} {show(x.v)} {show(x.v)}')
        for op, b in rhs:
            x.v = OPS[op](x.v, b)
            p.lines.append(f'{p.through("$r")} {op} {lit(b)};')
            p.say('say(show($x));', show(x.v))
        x.v = 7
        p.lines.append('$x = 7;')
        p.say(f'say({p.through("$r")});', '7')
        p.lines.append(f'{p.through("$r")} = "s";')
        x.v = 's'
        p.say('say($x, ref($r));', 'sSCALAR')
    p.block(lambda p: one(p, 5, [('+=', 3), ('-=', 1), ('*=', 4), ('%=', 5), ('**=', 3), ('.=', 'z'), ('x=', 2)]))
    p.block(lambda p: one(p, 'ab', [('.=', 'c'), ('x=', 3), ('||=', 'no'), ('&&=', 'yes'), ('//=', 'no')]))
    p.block(lambda p: one(p, 0, [('||=', 4), ('&&=', 0), ('&&=', 9), ('//=', 6), ('+=', 2)]))
    p.block(lambda p: one(p, None, [('//=', 3), ('.=', 'x')]))
    p.block(lambda p: one(p, None, [('+=', 2), ('-=', 5)]))
    def steps(p):
        x = Cell(5)
        p.lines += ['my $x = 5;', 'my $r = \\$x;']
        for before, op in ((False, '++'), (True, '++'), (False, '--'), (True, '--')):
            old = x.v
            x.v = old + (1 if op == '++' else -1)
            got = x.v if before else old
            expr = f'{op}{p.through("$r")}' if before else f'{p.through("$r")}{op}'
            p.lines.append(f'my $v{p.n} = {expr};')
            p.say(f'say($v{p.n}, " ", $x);', f'{got} {x.v}')
        p.lines += ['my $u;', 'my $s = \\$u;', '$s->$*++;']
        p.say('say($u);', '1')
        p.lines += ['my $w;', 'my $t = \\$w;', '--${ $t };']
        p.say('say($w);', '-1')
    p.block(steps)
    def identity(p):
        p.lines += ['my $x = 1;', 'my $y = 1;', 'my $r = \\$x;', 'my $s = \\$x;', 'my $t = \\$y;']
        p.say('say($r == $s ? "same" : "diff", " ", $r != $t ? "diff" : "same", " ", \\$x == $r ? "same" : "diff");', 'same diff same')
        p.lines += ['my @a = (1);', 'my $ra = \\@a;']
        p.say('say($r == $ra ? "same" : "diff", " ", $r == [1] ? "same" : "diff");', 'diff diff')
        p.lines.append('$s->$* = 3;')
        p.say('say($x, ${ $r });', '33')
    p.block(identity)
    def kinds(p):
        x, y = Cell(1), Cell(2)
        p.lines += ['my $x = 1;', 'my $y = 2;', 'my $r = \\$x;', 'my $q = \\$r;']
        rcell = Cell(x)
        p.say('say(ref($q), " ", ref($q->$*), " ", ${ ${ $q } }, " ", ${ $q->$* });', f'{ref(rcell)} {ref(x)} 1 1')
        p.say('say(show($q));', show(rcell))
        for v, shown in (([1, 2], 'ARRAY'), ({'k': 3}, 'HASH')):
            x.v = v
            p.lines.append(f'$x = {"[1, 2]" if isinstance(v, list) else "{k => 3}"};')
            p.say(f'say(ref($r), " ", ref({p.through("$r")}), " ", show($r));', f'{ref(x)} {shown} {show(x)}')
        x.v = y
        p.lines.append('$x = \\$y;')
        p.say(f'say(ref($r), " ", ref({p.through("$r")}), " ", show($r));', f'{ref(x)} {ref(y)} {show(x)}')
        p.lines.append('${ $x } = 5;')
        y.v = 5
        p.say('say($y);', '5')
        p.lines += ['my $u;', 'my $ru = \\$u;']
        p.say('say(ref($ru), " ", defined($ru->$*) ? "d" : "u", " ", ref(\\$u), " ", ref(\\$ru), " ", ref(5), "|", ref(undef), "|");', 'SCALAR u SCALAR REF ||')
        p.lines += ['my $z = \\$x;', '$x = 0;']
        p.say('say($z ? "true" : "false", " ", defined($z) ? "d" : "u", " ", ${ $z } ? "true" : "false", " ", !$z ? "t" : "f");', 'true d false f')
    p.block(kinds)
    def heads(p):
        p.subs += ['sub cell($v) {', '    my $c = $v;', '    return \\$c;', '}']
        p.lines += ['my $x = 4;', 'my @a = (\\$x);', 'my %h = (k => \\$x);', 'my $d = {l => [\\$x]};']
        p.say('say(${ $a[0] }, $a[0]->$*, ${ $h{k} }, $h{k}->$*, ${ $d->{l}[0] }, $d->{l}->[0]->$*);', '444444')
        p.say('say(cell(6)->$*, ${ cell(7) }, ${ \\$x }, (\\$x)->$*);', '6744')
        p.lines += ['${ $a[0] } += 1;', '$h{k}->$* *= 2;', '${ $d->{l}[0] } .= "!";', '${ \\$x } .= "?";']
        p.say('say($x);', '10!?')
        p.lines += ['my $c = 1;', 'my $y = 0;', '${ $c ? \\$x : \\$y } = "w";']
        p.say('say($x, $y);', 'w0')
    p.block(heads)

def case_made(p):
    def from_undef(p):
        p.lines += ['my $r;', '$r->$* = 5;']
        p.say('say(ref($r), " ", ${ $r });', 'SCALAR 5')
        for op, b, start in (('+=', 2, None), ('-=', 3, None), ('.=', 'x', None), ('//=', 4, None), ('||=', 'y', None), ('&&=', 9, None)):
            v = OPS[op](start, b)
            p.n += 1
            name = f'$s{p.n}'
            p.lines += [f'my {name};', f'{p.through(name)} {op} {lit(b)};']
            p.say(f'say(ref({name}), " ", show({name}));', f'SCALAR {show(Cell(v))}')
        p.lines += ['my $i;', '$i->$*++;', 'my $j;', '--${ $j };', 'my $k;', 'my $old = ${ $k }++;']
        p.say('say(${ $i }, $j->$*, $k->$*, $old);', '1-110')
        p.lines += ['my $e;', 'my $f;', '(${ $e }, $f->$*) = (1, 2);']
        p.say('say(show($e), show($f));', '\\1\\2')
    p.block(from_undef)
    def hops(p):
        p.lines += ['my @a;', '$a[1]->$* = 3;', '${ $a[3] } .= "x";']
        p.say('say(show(\\@a));', '[u,\\3,u,\\x]')
        p.lines += ['my %h;', '$h{k}->$* = 4;', '${ $h{j} } += 2;', '$h{i}->$*++;']
        p.say('say(show(\\%h));', '{i:\\1,j:\\2,k:\\4}')
        p.lines += ['my $t;', '$t->{a}[1]->$* = 6;', '${ $t->{b} } //= 7;', '${ $t->{c}{d} } = 8;']
        p.say('say(show($t));', '{a:[u,\\6],b:\\7,c:{d:\\8}}')
        p.lines += ['my $z = 0;', 'my $l = [undef, \\$z];', '$l->[0]->$* = 1;', '$l->[1]->$* = 2;', '${ $l->[2] } = 3;']
        p.say('say(show($l), $z);', '[\\1,\\2,\\3]2')
        p.lines += ['my $was = $l->[1];', '${ $l->[1] } += 10;']
        p.say('say($was == $l->[1] ? "same" : "made", " ", $was->$*);', 'same 12')
    p.block(hops)
    def made_in_a_sub(p):
        p.subs += ['sub set($r, $v) {', '    $r->$* = $v;', '    return $r;', '}']
        p.lines += ['my $p = set(undef, 1);', 'my $q;', 'my $back = set($q, 2);']
        p.say('say(show($p), " ", defined($q) ? "made" : "u", " ", show($back));', '\\1 u \\2')
        p.lines += ['my $x = 0;', 'set(\\$x, 9);']
        p.say('say($x);', '9')
    p.block(made_in_a_sub)
    def cycle(p):
        p.lines += ['my $r;', '${ $r } = $r;']
        p.say('say(ref($r), " ", $r == $r->$* ? "cycle" : "no", " ", ref(${ ${ $r } }));', 'REF cycle REF')
        p.lines += ['my $x;', 'my $y = \\$x;', '$x = $y;']
        p.say('say(ref($y), " ", ref($x), " ", $x == $y ? "same" : "diff");', 'REF REF same')
    p.block(cycle)

def case_cells(p):
    def loops(p):
        p.lines += ['my @r;', 'for my $i (1 .. 3) {', '    my $v = $i * 10;', '    push @r, \\$v;', '}']
        p.say('say(join(",", map { $_->$* } @r));', '10,20,30')
        p.lines += ['${ $r[0] } = 5;']
        p.say('say(join(",", map { ${ $_ } } @r), " ", $r[0] == $r[1] ? "same" : "diff");', '5,20,30 diff')
        p.lines += ['my @w;', 'my $n = 0;', 'while ($n < 3) {', '    my $c = $n++;', '    push @w, \\$c;', '}']
        p.say('say(join(",", map { $_->$* } @w));', '0,1,2')
        p.lines += ['my @q = (1, 2, 3);', 'my @t;', 'while (my $e = shift @q) {', '    push @t, \\$e;', '}']
        p.say('say(join(",", map { $_->$* } @t));', '1,2,3')
        p.lines += ['my @c;', 'for (my $i = 0; $i < 3; $i++) {', '    push @c, \\$i;', '}']
        p.say('say(join(",", map { $_->$* } @c));', '3,3,3')
        p.lines += ['my @o;', 'my $one;', 'for my $i (1 .. 2) {', '    $one = $i;', '    push @o, \\$one;', '}']
        p.say('say(join(",", map { $_->$* } @o), " ", $o[0] == $o[1] ? "same" : "diff");', '2,2 same')
        p.lines += ['my @m = map { my $v = $_; \\$v } (4, 5);']
        p.say('say(join(",", map { $_->$* } @m));', '4,5')
    p.block(loops)
    def subs(p):
        p.subs += ['sub cell($v) {', '    my $c = $v;', '    return \\$c;', '}',
                   'sub param($v) {', '    my $r = \\$v;', '    $r->$* += 1;', '    return $v;', '}',
                   'sub keep($v, $w = 3) {', '    return (\\$v, \\$w);', '}']
        p.lines += ['my $p = cell(1);', 'my $q = cell(2);']
        p.say('say($p->$*, $q->$*, " ", $p == $q ? "same" : "diff");', '12 diff')
        p.lines += ['my $x = 1;']
        p.say('say(param($x), " ", $x);', '2 1')
        p.lines += ['my ($k1, $k2) = keep(5);', '${ $k1 } .= "a";', '$k2->$* .= "b";']
        p.say('say($k1->$*, ${ $k2 });', '5a3b')
    p.block(subs)
    # A file's variable has one cell from the start, which a sub written
    # after its `my` may take before the `my` has run, and the `my` stores
    # nothing (T255).
    p.lines += ['my $early = early();', '$early->$* = 7;', 'my $late;', 'sub early() {', '    return \\$late;', '}']
    p.say('say($late, " ", ${ early() }, " ", early() == $early ? "same" : "diff");', '7 7 same')
    def caught(p):
        p.lines += ['my @r;', 'for my $n (1 .. 2) {', '    try {', '        die "e$n\\n";', '    }', '    catch ($e) {', '        push @r, \\$e;', '    }', '}']
        p.lines.append('say(join("", map { $_->$* } @r));')
        p.out += ['e1', 'e2', '']
        p.lines += ['my ($x, $y) = (1, 2);', 'my $r = \\$x;', '($x, $y) = ($y, $x);']
        p.say('say("$x $y ", $r->$*);', '2 1 2')
    p.block(caught)

def case_lists(p):
    def lists(p):
        p.lines += ['my $x = 1;', 'my $y = 2;', 'my $r = \\$x;', 'my $s = \\$y;']
        p.say('say(join(",", $r->$*, ${ $s }, $x + $y, $r->$* + ${ $s }, $s->$* . $r->$*));', '1,2,3,3,21')
        p.lines += ['my @l = ($r->$*, $s->$*, $r->$*);']
        p.say('say("@l");', '1 2 1')
        p.lines += ['for my $v ($r->$*, ${ $s }) {', '    say($v * 10);', '}']
        p.out += ['10', '20']
        p.say('say(join(",", map { $_ * 2 } $r->$*, $s->$*), " ", join(",", grep { $_ > 1 } ${ $r }, ${ $s }));', '2,4 2')
        p.say('say(join(",", sort { $b <=> $a } ${ $r }, ${ $s }, 3));', '3,2,1')
        p.lines += ['(${ $r }, $s->$*) = ($s->$*, $r->$*);']
        p.say('say($x, $y);', '21')
        p.lines += ['my @refs = (\\$x, \\$y);', '$_->$* *= 2 for @refs;']
        p.say('say($x, $y);', '42')
        p.lines += ['for my $c (@refs) {', '    ${ $c } += 1;', '}']
        p.say('say($x, $y);', '53')
        p.lines += ['my @v = map { $_->$* } @refs;', 'my @g = grep { ${ $_ } > 4 } @refs;']
        p.say('say("@v ", scalar(@g), " ", ${ $g[0] });', '5 3 1 5')
    p.block(lists)
    def subs(p):
        p.subs += ['sub add($p, $q) {', '    return $p + $q;', '}',
                   'sub bump($c) {', '    $c->$* += 10;', '    return;', '}',
                   'sub where($c, $p, $q) {', '    return $c ? $p : $q;', '}']
        p.lines += ['my ($cx, $cy) = (1, 2);', 'my $x = 1;', 'my $r = \\$x;']
        p.say('say(add($r->$*, ${ $r }));', '2')
        p.lines += ['bump($r);', 'bump(\\$x);']
        p.say('say($x);', '21')
        p.lines += ['${ where(1, \\$cx, \\$cy) } = 10;', 'where(0, \\$cx, \\$cy)->$* .= "y";']
        p.say('say($cx, $cy);', '102y')
        p.lines += ['my %h = (a => \\$x);', '${ $h{a} } = 0;']
        p.say('say($x);', '0')
    p.block(subs)
    def thrown(p):
        p.lines += ['my $x = 1;', 'try {', '    die \\$x;', '}', 'catch ($e) {', '    say(ref($e), " ", $e->$*, " ", $e == \\$x ? "same" : "diff");', '}']
        p.out.append('SCALAR 1 same')
    p.block(thrown)

SAME = {
    '2200': ('sref-reads-and-stores', case_reads),
    '2201': ('sref-made', case_made),
    '2202': ('sref-cells-and-scopes', case_cells),
    '2203': ('sref-in-lists-loops-and-subs', case_lists),
}

# ---- the faults: each program says 1, does the one thing, and says 2.

FAULTS = []

def fault(name, lines, message, at=None):
    FAULTS.append((name, lines, message, at))

# Reading through what is not a reference to a scalar (D107).
fault('read-undef', ['my $r;', 'my $v = $r->$*;'], UNDEF_REF)
fault('read-undef-braces', ['my $r;', 'say(${ $r });'], UNDEF_REF)
fault('read-undef-defined', ['my $r;', 'say(defined($r->$*) ? "d" : "u");'], UNDEF_REF)
fault('read-undef-tested', ['my $r;', 'say("yes") if ${ $r };'], UNDEF_REF)
fault('read-undef-in-a-list', ['my $r;', 'my @l = (1, $r->$*);'], UNDEF_REF)
fault('read-undef-argument', ['sub f($v) {', '    return $v;', '}', 'my $r;', 'f(${ $r });'], UNDEF_REF)
fault('read-undef-in-a-loop', ['my $r;', 'for my $v ($r->$*) {', '}'], UNDEF_REF, 1)
fault('read-through-missing-index', ['my @a;', 'say(${ $a[0] });'], UNDEF_REF)
fault('read-through-missing-key', ['my %h;', 'say($h{k}->$*);'], UNDEF_REF)
fault('read-through-missing-hop', ['my $h = {};', 'say($h->{a}->$*);'], UNDEF_REF)
fault('read-a-call-giving-undef', ['sub g() {', '    return undef;', '}', 'say(g()->$*);'], UNDEF_REF)
fault('read-an-array-reference', ['my $r = [1];', 'say($r->$*);'], NOT_SCALAR)
fault('read-a-hash-reference', ['my $r = {};', 'say(${ $r });'], NOT_SCALAR)
fault('read-a-number', ['my $r = 5;', 'say($r->$*);'], NOT_SCALAR)
fault('read-a-string', ['my $r = "x";', 'say(${ $r });'], NOT_SCALAR)
fault('read-an-element-as-a-scalar', ['my $r = [[1]];', 'say($r->[0]->$*);'], NOT_SCALAR)
fault('read-a-scalar-as-an-array', ['my $x = 1;', 'my $r = \\$x;', 'say($r->[0]);'], NOT_ARRAY)
fault('read-a-scalar-as-a-hash', ['my $x = 1;', 'my $r = \\$x;', 'say(scalar(keys $r->%*));'], NOT_HASH)
# A store through what is defined and not a reference to a scalar (T234).
fault('store-through-an-array-reference', ['my $r = [1];', '$r->$* = 5;'], NOT_SCALAR)
fault('store-through-a-hash-reference', ['my $r = {};', '${ $r } .= "x";'], NOT_SCALAR)
fault('store-through-empty-string', ['my $r = "";', '${ $r } = 1;'], NOT_SCALAR)
fault('store-through-false', ['my $r = false;', '$r->$* = 1;'], NOT_SCALAR)
fault('step-through-a-number', ['my $r = 3;', '$r->$*++;'], NOT_SCALAR)
fault('hop-of-the-other-kind', ['my $h = {a => [1]};', '$h->{a}->$* = 5;'], NOT_SCALAR)
fault('push-through-a-scalar-reference', ['my $x;', 'my $r = \\$x;', 'push $r->@*, 1;'], NOT_ARRAY)
# Only a variable or an element is made (T252); a read-only one holding
# undef is not made either (T250).
fault('store-through-a-call', ['sub g() {', '    return undef;', '}', '${ g() } = 5;'], UNDEF_REF)
fault('store-through-or', ['my ($r, $s);', '($r || $s)->$* = 5;'], UNDEF_REF)
fault('store-through-a-choice', ['my ($r, $s);', 'my $c = 1;', '${ $c ? $r : $s } = 5;'], UNDEF_REF)
fault('store-through-loop-variable', ['my @l = (undef);', 'for my $x (@l) {', '    $x->$* = 1;', '}'], UNDEF_REF, 2)
fault('step-through-it', ['my @m = (undef);', '${ $_ }++ for @m;'], UNDEF_REF)
fault('store-through-it-in-a-map', ['my @m = (undef);', 'my @n = map { $_->$* = 1 } @m;'], UNDEF_REF)
# A reference to a scalar where a number or a string is wanted (D112).
for name, code, message in (
        ('added', 'say($r + 1);', NUMBER), ('negated', 'say(-$r);', NUMBER), ('compared', 'say($r < 1 ? "y" : "n");', NUMBER),
        ('compared-to-a-number', 'say($r == 1 ? "y" : "n");', NUMBER), ('stepped', '$r++;', NUMBER),
        ('joined', 'say($r . "x");', STRING), ('said', 'say($r);', STRING), ('interpolated', 'say("r=$r");', STRING),
        ('compared-as-a-string', 'say($r eq "x" ? "y" : "n");', STRING), ('a-key', 'my %h = ($r => 1);', STRING),
        ('length', 'say(length($r));', STRING), ('in-join', 'say(join(",", $r, 1));', STRING),
        ('sorted', 'my @l = ($r, \\$x);\nmy @s = sort @l;', STRING), ('repeated', 'say($r x 2);', STRING),
        ('formatted', 'say(sprintf("%s", $r));', STRING), ('died-among-others', 'die "x", $r;', STRING),
        ('warned', 'warn $r;', STRING)):
    fault(f'reference-{name}', ['my $x = 1;', 'my $r = \\$x;'] + code.split('\n'), message)
fault('reference-died-uncaught', ['my $x = 1;', 'die \\$x;'], STRING)
# The freeze is of the containers on the way to the scalar (D114, T251).
fault('frozen-on-the-way', ['my %h = (b => 2);', 'my $x = 1;', '$h{a} = \\$x;', 'my $g = \\%h;', 'for my $v ($h{a}->$*) {', '    $g->{c} = 3;', '    last;', '}'], HFROZEN, 5)
fault('frozen-on-a-chain', ['my $x = 1;', 'my $r = [\\$x];', 'my $s = $r;', 'for my $v ($r->[0]->$*) {', '    push $s->@*, 2;', '    last;', '}'], FROZEN, 4)

def commands():
    out = []
    for number, (name, _) in SAME.items():
        out.append(f'    python3 t/models/sref.py --program {number} > t/{number}-{name}.pl')
        out.append(f'    python3 t/models/sref.py {number} > t/{number}-{name}.expected')
    for n, (name, _, _, _) in enumerate(FAULTS):
        number = 2220 + n
        out.append(f'    python3 t/models/sref.py --program {number} > t/{number}-fault-sref-{name}.pl')
        out.append(f'    python3 t/models/sref.py {number} > t/{number}-fault-sref-{name}.expected')
    return '\n'.join(out) + '\n'

HEAD = '# model: t/models/sref.py\nuse v5.42;\n'

def main(argv):
    if argv == ['--commands']:
        sys.stdout.write(commands())
        return
    assert commands() in __doc__, 'the commands in the docstring are not the tests: python3 t/models/sref.py --commands'
    want_program = argv[0] == '--program'
    number = argv[-1]
    if number in SAME:
        name, case = SAME[number]
        p = Prog()
        case(p)
        indent = 0
        body = []
        for line in SHOW + p.subs + p.lines:
            for l in line.split('\n'):
                t = l.strip()
                if t.startswith('}'):
                    indent -= 1
                body.append('    ' * indent + t)
                if t.endswith('{'):
                    indent += 1
        sys.stdout.write(HEAD + '\n'.join(body) + '\n' if want_program else '\n'.join(p.out) + '\n')
        return
    n = int(number) - 2220
    name, lines, message, at = FAULTS[n]
    program = '# kind: fault\n' + HEAD + 'say(1);\n' + '\n'.join(lines) + '\nsay(2);\n'
    if want_program:
        sys.stdout.write(program)
        return
    # The line of the statement that faults: the last of `lines`, or the
    # one `at` says (a loop's own, for what its list does).
    line = 5 + (at if at is not None else len(lines) - 1)
    sys.stdout.write(f'1\nfault: {message} at t/{number}-fault-sref-{name}.pl line {line}.\nexit: 1\n')

if __name__ == '__main__':
    main(sys.argv[1:])
