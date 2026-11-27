# Step 17's statements about perl, as claims.py's rows: a file of its own,
# as step 16's is, so that it merges beside step 14 without touching the
# rows that step adds. claims.py reads it.
#
#     python3 docs/briefs/claims.py T400 17-dispatch-shape
#
# A row with roles=True is a statement about the roles perl (D161, D166),
# and claims.py runs it under $CURLY_PERL_ROLES (default
# /opt/perl-5.42-roles/bin/perl, which tools/perl-roles/build.sh makes).
# The program is claim.pl: `use v5.42;` is line 1 and CLASS line 2, so a
# statement on the first line of `code` is on line 3.

CLASS = "use experimental 'class';\n"

def c(id, where, code, **said):
    return (id, where, CLASS + code, said)

STEP17 = [
    # ---- construction (PLAN 17, "What perl does that the obvious build
    # gets wrong"; TRAPS T400 to T404)
    c('T400', 'TRAPS; PLAN 17', 'class A { field $a = do { say "A.field"; 1 }; ADJUST { say "A.adjust" } } class B :isa(A) { field $b = do { say "B.field"; 2 }; ADJUST { say "B.adjust" } } B->new;', out='A.field\nB.field\nA.adjust\nB.adjust\n'),
    c('T400-one', 'TRAPS; PLAN 17', 'class P { field $x = do { say "x"; 1 }; ADJUST { say "adj1 $x" } field $y = do { say "y"; 2 }; ADJUST { say "adj2 $y" } } P->new;', out='x\ny\nadj1 1\nadj2 2\n'),
    c('T401-self', 'TRAPS; PLAN 17', 'class P { field $x = 2; field $y = $self->x; method x { $x } }', compiles=False, err=r'Global symbol "\$self" requires explicit package name'),
    c('T401-later', 'TRAPS; PLAN 17', 'class P { ADJUST { say $y } field $y = 1; }', compiles=False, err=r'Global symbol "\$y" requires explicit package name'),
    c('T401-earlier', 'TRAPS; PLAN 17', 'class P { field $x = 2; field $y = $x * 10; method y { $y } } say P->new->y;', out='20\n'),
    c('T402', 'TRAPS; PLAN 17', 'class P { field $x :param :reader = 5; } my $p = P->new("x"); say defined $p->x ? $p->x : "undef";', out='undef\n', err=r'Odd number of arguments passed to "P" constructor'),
    c('T402-hashref', 'TRAPS; PLAN 17', 'class P { field $x :param = 1; } P->new({ x => 2 });', exit=255, err=r'Unrecognised parameters for "P" constructor: HASH\(0x[0-9a-f]+\)'),
    c('T403', 'TRAPS; PLAN 17', 'class P { field $x :param :reader; } say P->new(x => 1, x => 2)->x;', out='2\n'),
    c('T404', 'TRAPS; PLAN 17', 'class P { field $x :param; } P->new(x => 1, y => 2);', exit=255, err=r'^Unrecognised parameters for "P" constructor: y at claim\.pl line 3\.\n$'),
    c('T404-required', 'TRAPS; PLAN 17', 'class P { field $x :param; } P->new;', exit=255, err=r'''^Required parameter 'x' is missing for "P" constructor at claim\.pl line 3\.\n$'''),
    c('T404-caught', 'TRAPS; PLAN 17', 'class P { field $x :param; } try { P->new } catch ($e) { say "caught" }', out='caught\n'),
    c('17-param-default-skipped', 'PLAN 17', 'class P { field $x :param = do { say "init"; 1 }; method x { $x } } say P->new(x => 5)->x; say P->new->x;', out='5\ninit\n1\n'),
    c('17-param-defined-or', 'PLAN 17', 'class P { field $x :param //= 7; field $y :param ||= 8; method show { say "$x $y" } } P->new(x => undef, y => 0)->show;', out='7 8\n'),
    c('17-param-parent', 'PLAN 17', 'class A { field $x :param :reader; } class B :isa(A) { field $y :param :reader; } my $b = B->new(x => 1, y => 2); say $b->x, $b->y;', out='12\n'),
    c('17-param-collide', 'PLAN 17', 'class A { field $x :param; } class B :isa(A) { field $z :param(x); }', exit=255, err=r'Cannot assign :param\(x\) to field \$z because that name is already in use'),
    c('17-param-array', 'PLAN 17', 'class P { field @a :param; }', exit=255, err=r'Only scalar fields can take a :param attribute'),
    c('17-adjust-return', 'PLAN 17', 'class P { field $x = 1; ADJUST { return; $x = 2 } ADJUST { $x .= "b" } method x { $x } } say P->new->x;', out='1b\n'),
    c('17-adjust-die', 'PLAN 17', 'class P { ADJUST { die "no\\n" } } try { P->new } catch ($e) { print "caught $e" }', out='caught no\n'),
    c('17-field-fresh', 'PLAN 17', 'class P { field @a = (1); method push($v) { push @a, $v; scalar @a } } my $p = P->new; my $q = P->new; $p->push(2); say $q->push(3);', out='2\n'),
    c('17-field-class', 'PLAN 17', 'class P { field $k = __CLASS__; method k { $k } } class Q :isa(P) { } say P->new->k, Q->new->k;', out='PQ\n'),
    # ---- calls (TRAPS T405 to T407, T411, T417)
    c('T405', 'TRAPS; PLAN 17', 'class P { field $n :param; method m($a) { "$n:$a" } } my $o = P->new(n => 1); say $o->m(($o = P->new(n => 2)) ? "x" : "y");', out='2:x\n'),
    c('T405-order', 'TRAPS; PLAN 17', 'class P { field $n :param; method m($a) { "$n:$a" } } sub inv() { say "inv"; P->new(n => 1) } sub arg() { say "arg"; 2 } say inv()->m(arg());', out='inv\narg\n1:2\n'),
    c('T406', 'TRAPS; PLAN 17', 'class A { method v { return (1, 2, 3) } } class B { method v { return 7 } } for my $o (A->new, B->new) { my $s = $o->v; say $s }', out='3\n7\n'),
    c('T406-array', 'TRAPS; PLAN 17', 'class P { method parts { my @p = ("a", "b"); return @p } method count { my $c = $self->parts; return $c } } say P->new->count;', out='2\n'),
    c('T407', 'TRAPS; PLAN 17', 'sub P() { "sub" } class P { method m { 3 } } say P->new->m;', exit=255, err=r'Can\'t locate object method "new" via package "sub"'),
    c('T411-class', 'TRAPS; PLAN 17', 'class P { method m { 1 } } P->m;', exit=255, err=r'^Cannot invoke method "m" on a non-instance at claim\.pl line 3\.\n$'),
    c('T411-sub', 'TRAPS; PLAN 17', 'class P { field $x :param :reader; sub make($class, $v) { $class->new(x => $v) } } say P->make(3)->x; say P->new(x => 1)->make(4)->x;', out='3\n4\n'),
    c('T411-new-on-object', 'TRAPS; PLAN 17', 'class P { field $x :param :reader; } my $p = P->new(x => 1); say $p->new(x => 2)->x;', out='2\n'),
    c('T411-function', 'TRAPS; PLAN 17', 'class P { method m { "m " . ref $self } } class Q { } say P::m(P->new); P::m(Q->new);', out='m P\n', exit=255, err=r'Cannot invoke a method of "P" on an instance of "Q"'),
    c('T411-field-in-sub', 'TRAPS; PLAN 17', 'class P { field $x = 1; sub f { $x } }', exit=255, err=r'Field \$x is not accessible outside a method'),
    c('T417', 'TRAPS; PLAN 17', 'class A { method m { "A" } } class B :isa(A) { method m { "B" . $self->next::method() } } say B->new->m;', exit=255, err=r'Can\'t locate object method "method" via package "next"'),
    c('17-super', 'PLAN 17', 'class A { method m { "A" } } class B :isa(A) { method m { "B" . $self->SUPER::m() } } say B->new->m;', out='BA\n'),
    c('17-missing', 'PLAN 17', 'class P { } P->new->nope;', exit=255, err=r'^Can\'t locate object method "nope" via package "P" at claim\.pl line 3\.\n$'),
    c('17-undef', 'PLAN 17', 'class P { method m { 1 } } my $u; $u->m;', exit=255, err=r'^Can\'t call method "m" on an undefined value at claim\.pl line 3\.\n$'),
    c('17-unblessed', 'PLAN 17', 'my $r = [1]; $r->m;', exit=255, err=r'Can\'t call method "m" on unblessed reference'),
    c('17-string-class', 'PLAN 17', 'class P { method m { 1 } } my $c = "P"; say ref $c->new;', out='P\n'),
    c('17-lexical-method', 'PLAN 17', 'class P { my method secret { 7 } method pub { $self->&secret() + 1 } } say P->new->pub; P->new->secret;', out='8\n', exit=255, err=r'Can\'t locate object method "secret" via package "P"'),
    c('17-method-nosig', 'PLAN 17', 'class P { method m { "ok" } } say P->new->m(1, 2, 3);', out='ok\n'),
    c('17-call-forms', 'PLAN 17', 'class P { field $n :param :reader; method m($x = 0) { 5 + $x } method next { P->new(n => $n + 1) } } my $p = P->new(n => 1); say $p->m + 1; say $p->m -1; say $p->m (1); say $p->next->next->n;', out='6\n4\n6\n3\n'),
    c('17-builtin-names', 'PLAN 17', 'class P { method keys { "k" } method length { "l" } method say { "s" } } my $p = P->new; say $p->keys, $p->length, $p->say;', out='kls\n'),
    c('17-used-before', 'PLAN 17', 'say Q->new->m; class Q { method m { 3 } }', out='3\n'),
    c('17-indirect', 'PLAN 17', 'class P { } my $p = new P;', compiles=False, err=r'syntax error'),
    # ---- the class block (TRAPS T408 to T410, T413, T419)
    c('T408', 'TRAPS; PLAN 17', 'say Q->new->inc; class Q { my $c = 10; method inc { ++$c } }', out='1\n'),
    c('T408-after', 'TRAPS; PLAN 17', 'class Q { my $c = 10; method inc { ++$c } } say Q->new->inc;', out='11\n'),
    c('T408-adjust', 'TRAPS; PLAN 17', 'my $q = Q->new; class Q { my $x = do { say "body"; 5 }; ADJUST { say "adjust ", defined $x ? $x : "undef" } }', out='adjust undef\nbody\n'),
    c('T408-statements', 'TRAPS; PLAN 17', 'say "before"; class Q { say "in class body"; method m { 1 } } say "after";', out='before\nin class body\nafter\n'),
    c('T409', 'TRAPS; PLAN 17', 'class P { method m { 1 } method m { 2 } } say P->new->m;', out='2\n', err=r'Method m redefined'),
    c('T409-reader', 'TRAPS; PLAN 17', 'class P { field $x :reader = 1; method x { 2 } } say P->new->x;', out='2\n', err=r'Method x redefined'),
    c('T409-new', 'TRAPS; PLAN 17', 'class P { method new { "mine" } } say P->new;', exit=255, err=r'(?s)Subroutine new redefined.*Cannot invoke method "new" on a non-instance'),
    c('T409-reopen', 'TRAPS; PLAN 17', 'class P { } class P { }', exit=255, err=r'Cannot reopen existing class "P"'),
    c('T409-package', 'TRAPS; PLAN 17', 'class P { method m { 1 } } package P { sub f { 2 } } say P->new->m, P::f();', out='12\n'),
    c('T410', 'TRAPS; PLAN 17', 'class B :isa(A) { } class A { }', exit=2, err=r"Can't locate A\.pm in @INC"),
    c('T410-version', 'TRAPS; PLAN 17', 'class A 1.5 { } class B :isa(A 2.0) { }', exit=255, err=r'A version 2\.0 required--this is only version 1\.5'),
    c('T413', 'TRAPS; PLAN 17', 'class P { method m { $self = 1; ref \\$self } } say P->new->m;', out='SCALAR\n'),
    c('T419', 'TRAPS; PLAN 17', 'class P { method m; method n { 1 } } say P->new->n; P->new->m;', out='1\n', exit=255, err=r'Undefined subroutine &P::m called'),
    c('17-stmt-form', 'PLAN 17', 'class P; field $x :reader = 4; method m { $x } package main; say P->new->m;', out='4\n'),
    c('17-version', 'PLAN 17', 'class P 1.23 { } say P->VERSION;', out='1.23\n'),
    c('17-shadow-field', 'PLAN 17; TRAPS T56', 'class A { field $x :reader = 1; } class B :isa(A) { field $x = 2; method bx { $x } } my $b = B->new; say $b->x, $b->bx;', out='12\n'),
    c('17-field-list-scalar', 'PLAN 17', 'class P { field $x = (4, 5, 6); method x { $x } } say P->new->x;', out='6\n', err=r'Useless use of a constant'),
    c('17-field-hash-odd', 'PLAN 17', 'class P { field %h = (1, 2, 3); method k { join ",", sort keys %h } } say P->new->k;', out='1,3\n', err=r'Odd number of elements in hash field initialization'),
    # ---- readers and writers (TRAPS T418)
    c('T418', 'TRAPS; PLAN 17', 'class P { field @a :reader = (4, 5, 6); field %h :reader = (k => 1); } my $p = P->new; my @l = $p->a; my $n = $p->a; say "@l|$n"; my %h = $p->h; say join ",", %h;', out='4 5 6|3\nk,1\n'),
    c('17-reader-name', 'PLAN 17', 'class P { field $x :reader(get_x) = 3; } say P->new->get_x;', out='3\n'),
    c('17-reader-copy', 'PLAN 17', 'class P { field @a :reader = (1, 2); method show { "@a" } } my $p = P->new; my @l = $p->a; $l[0] = 9; say $p->show;', out='1 2\n'),
    c('17-writer', 'PLAN 17', 'class P { field $x :reader :writer = 3; } my $p = P->new; my $r = $p->set_x(9); say $p->x, ref $r;', out='9P\n'),
    c('17-writer-array', 'PLAN 17', 'class P { field @a :writer; }', exit=255, err=r'Cannot apply a :writer attribute to a non-scalar field'),
    # ---- fields as containers (TRAPS T412)
    c('T412', 'TRAPS; PLAN 17', 'class P { field @a = (1, 2, 3); method go { for my $v (@a) { push @a, 9 if $v == 1; last if @a > 5 } "@a" } } say P->new->go;', out='1 2 3 9\n'),
    c('17-field-ref', 'PLAN 17', 'class P { field @a = (1); field $x = 1; method r { \\@a } method s { \\$x } method show { "@a $x" } } my $p = P->new; push $p->r->@*, 2; ${ $p->s } = 5; say $p->show;', out='1 2 5\n'),
    # ---- objects as values (TRAPS T414 to T416)
    c('T414', 'TRAPS; PLAN 17', 'class P { } my $p = P->new; say "$p" =~ /^P=OBJECT\\(0x[0-9a-f]+\\)$/ ? "address" : "other"; say $p + 0 > 0 ? "number" : "no"; my %h = ($p => 1); say((keys %h)[0] =~ /^P=OBJECT/ ? "key" : "other");', out='address\nnumber\nkey\n'),
    c('T414-die', 'TRAPS; PLAN 17', 'class E { } die E->new;', exit=255, err=r'^E=OBJECT\(0x[0-9a-f]+\)$'),
    c('T414-caught', 'TRAPS; PLAN 17', 'class E { field $msg :param :reader; } try { die E->new(msg => "boom") } catch ($e) { say ref $e, " ", $e->msg, " ", ($e isa E) ? 1 : 0 }', out='E boom 1\n'),
    c('T415', 'TRAPS; PLAN 17', 'class P { } say((P->new isa Object) ? 1 : 0); class Object { } class Class { } class Role { } say "declared";', out='0\ndeclared\n'),
    c('T416', 'TRAPS; PLAN 17', 'class P { } my $p = P->new; say $p->isa("P") ? 1 : 0, defined $p->can("isa") ? 1 : 0, $p->DOES("P") ? 1 : 0, defined(P->VERSION) ? "v" : "-";', out='111-\n'),
    c('T416-own', 'TRAPS; PLAN 17', 'class P { method isa($c) { "mine" } } say P->new->isa("P");', out='mine\n'),
    c('T416-destroy', 'TRAPS; PLAN 17', 'class P { method DESTROY { say "bye" } } { my $p = P->new; } say "after";', out='bye\nafter\n'),
    c('17-object', 'PLAN 17', 'class P { } my $p = P->new; my $q = P->new; my $r = $p; say $p == $r ? "same" : "diff", $p == $q ? "same" : "diff"; say ref $p, builtin::reftype($p), builtin::blessed($p); say $p ? "true" : "false";', out='samediff\nPOBJECTP\ntrue\n'),
    c('17-isa', 'PLAN 17', 'class A { } class B :isa(A) { } my $b = B->new; say $b isa A ? 1 : 0, $b isa B ? 1 : 0, A->new isa B ? 1 : 0; my $s = "A"; my $u; say $s isa A ? 1 : 0, $u isa A ? 1 : 0, (A->new isa Nope) ? 1 : 0;', out='110\n000\n'),
    c('17-say-object', 'PLAN 17', 'class P { } say P->new;', outre=r'P=OBJECT\(0x[0-9a-f]+\)\n'),
    # ---- roles, in the roles perl (TRAPS T420, T421; PLAN 17b)
    c('17b-role', 'PLAN 17', 'role R { method hi { "hi " . ref $self } } class C :does(R) { } say C->new->hi;', out='hi C\n', roles=True),
    c('17b-required', 'PLAN 17', 'role R { method name; method greet { "hello " . $self->name } } class C :does(R) { method name { "c" } } say C->new->greet;', out='hello c\n', roles=True),
    c('17b-required-missing', 'PLAN 17', 'role R { method name; } class C :does(R) { }', exit=255, err=r'''Method 'name' is required but not provided by "C"''', roles=True),
    c('17b-conflict', 'PLAN 17', 'role R1 { method m { 1 } } role R2 { method m { 2 } } class C :does(R1, R2) { }', exit=255, err=r'''Method 'm' conflicts between "R1" and "R2"''', roles=True),
    c('17b-class-wins', 'PLAN 17', 'role R { method m { "role" } } class C :does(R) { method m { "class" } } say C->new->m;', out='class\n', roles=True),
    c('17b-field', 'PLAN 17', 'role R { field $count = 0; method inc { ++$count } } class C :does(R) { } my $c = C->new; $c->inc; say $c->inc;', out='2\n', roles=True),
    c('17b-field-param', 'PLAN 17', 'role R { field $n :param :reader; } class C :does(R) { } say C->new(n => 3)->n;', out='3\n', roles=True),
    c('17b-field-conflict', 'PLAN 17', 'role R { field $x; } class C :does(R) { field $x; }', exit=255, err=r'''Field '\$x' conflicts between "C" and "R"''', roles=True),
    c('17b-field-private', 'PLAN 17', 'role R { field $x = 5; } class C :does(R) { method m { $x } }', compiles=False, err=r'Global symbol "\$x" requires explicit package name', roles=True),
    c('17b-does', 'PLAN 17', 'role R { } class C :does(R) { } class D { } say((C->new does R) ? 1 : 0, (D->new does R) ? 1 : 0, (C->new isa R) ? 1 : 0, C->new->DOES("R") ? 1 : 0);', out='1001\n', roles=True),
    c('T420', 'TRAPS; PLAN 17', 'role R { field $r = do { say "R.field"; 1 }; ADJUST { say "R.adjust" } } class C :does(R) { field $c = do { say "C.field"; 2 }; ADJUST { say "C.adjust" } } C->new;', out='R.field\nC.field\nC.adjust\nR.adjust\n', roles=True),
    c('T421', 'TRAPS; PLAN 17', 'role R { sub helper { "h" } method m { helper() } } class C :does(R) { } say C->new->m; say C->can("helper") ? "composed" : "not";', out='h\nnot\n', roles=True),
    c('17b-role-does-role', 'PLAN 17', 'role A { method a { "a" } } role B :does(A) { method b { "b" } } class C :does(B) { } my $c = C->new; say $c->a, $c->b, ($c does A) ? 1 : 0;', out='ab1\n', roles=True),
    c('17b-diamond', 'PLAN 17', 'role A { method a { "a" } } role B :does(A) { } role D :does(A) { } class C :does(B, D) { } say C->new->a;', out='a\n', roles=True),
    c('17b-role-new', 'PLAN 17', 'role R { } R->new;', exit=255, err=r'Can\'t locate object method "new" via package "R"', roles=True),
    c('17b-role-later', 'PLAN 17', 'class C :does(R) { } role R { }', exit=2, err=r"Can't locate R\.pm in @INC", roles=True),
    c('17b-inherited', 'PLAN 17', 'role R { method r { "r" } } class A :does(R) { } class B :isa(A) { } say B->new->r, (B->new does R) ? 1 : 0;', out='r1\n', roles=True),
]
