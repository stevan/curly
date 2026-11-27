#!/usr/bin/env python3
"""t/4000 to t/4003, and the faults from t/4020: classes (step 17a; D170 to
D178, D187).

The definition, which is all this file knows of the language:

  class NAME { ... }         a class, its block declarations alone (D171):
  class NAME :isa(P) { ... } field, method, my method, ADJUST
  field $x :param :reader    a field; :param(NAME), :reader(NAME),
  field @a = LIST            :writer(NAME); a default with =, and with //=
                             or ||= for a parameter
  method NAME (SIG) { ... }  `$self` the object, read-only
  ADJUST { ... }
  NAME->new(PAIRS)           a new object; __CLASS__->new in the class
  EXPR->NAME(ARGS)           a method call; $self->SUPER::NAME(...),
                             $self->&NAME(...) of a my method
  EXPR isa NAME, ref, blessed, reftype

**Construction is two passes** (T400): every field of every class of the
chain, the root's first, in order, each argument copied at its field's
turn and each default worked out only where no argument was taken; then
every `ADJUST`, the root's first. **The pairs are looked at before any of
it runs** (D178, D187): an odd count, a name that is no parameter, a name
given twice, a required parameter missing, each a fault. **A method call
reaches the method the object's class has for the name**, its own or its
parent's; `SUPER::` is the parent of the class the method is written in
(T431); a `my method` is called with no dispatch. A reader gives a copy of
its field, an array's or a hash's a list (D18: where one value is wanted,
the fault `P->a returned a list where one value is wanted`); a writer
stores and gives the object back. **A field is a container** (D175): a
loop over it freezes it, `\\$x` of a scalar field is one reference for the
instance's life (T432), and a closure has the field itself (D161). **An
object is a reference** (D176): true, `==` by identity, `ref` and
`blessed` its class's name, `reftype` OBJECT, and wherever a number or a
string is wanted the fault `a reference where a ... is wanted`. A call on
undef is `undef where an object is wanted`, on what is no object `not an
object`, and on an object whose class has no such method `an object of P
has no method m`.

The model is Python, an object a dict of fields with its class, a class a
record of its parent, its fields and its methods written out as Python
functions by hand. perl is the second derivation: t/checks.py oracle holds
every .expected of a test without a `kind:` to what perl 5.42 prints, and
each fault test's output to the start of it.

4000 construction; 4001 dispatch; 4002 fields as containers and closures;
4003 objects in data, and the orders. 4020 on each fault once.

Every command that writes a file, one a line (t/checks.py runs them all):

    python3 t/models/obj.py --program 4000 > t/4000-obj-construction.pl
    python3 t/models/obj.py 4000 > t/4000-obj-construction.expected
    python3 t/models/obj.py --program 4001 > t/4001-obj-dispatch.pl
    python3 t/models/obj.py 4001 > t/4001-obj-dispatch.expected
    python3 t/models/obj.py --program 4002 > t/4002-obj-fields.pl
    python3 t/models/obj.py 4002 > t/4002-obj-fields.expected
    python3 t/models/obj.py --program 4003 > t/4003-obj-in-data.pl
    python3 t/models/obj.py 4003 > t/4003-obj-in-data.expected
    python3 t/models/obj.py --program 4020 > t/4020-fault-obj-new-odd.pl
    python3 t/models/obj.py 4020 > t/4020-fault-obj-new-odd.expected
    python3 t/models/obj.py --program 4021 > t/4021-fault-obj-new-unknown.pl
    python3 t/models/obj.py 4021 > t/4021-fault-obj-new-unknown.expected
    python3 t/models/obj.py --program 4022 > t/4022-fault-obj-new-twice.pl
    python3 t/models/obj.py 4022 > t/4022-fault-obj-new-twice.expected
    python3 t/models/obj.py --program 4023 > t/4023-fault-obj-new-missing.pl
    python3 t/models/obj.py 4023 > t/4023-fault-obj-new-missing.expected
    python3 t/models/obj.py --program 4024 > t/4024-fault-obj-new-missing-parent.pl
    python3 t/models/obj.py 4024 > t/4024-fault-obj-new-missing-parent.expected
    python3 t/models/obj.py --program 4025 > t/4025-fault-obj-new-unknown-before-adjust.pl
    python3 t/models/obj.py 4025 > t/4025-fault-obj-new-unknown-before-adjust.expected
    python3 t/models/obj.py --program 4026 > t/4026-fault-obj-new-undef-key.pl
    python3 t/models/obj.py 4026 > t/4026-fault-obj-new-undef-key.expected
    python3 t/models/obj.py --program 4027 > t/4027-fault-obj-new-reference-key.pl
    python3 t/models/obj.py 4027 > t/4027-fault-obj-new-reference-key.expected
    python3 t/models/obj.py --program 4028 > t/4028-fault-obj-new-hash-default-odd.pl
    python3 t/models/obj.py 4028 > t/4028-fault-obj-new-hash-default-odd.expected
    python3 t/models/obj.py --program 4029 > t/4029-fault-obj-call-undef.pl
    python3 t/models/obj.py 4029 > t/4029-fault-obj-call-undef.expected
    python3 t/models/obj.py --program 4030 > t/4030-fault-obj-call-string.pl
    python3 t/models/obj.py 4030 > t/4030-fault-obj-call-string.expected
    python3 t/models/obj.py --program 4031 > t/4031-fault-obj-call-array-reference.pl
    python3 t/models/obj.py 4031 > t/4031-fault-obj-call-array-reference.expected
    python3 t/models/obj.py --program 4032 > t/4032-fault-obj-call-sub-reference.pl
    python3 t/models/obj.py 4032 > t/4032-fault-obj-call-sub-reference.expected
    python3 t/models/obj.py --program 4033 > t/4033-fault-obj-call-number.pl
    python3 t/models/obj.py 4033 > t/4033-fault-obj-call-number.expected
    python3 t/models/obj.py --program 4034 > t/4034-fault-obj-call-missing.pl
    python3 t/models/obj.py 4034 > t/4034-fault-obj-call-missing.expected
    python3 t/models/obj.py --program 4035 > t/4035-fault-obj-call-count-few.pl
    python3 t/models/obj.py 4035 > t/4035-fault-obj-call-count-few.expected
    python3 t/models/obj.py --program 4036 > t/4036-fault-obj-call-count-many.pl
    python3 t/models/obj.py 4036 > t/4036-fault-obj-call-count-many.expected
    python3 t/models/obj.py --program 4037 > t/4037-fault-obj-reader-count.pl
    python3 t/models/obj.py 4037 > t/4037-fault-obj-reader-count.expected
    python3 t/models/obj.py --program 4038 > t/4038-fault-obj-writer-count.pl
    python3 t/models/obj.py 4038 > t/4038-fault-obj-writer-count.expected
    python3 t/models/obj.py --program 4039 > t/4039-fault-obj-list-where-one-value.pl
    python3 t/models/obj.py 4039 > t/4039-fault-obj-list-where-one-value.expected
    python3 t/models/obj.py --program 4040 > t/4040-fault-obj-reader-list-where-one-value.pl
    python3 t/models/obj.py 4040 > t/4040-fault-obj-reader-list-where-one-value.expected
    python3 t/models/obj.py --program 4041 > t/4041-fault-obj-frozen-field-array.pl
    python3 t/models/obj.py 4041 > t/4041-fault-obj-frozen-field-array.expected
    python3 t/models/obj.py --program 4042 > t/4042-fault-obj-frozen-field-by-method.pl
    python3 t/models/obj.py 4042 > t/4042-fault-obj-frozen-field-by-method.expected
    python3 t/models/obj.py --program 4043 > t/4043-fault-obj-frozen-field-hash.pl
    python3 t/models/obj.py 4043 > t/4043-fault-obj-frozen-field-hash.expected
    python3 t/models/obj.py --program 4044 > t/4044-fault-obj-object-said.pl
    python3 t/models/obj.py 4044 > t/4044-fault-obj-object-said.expected
    python3 t/models/obj.py --program 4045 > t/4045-fault-obj-object-interpolated.pl
    python3 t/models/obj.py 4045 > t/4045-fault-obj-object-interpolated.expected
    python3 t/models/obj.py --program 4046 > t/4046-fault-obj-object-joined.pl
    python3 t/models/obj.py 4046 > t/4046-fault-obj-object-joined.expected
    python3 t/models/obj.py --program 4047 > t/4047-fault-obj-object-added.pl
    python3 t/models/obj.py 4047 > t/4047-fault-obj-object-added.expected
    python3 t/models/obj.py --program 4048 > t/4048-fault-obj-object-negated.pl
    python3 t/models/obj.py 4048 > t/4048-fault-obj-object-negated.expected
    python3 t/models/obj.py --program 4049 > t/4049-fault-obj-object-compared.pl
    python3 t/models/obj.py 4049 > t/4049-fault-obj-object-compared.expected
    python3 t/models/obj.py --program 4050 > t/4050-fault-obj-object-compared-to-a-number.pl
    python3 t/models/obj.py 4050 > t/4050-fault-obj-object-compared-to-a-number.expected
    python3 t/models/obj.py --program 4051 > t/4051-fault-obj-object-compared-as-a-string.pl
    python3 t/models/obj.py 4051 > t/4051-fault-obj-object-compared-as-a-string.expected
    python3 t/models/obj.py --program 4052 > t/4052-fault-obj-object-a-key.pl
    python3 t/models/obj.py 4052 > t/4052-fault-obj-object-a-key.expected
    python3 t/models/obj.py --program 4053 > t/4053-fault-obj-object-length.pl
    python3 t/models/obj.py 4053 > t/4053-fault-obj-object-length.expected
    python3 t/models/obj.py --program 4054 > t/4054-fault-obj-object-in-join.pl
    python3 t/models/obj.py 4054 > t/4054-fault-obj-object-in-join.expected
    python3 t/models/obj.py --program 4055 > t/4055-fault-obj-object-sorted.pl
    python3 t/models/obj.py 4055 > t/4055-fault-obj-object-sorted.expected
    python3 t/models/obj.py --program 4056 > t/4056-fault-obj-object-formatted.pl
    python3 t/models/obj.py 4056 > t/4056-fault-obj-object-formatted.expected
    python3 t/models/obj.py --program 4057 > t/4057-fault-obj-object-an-index.pl
    python3 t/models/obj.py 4057 > t/4057-fault-obj-object-an-index.expected
    python3 t/models/obj.py --program 4058 > t/4058-fault-obj-object-stepped.pl
    python3 t/models/obj.py 4058 > t/4058-fault-obj-object-stepped.expected
    python3 t/models/obj.py --program 4059 > t/4059-fault-obj-object-uc.pl
    python3 t/models/obj.py 4059 > t/4059-fault-obj-object-uc.expected
    python3 t/models/obj.py --program 4060 > t/4060-fault-obj-object-warned.pl
    python3 t/models/obj.py 4060 > t/4060-fault-obj-object-warned.expected
    python3 t/models/obj.py --program 4061 > t/4061-fault-obj-object-died-among-others.pl
    python3 t/models/obj.py 4061 > t/4061-fault-obj-object-died-among-others.expected
    python3 t/models/obj.py --program 4062 > t/4062-fault-obj-object-died-uncaught.pl
    python3 t/models/obj.py 4062 > t/4062-fault-obj-object-died-uncaught.expected
    python3 t/models/obj.py --program 4063 > t/4063-fault-obj-object-as-an-array.pl
    python3 t/models/obj.py 4063 > t/4063-fault-obj-object-as-an-array.expected
    python3 t/models/obj.py --program 4064 > t/4064-fault-obj-object-as-a-hash.pl
    python3 t/models/obj.py 4064 > t/4064-fault-obj-object-as-a-hash.expected
    python3 t/models/obj.py --program 4065 > t/4065-fault-obj-object-as-a-scalar.pl
    python3 t/models/obj.py 4065 > t/4065-fault-obj-object-as-a-scalar.expected
    python3 t/models/obj.py --program 4066 > t/4066-fault-obj-object-as-a-sub.pl
    python3 t/models/obj.py 4066 > t/4066-fault-obj-object-as-a-sub.expected
    python3 t/models/obj.py --program 4067 > t/4067-fault-obj-object-as-a-whole-array.pl
    python3 t/models/obj.py 4067 > t/4067-fault-obj-object-as-a-whole-array.expected
    python3 t/models/obj.py --program 4068 > t/4068-fault-obj-recursion-too-deep.pl
    python3 t/models/obj.py 4068 > t/4068-fault-obj-recursion-too-deep.expected
"""

