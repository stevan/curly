# model: t/models/obj.py
use v5.42;
use experimental 'class';
my $v = "old";
sub bump_v() {
    $v = "new";
    return 1;
}
class Pt {
    field $x :param :reader;
    field $y :param :reader = 0;
    method str { "($x,$y)" }
    method plus($o) { Pt->new(x => $x + $o->x, y => $y + $o->y) }
}
class Err {
    field $msg :param :reader;
}
class Link {
    field $v :param :reader;
    field $next :param :reader = undef;
    method sum { $v + (defined $next ? $next->sum : 0) }
}
class Late {
    field $w = main::bump_v();
    field $got :param :reader;
}
my @pts = (Pt->new(x => 3, y => 1), Pt->new(x => 1, y => 5), Pt->new(x => 2, y => 2));
say join " ", map { $_->str } sort { $a->x <=> $b->x } @pts;
say join " ", map { $_->str } grep { $_->y > 1 } @pts;
say $pts[0]->plus($pts[1])->plus($pts[2])->str;
my %by = map { ($_->x => $_) } @pts;
say $by{2}->str;
my $r = { list => [@pts] };
say $r->{list}[1]->str, $r->{list}->[2]->y;
try { die Err->new(msg => "boom") } catch ($e) { say ref($e), " ", $e->msg, " ", ($e isa Err) ? 1 : 0 }
my $o = Pt->new(x => 1);
say $o->plus(($o = Pt->new(x => 10)) ? Pt->new(x => 100) : undef)->x;
my $o2 = Pt->new(x => 1);
say((1 ? $o2 : undef)->plus(($o2 = Pt->new(x => 20)) ? Pt->new(x => 100) : undef)->x);
say Late->new(got => $v)->got;
my $l = undef;
for my $i (1 .. 90) { $l = Link->new(v => $i, next => $l) }
say $l->sum;
say $l ? "true" : "false", defined($l) ? 1 : 0;
