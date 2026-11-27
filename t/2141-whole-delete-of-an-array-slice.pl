# kind: refused
# perl runs it, and says nothing.
use v5.42;
my $r = [1, 2];
delete $r->@[0];
