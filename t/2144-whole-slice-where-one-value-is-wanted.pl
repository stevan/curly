# kind: refused
# perl runs it, and says nothing (the last element).
use v5.42;
my $r = [1, 2];
my $x = $r->@[0, 1];
