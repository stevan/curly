# kind: refused
# perl runs it, and says nothing: a reference to a new scalar that holds a reference.
use v5.42;
my $x = 1;
my $s = \\$x;
