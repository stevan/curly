# kind: refused
# perl runs it, and says nothing.
use v5.42;
my $r = [1, 2];
my $x;
($x, $r->@[0]) = (1, 2);
