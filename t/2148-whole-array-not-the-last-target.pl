# kind: refused
# perl runs it, and says nothing: the array takes every value.
use v5.42;
my $r = [1, 2];
my $x;
($r->@*, $x) = (1, 2);
