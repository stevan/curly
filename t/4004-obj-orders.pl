# What the review of step 17 and its proposal ran, written out with
# perl's answers (make oracle): the two passes of construction (T400), an
# argument read at its field's turn and a name read at the call (T427),
# the invocant read at the call in every shape (T405, T429), SUPER as the
# parent of the class written in (T431), a parent's ADJUST dispatching to
# the child's method (R17-17), __CLASS__->new from a subclass, closures
# over fields (17-clo-*), the reference to a scalar field (T432), and
# methods named for perl's words.
use v5.42;
use experimental 'class';
my $log = "";
sub note($what) {
    $log .= "$what ";
    return 1;
}
my $v = "old";
sub change_v() {
    $v = "new";
    return 1;
}
my $k = "x";
sub change_k() {
    $k = "y";
    return 1;
}
class A {
    field $a1 = main::note("A.a1");
    ADJUST { main::note("A.adjust") }
    field $a2 = main::note("A.a2");
    method k { "A" }
    method hi { "A.hi " . $self->name }
    method name { "a" }
}
class B :isa(A) {
    field $b1 = main::note("B.b1");
    ADJUST { main::note("B.adjust") }
    method k { "B" }
    method m { $self->SUPER::k() }
    method name { "b" }
}
class C :isa(B) {
    method again { __CLASS__->new }
}
class Late {
    field $w = main::change_v();
    field $got :param :reader;
}
class Keys {
    field $w = main::change_k();
    field $x :param :reader = "dx";
    field $y :param :reader = "dy";
}
class Pt {
    field $n :param :reader;
    method m($t) { "$n:$t" }
}
class Clo {
    field $n = 1;
    field @a = (1);
    field $get = sub { $n };
    method f { sub { $n } }
    method set { sub ($x) { $n = $x; return } }
    method push { sub { push @a, 2; scalar(@a) } }
    method count { scalar(@a) }
    method both { $get->() }
    method r { \$n }
    method one { sub { 1 } }
    method mine { sub { $self } }
}
class Words {
    method keys { "k" }
    method length { "l" }
    method say { "s" }
    method last { "z" }
    method x { "x" }
    method q { "q" }
    method not { "n" }
    method print { "p" }
}
C->new;
say $log;
say C->new->m, C->new->hi, " ", ref C->new->again;
say Late->new(got => $v)->got;
my $kk = Keys->new($k => 5);
say $kk->x, " ", $kk->y;
my $o = Pt->new(n => 1);
say $o->m(($o = Pt->new(n => 2)) ? "x" : "y");
my $p = Pt->new(n => 1);
say((1 ? $p : undef)->m(($p = Pt->new(n => 3)) ? "x" : "y"));
my $u;
my $q = Pt->new(n => 1);
say(($u // $q)->m(($q = Pt->new(n => 4)) ? "x" : "y"));
my $s;
say(($s = Pt->new(n => 1))->m(($s = Pt->new(n => 5)) ? "x" : "y"));
my $c = Clo->new;
my $f = $c->f;
$c->set->(7);
say $f->(), $c->both, $c->push->(), $c->count;
${ $c->r } = 9;
say $f->(), $c->r == $c->r ? "same" : "diff", $c->r == Clo->new->r ? "same" : "diff";
say $c->one == $c->one ? "same" : "diff", $c->mine == $c->mine ? "same" : "diff";
say ref \$c, ref $c;
my $w = Words->new;
say $w->keys, $w->length, $w->say, $w->last, $w->x, $w->q, $w->not, $w->print;
