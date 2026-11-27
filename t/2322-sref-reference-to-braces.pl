# kind: refused
# perl runs it, and says nothing.
use v5.42;
my $x = 1;
my $r = \$x;
my $s = \${ $r };
