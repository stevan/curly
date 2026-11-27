# kind: refused
# perl runs it, and says nothing ($n is the count of the right side, 2).
use v5.42;
my $r = [1, 2];
my $n = ($r->@* = (5, 6));
