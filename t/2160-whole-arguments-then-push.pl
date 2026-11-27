# kind: refused
# perl runs it: '3'.
use v5.42;
my $r = [1, 2];
sub f(@x) {
    return scalar(@x);
}
say f($r->@*, push($r->@*, 3));
