# kind: refused
# perl does not compile it: Experimental push on scalar is now forbidden.
use v5.42;
my $x = 1;
my $r = \$x;
push $r->$*, 1;