import sys

STRING = 'a reference where a string is wanted'
NUMBER = 'a reference where a number is wanted'
FROZEN = 'an array was changed while a foreach is over it'
HFROZEN = 'a hash was changed while a foreach is over it'


class Prog:
    def __init__(self):
        self.lines = []
        self.out = []
        self.classes = []

    def say(self, text, printed):
        self.lines.append(text)
        self.out.append(printed)


def case_construction(p):
    # Two passes over a chain of three (T400): fields root first, each in
    # order, then every ADJUST root first. The log is a file variable each
    # default and ADJUST appends to.
    p.classes += [
        'my $log = "";',
        'class A {',
        'field $a1 = main::do_log("A.a1", 1);',
        'field $x :param :reader;',
        'ADJUST { $log .= "A.adjust1 "; }',
        'field $a2 :reader = $x + 100;',
        'ADJUST { $log .= "A.adjust2 "; }',
        '}',
        'class B :isa(A) {',
        'field $b1 :param :reader //= "b1d";',
        'field $b2 :param :reader ||= "b2d";',
        'ADJUST { $log .= "B.adjust "; }',
        '}',
        'class C :isa(B) {',
        'field @items :reader = (1, 2, 3);',
        'field %opts = (k => "v");',
        'field $total :reader = 0;',
        'ADJUST { $total = scalar(@items); $log .= "C.adjust "; }',
        'method opt($k) { $opts{$k} }',
        '}',
    ]
    # A field's default calls a sub of the program's by its whole name
    # (D178, T422).
    p.classes[1:1] = ['sub do_log($what, $v) {', '$log .= "$what ";', 'return $v;', '}']

    def make(x, b1=None, b2=None, given_b1=False, given_b2=False):
        log = ['A.a1']
        obj = {'x': x, 'a2': x + 100}
        obj['b1'] = b1 if given_b1 and b1 is not None else 'b1d'
        obj['b2'] = b2 if given_b2 and b2 else 'b2d'
        obj['items'] = [1, 2, 3]
        obj['total'] = 3
        log += ['A.adjust1', 'A.adjust2', 'B.adjust', 'C.adjust']
        return obj, ' '.join(log) + ' '

    o, log = make(5)
    p.lines.append('my $c = C->new(x => 5);')
    p.say('say $log;', log)
    p.say('say join ",", $c->x, $c->a2, $c->b1, $c->b2, $c->total;', ','.join(map(str, [o['x'], o['a2'], o['b1'], o['b2'], o['total']])))
    p.say('say join ",", $c->items;', ','.join(map(str, o['items'])))
    p.say('say $c->opt("k");', 'v')
    p.lines.append('$log = "";')
    o, log = make(7, b1=None, b2=0, given_b1=True, given_b2=True)
    # `//=` takes the default for undef, `||=` for anything false.
    p.lines.append('my $d = C->new(b2 => 0, x => 7, b1 => undef);')
    p.say('say $log;', log)
    p.say('say join ",", $d->x, $d->b1, $d->b2;', ','.join(map(str, [o['x'], o['b1'], o['b2']])))
    o, _ = make(1, b1='given', b2='also', given_b1=True, given_b2=True)
    p.lines.append('my $e = C->new(b1 => "given", x => 1, b2 => "also");')
    p.say('say join ",", $e->b1, $e->b2;', f"{o['b1']},{o['b2']}")
    # A default is worked out only where no argument was taken
    # (17-param-default-skipped).
    p.lines.append('$log = "";')
    p.classes += ['class D {', 'field $v :param :reader = main::do_log("D.default", 9);', '}']
    p.lines.append('my $dv = D->new(v => 3)->v;')
    p.say('say "$dv [$log]";', '3 []')
    p.lines.append('my $dd = D->new->v;')
    p.say('say "$dd [$log]";', '9 [D.default ]')
    # A writer stores, and gives the object back; a reader a copy.
    p.classes += ['class W {', 'field $n :reader :writer = 1;', 'field $m :reader :writer(put_m) = "m";', '}']
    p.lines.append('my $w = W->new;')
    p.say('say $w->set_n(5)->put_m("q")->n, $w->m;', '5q')
    p.lines.append('my $copy = $w->n;')
    p.lines.append('$copy = 99;')
    p.say('say $w->n;', '5')
    # Each object has fields of its own (17-field-fresh).
    p.lines += ['my $c1 = C->new(x => 1);', 'my $c2 = C->new(x => 2);']
    p.say('say $c1->x, $c2->x, $c1->a2, $c2->a2;', '12101102')


