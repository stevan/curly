# kind: refused
# perl runs it, and says nothing: the reference $r points at.
use v5.42;
my $x = 1;
my $r = \$x;
my $s = \$r->$*;
