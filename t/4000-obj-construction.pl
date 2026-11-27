# model: t/models/obj.py
use v5.42;
use experimental 'class';
my $log = "";
sub do_log($what, $v) {
    $log .= "$what ";
    return $v;
}
class A {
    field $a1 = main::do_log("A.a1", 1);
    field $x :param :reader;
    ADJUST { $log .= "A.adjust1 "; }
    field $a2 :reader = $x + 100;
    ADJUST { $log .= "A.adjust2 "; }
}
class B :isa(A) {
    field $b1 :param :reader //= "b1d";
    field $b2 :param :reader ||= "b2d";
    ADJUST { $log .= "B.adjust "; }
}
class C :isa(B) {
    field @items :reader = (1, 2, 3);
    field %opts = (k => "v");
    field $total :reader = 0;
    ADJUST { $total = scalar(@items); $log .= "C.adjust "; }
    method opt($k) { $opts{$k} }
}
class D {
    field $v :param :reader = main::do_log("D.default", 9);
}
class W {
    field $n :reader :writer = 1;
    field $m :reader :writer(put_m) = "m";
}
my $c = C->new(x => 5);
say $log;
say join ",", $c->x, $c->a2, $c->b1, $c->b2, $c->total;
say join ",", $c->items;
say $c->opt("k");
$log = "";
my $d = C->new(b2 => 0, x => 7, b1 => undef);
say $log;
say join ",", $d->x, $d->b1, $d->b2;
my $e = C->new(b1 => "given", x => 1, b2 => "also");
say join ",", $e->b1, $e->b2;
$log = "";
my $dv = D->new(v => 3)->v;
say "$dv [$log]";
my $dd = D->new->v;
say "$dd [$log]";
my $w = W->new;
say $w->set_n(5)->put_m("q")->n, $w->m;
my $copy = $w->n;
$copy = 99;
say $w->n;
my $c1 = C->new(x => 1);
my $c2 = C->new(x => 2);
say $c1->x, $c2->x, $c1->a2, $c2->a2;