def case_dispatch(p):
    p.classes += [
        'my @said;',
        'class Shape {',
        'field $name :param :reader = "shape";',
        'method area { 0 }',
        'method describe { $name . " " . $self->area }',
        'method kind { __CLASS__ }',
        'method twin { __CLASS__->new(name => "twin of $name") }',
        'ADJUST { $self->hello }',
        'method hello { push @said, "Shape.hello"; return }',
        '}',
        'class Square :isa(Shape) {',
        'field $side :param :reader = 1;',
        'method area { $side * $side }',
        'method hello { return }',
        '}',
        'class Cube :isa(Square) {',
        'method area { 6 * $self->SUPER::area() }',
        'method label { "cube:" . $self->SUPER::describe() }',
        '}',
        'class Counter {',
        'field $n = 0;',
        'my method bump($by) { $n += $by; return $n }',
        'method add2 { $self->&bump(1); return $self->&bump(1) }',
        'method parts { return ($n, $n + 1, $n + 2) }',
        'method one { return $n }',
        '}',
    ]
    shapes = [('Shape', 'shape', 0), ('Square', 'sq', 9), ('Cube', 'cu', 6 * 4)]
    p.lines += ['my @shapes = (Shape->new, Square->new(name => "sq", side => 3), Cube->new(name => "cu", side => 2));']
    p.say('say join "|", map { $_->describe } @shapes;', '|'.join(f'{n} {a}' for _, n, a in shapes))
    p.say('say join "|", map { $_->kind } @shapes;', '|'.join(k for k, _, _ in shapes))
    p.say('say join "|", map { ref $_->twin } @shapes;', '|'.join(k for k, _, _ in shapes))
    p.say('say $shapes[2]->twin->name;', 'twin of cu')
    p.say('say $shapes[2]->label;', 'cube:cu 24')
    # The parent's ADJUST dispatches to the child's method (R17-17): a
    # Square and a Cube say nothing, and each object that is only a Shape
    # says hello once: the first, its twin made in the map above, and the
    # two made here.
    made = 1 + 1 + 2
    p.lines.append('my $t = Shape->new->twin;')
    p.say('say scalar(@said);', str(made))
    p.say('say join ",", map { ($_ isa Shape ? 1 : 0) . ($_ isa Square ? 1 : 0) . ($_ isa Cube ? 1 : 0) } @shapes;', '100,110,111')
    p.say('say join ",", map { ref $_ } @shapes;', 'Shape,Square,Cube')
    p.say('say blessed($shapes[1]), " ", reftype($shapes[1]);', 'Square OBJECT')
    p.lines.append("my $z = 1;\nmy $first = $shapes[0];")
    p.say('say defined(blessed([1])) ? "b" : "u", reftype([1]), reftype({}), reftype(\\$z), reftype(\\$first), defined(reftype(1)) ? "r" : "u";', 'uARRAYHASHSCALARREFu')
    p.lines.append('my $k = Counter->new;')
    p.say('say $k->add2, $k->add2;', '24')
    p.lines.append('my @p = $k->parts;')
    p.say('say "@p";', '4 5 6')
    p.say('say $k->one + 1;', '5')
    p.say('say((Counter->new isa Shape) ? "yes" : "no");', 'no')
    p.say('say(((undef) isa Shape) ? "yes" : "no", ("Shape" isa Shape) ? "yes" : "no", ([] isa Shape) ? "yes" : "no");', 'nonono')


