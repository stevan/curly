# kind: refused
# perl runs it: '2'.
use v5.42;
my $r = [1, 2];
for my $x ($r->@*) {
    my $y;
    ($y, $r->@*) = (1, 2);
    last;
}
