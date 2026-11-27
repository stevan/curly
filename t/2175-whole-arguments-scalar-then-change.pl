# kind: refused
# perl runs it: '5 2 5'.
use v5.42;
sub f(@a) {
    return "@a";
}
my $x = 1;
my $r = [2];
say f($x, $r->@*, ($x = 5));