def case_fields(p):
    p.classes += [
        'class Bag {',
        'field @items;',
        'field %count;',
        'field $last = "none";',
        'method add(@new) { for my $x (@new) { push @items, $x; $count{$x}++; $last = $x } return scalar(@items) }',
        'method items_ref { \\@items }',
        'method last_ref { \\$last }',
        'method last { $last }',
        'method counts { join ",", map { "$_=$count{$_}" } sort keys %count }',
        'method watcher { sub { $last } }',
        'method setter { sub ($v) { $last = $v; return } }',
        'method self_getter { sub { $self->last } }',
        'method plain { sub { 42 } }',
        '}',
        'class Lazy {',
        'field $n = 1;',
        'field $get = sub { $n };',
        'field $cb;',
        'ADJUST { $cb = sub { $n * 10 } }',
        'method bump { $n++; return }',
        'method both { $get->() . "/" . $cb->() }',
        '}',
    ]
    p.lines.append('my $g = Bag->new;')
    p.say('say $g->add("x", "y", "x");', '3')
    p.say('say $g->counts, " ", $g->last;', 'x=2,y=1 x')
    p.lines.append('push $g->items_ref->@*, "z";')
    p.say('say join ",", $g->items_ref->@*;', 'x,y,x,z')
    p.lines.append('${ $g->last_ref } = "set";')
    p.say('say $g->last;', 'set')
    p.say('say $g->last_ref == $g->last_ref ? "same" : "diff";', 'same')
    p.lines.append('my $h = Bag->new;')
    p.say('say $g->last_ref == $h->last_ref ? "same" : "diff";', 'diff')
    p.lines += ['my $w = $g->watcher;', 'my $s = $g->setter;']
    p.lines.append('$g->add("q");')
    p.say('say $w->();', 'q')
    p.lines.append('$s->("from closure");')
    p.say('say $g->last, " ", $h->last;', 'from closure none')
    p.say('say $g->self_getter->();', 'from closure')
    p.say('say $g->plain == $g->plain ? "same" : "diff", $g->watcher == $g->watcher ? "same" : "diff";', 'samediff')
    p.lines.append('my $z = Lazy->new;')
    p.say('say $z->both;', '1/10')
    p.lines.append('$z->bump;')
    p.say('say $z->both;', '2/20')


