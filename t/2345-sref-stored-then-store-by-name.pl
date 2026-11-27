# kind: refused
# perl runs it: '77' (the assignment is the scalar itself, read late).
use v5.42;
my $x = 1;
my $r = \$x;
say(($r->$* = 5), ($x = 7));
