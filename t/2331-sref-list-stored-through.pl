# kind: refused
# perl runs it, and says nothing (the last value).
use v5.42;
my $x = 1;
my $r = \$x;
$r->$* = (1, 2);