def case_in_data(p):
    p.classes += [
        'class Pt {',
        'field $x :param :reader;',
        'field $y :param :reader = 0;',
        'method str { "($x,$y)" }',
        'method plus($o) { Pt->new(x => $x + $o->x, y => $y + $o->y) }',
        '}',
        'class Err {',
        'field $msg :param :reader;',
        '}',
        'class Link {',
        'field $v :param :reader;',
        'field $next :param :reader = undef;',
        'method sum { $v + (defined $next ? $next->sum : 0) }',
        '}',
    ]
    pts = [(3, 1), (1, 5), (2, 2)]
    p.lines.append('my @pts = (Pt->new(x => 3, y => 1), Pt->new(x => 1, y => 5), Pt->new(x => 2, y => 2));')
    p.say('say join " ", map { $_->str } sort { $a->x <=> $b->x } @pts;', ' '.join(f'({x},{y})' for x, y in sorted(pts)))
    p.say('say join " ", map { $_->str } grep { $_->y > 1 } @pts;', ' '.join(f'({x},{y})' for x, y in pts if y > 1))
    p.say('say $pts[0]->plus($pts[1])->plus($pts[2])->str;', '(6,8)')
    p.lines.append('my %by = map { ($_->x => $_) } @pts;')
    p.say('say $by{2}->str;', '(2,2)')
    p.lines.append('my $r = { list => [@pts] };')
    p.say('say $r->{list}[1]->str, $r->{list}->[2]->y;', '(1,5)2')
    # A die of an object is caught as the object itself (T414-caught).
    p.lines.append('try { die Err->new(msg => "boom") } catch ($e) { say ref($e), " ", $e->msg, " ", ($e isa Err) ? 1 : 0 }')
    p.out.append('Err boom 1')
    # The invocant is read when the call is made (T405, T429).
    p.lines.append('my $o = Pt->new(x => 1);')
    p.say('say $o->plus(($o = Pt->new(x => 10)) ? Pt->new(x => 100) : undef)->x;', '110')
    p.lines.append('my $o2 = Pt->new(x => 1);')
    p.say('say((1 ? $o2 : undef)->plus(($o2 = Pt->new(x => 20)) ? Pt->new(x => 100) : undef)->x);', '120')
    # `new`'s values are read at their fields' turns (T427).
    p.classes += ['class Late {', 'field $w = main::bump_v();', 'field $got :param :reader;', '}']
    p.classes[0:0] = ['my $v = "old";', 'sub bump_v() {', '$v = "new";', 'return 1;', '}']
    p.say('say Late->new(got => $v)->got;', 'new')
    total = 0
    p.lines.append('my $l = undef;')
    p.lines.append('for my $i (1 .. 90) { $l = Link->new(v => $i, next => $l) }')
    p.say('say $l->sum;', str(sum(range(1, 91))))
    p.say('say $l ? "true" : "false", defined($l) ? 1 : 0;', 'true1')


