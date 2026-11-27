# kind: refused
# perl runs it, and says nothing: $_ is $x itself, which the block stores 9 to.
use v5.42;
my $x = 1;
my $r = \$x;
my @m = map { $r->$* = 9; $_ } ($x);