SAME = {
    '4000': ('obj-construction', case_construction),
    '4001': ('obj-dispatch', case_dispatch),
    '4002': ('obj-fields', case_fields),
    '4003': ('obj-in-data', case_in_data),
}

FAULTS = []

def fault(name, classes, lines, message, at=None):
    FAULTS.append((name, classes, lines, message, at))

P = 'class P { field $x :param :reader; field $y :param = 0; method m($v) { $v } method many { return (1, 2) } }'
Q = 'class Q { method only { 1 } }'
# The constructor's faults, before anything of it runs (D178, D187).
fault('new-odd', [P], ['P->new("x");'], 'an odd number of arguments for P->new: they are names and values by turns')
fault('new-unknown', [P], ['P->new(x => 1, z => 2);'], 'P->new was given z, which is no parameter of P')
fault('new-twice', [P], ['P->new(x => 1, x => 2);'], 'P->new was given x twice')
fault('new-missing', [P], ['P->new(y => 1);'], 'P->new was not given x, which it needs')
fault('new-missing-parent', [P, 'class R :isa(P) { field $z :param; }'], ['R->new(x => 1);'], 'R->new was not given z, which it needs')
fault('new-unknown-before-adjust', ['class S { field $f = main::noisy(); ADJUST { say "adjust" } }'], ['S->new(b => 1);'], 'S->new was given b, which is no parameter of S')
fault('new-undef-key', [P], ['P->new(undef, 1);'], 'undef where a string is wanted')
fault('new-reference-key', [P], ['P->new([1], 1);'], STRING)
fault('new-hash-default-odd', ['class H { field %h = (1, 2, 3); }'], ['H->new;'], 'an odd number of values for a hash', at='class H')
# A method call's faults.
fault('call-undef', [P], ['my $u;', '$u->m(1);'], 'undef where an object is wanted')
fault('call-string', [P], ['my $s = "P";', '$s->m(1);'], 'not an object')
fault('call-array-reference', [P], ['my $r = [1];', '$r->m(1);'], 'not an object')
fault('call-sub-reference', [P], ['my $r = sub { 1 };', '$r->m(1);'], 'not an object')
fault('call-number', [P], ['my $n = 5;', '$n->m(1);'], 'not an object')
fault('call-missing', [P, Q], ['my $q = Q->new;', '$q->m(1);'], 'an object of Q has no method m')
fault('call-count-few', [P], ['P->new(x => 1)->m;'], 'too few arguments for P->m: got 0, expected 1')
fault('call-count-many', [P], ['P->new(x => 1)->m(1, 2);'], 'too many arguments for P->m: got 2, expected 1')
fault('reader-count', [P], ['P->new(x => 1)->x(1);'], 'too many arguments for P->x: got 1, expected 0')
fault('writer-count', ['class W { field $n :writer = 1; }'], ['W->new->set_n;'], 'too few arguments for W->set_n: got 0, expected 1')
fault('list-where-one-value', [P], ['my $v = P->new(x => 1)->many;'], 'P->many returned a list where one value is wanted', at='class P')
fault('reader-list-where-one-value', ['class A { field @a :reader = (1, 2); }'], ['my $n = A->new->a;'], 'A->a returned a list where one value is wanted', at='class A')
fault('frozen-field-array', ['class F { field @a = (1, 2); method go { for my $v (@a) { push @a, 3; last } return } }'], ['F->new->go;'], FROZEN, at='class F')
fault('frozen-field-by-method', ['class G { field @a = (1, 2); method more { push @a, 3; return } method go { for my $v (@a) { $self->more; last } return } }'], ['G->new->go;'], FROZEN, at='class G')
fault('frozen-field-hash', ['class K { field %h = (a => 1); method go { for my $v (values %h) { $h{b} = 2; last } return } }'], ['K->new->go;'], HFROZEN, at='class K')
# An object is a reference (D176): every place a number or a string is
# wanted.
for name, code, message in (
        ('said', 'say $o;', STRING), ('interpolated', 'say "o: $o";', STRING), ('joined', 'my $s = "a" . $o;', STRING),
        ('added', 'my $n = $o + 1;', NUMBER), ('negated', 'my $n = -$o;', NUMBER), ('compared', 'my $c = $o < 1;', NUMBER),
        ('compared-to-a-number', 'my $c = $o == 1;', NUMBER), ('compared-as-a-string', 'my $c = $o eq "P";', STRING),
        ('a-key', 'my %h = ($o => 1);', STRING), ('length', 'my $n = length($o);', STRING), ('in-join', 'my $s = join(",", $o);', STRING),
        ('sorted', 'my @l = ($o, $o);\nmy @s = sort @l;', STRING), ('formatted', 'my $s = sprintf("%s", $o);', STRING), ('an-index', 'my @a = (1);\nmy $e = $a[$o];', NUMBER),
        ('stepped', 'my $p = $o;\n$p++;', NUMBER), ('uc', 'my $s = uc($o);', STRING), ('warned', 'warn $o;', STRING),
        ('died-among-others', 'die "x", $o;', STRING), ('died-uncaught', 'die $o;', STRING),
        ('as-an-array', 'my $e = $o->[0];', 'not a reference to an array'), ('as-a-hash', 'my $e = $o->{k};', 'not a reference to a hash'),
        ('as-a-scalar', 'my $e = $o->$*;', 'not a reference to a scalar'), ('as-a-sub', 'my $e = $o->();', 'not a reference to a sub'),
        ('as-a-whole-array', 'my @e = $o->@*;', 'not a reference to an array')):
    fault(f'object-{name}', [Q], ['my $o = Q->new;'] + code.split('\n'), message)
# A loop that only the fault ends is counted by something the fault does
# not touch (T131): the depth of a construction, each object's default
# making the next. Nested construction counts against D68's limit. perl
# 5.42 itself dies of a segmentation fault at about 20,000 deep on an 8 MB
# stack (T440), so the test goes to 4,000, which perl finishes.
fault('recursion-too-deep', ["no warnings 'recursion';", 'class N { field $d :param; field $kid = $d < 4000 ? N->new(d => $d + 1) : undef; }'], ['N->new(d => 0);'], 'recursion too deep', at='kid')


def commands():
    out = []
    for number, (name, _) in SAME.items():
        out.append(f'    python3 t/models/obj.py --program {number} > t/{number}-{name}.pl')
        out.append(f'    python3 t/models/obj.py {number} > t/{number}-{name}.expected')
    for n, (name, *_rest) in enumerate(FAULTS):
        number = 4020 + n
        out.append(f'    python3 t/models/obj.py --program {number} > t/{number}-fault-obj-{name}.pl')
        out.append(f'    python3 t/models/obj.py {number} > t/{number}-fault-obj-{name}.expected')
    return '\n'.join(out) + '\n'


HEAD = "# model: t/models/obj.py\nuse v5.42;\nuse experimental 'class';\n"


def lay_out(lines):
    indent = 0
    body = []
    for line in lines:
        for l in line.split('\n'):
            t = l.strip()
            if t.startswith('}'):
                indent -= 1
            body.append('    ' * indent + t)
            if t.endswith('{'):
                indent += 1
    return body


def main(argv):
    if argv == ['--commands']:
        sys.stdout.write(commands())
        return
    assert commands() in __doc__, 'the commands in the docstring are not the tests: python3 t/models/obj.py --commands'
    want_program = argv[0] == '--program'
    number = argv[-1]
    if number in SAME:
        name, case = SAME[number]
        p = Prog()
        case(p)
        sys.stdout.write(HEAD + '\n'.join(lay_out(p.classes + p.lines)) + '\n' if want_program else '\n'.join(p.out) + '\n')
        return
    n = int(number) - 4020
    name, classes, lines, message, at = FAULTS[n]
    pragma = ''
    if classes and classes[0].startswith('no warnings'):
        pragma = classes[0] + '\n'
        classes = classes[1:]
    noisy = ['sub noisy() {', 'say "noisy";', 'return 1;', '}'] if any('main::noisy' in c for c in classes) else []
    head = '# kind: fault\n' + HEAD + pragma
    top = noisy + classes
    program = head + ''.join(c + '\n' for c in top) + 'say(1);\n' + '\n'.join(lines) + '\nsay(2);\n'
    if want_program:
        sys.stdout.write(program)
        return
    first = head.count('\n') + len(top) + 2
    if at == -1:
        line = first + len(lines) - 1
    elif isinstance(at, str):
        line = head.count('\n') + 1 + next(k for k, c in enumerate(top) if at in c)
    else:
        line = first + len(lines) - 1
    sys.stdout.write(f'1\nfault: {message} at t/{number}-fault-obj-{name}.pl line {line}.\nexit: 1\n')


if __name__ == '__main__':
    main(sys.argv[1:])
