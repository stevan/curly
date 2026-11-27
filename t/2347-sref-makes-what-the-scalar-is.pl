# kind: refused
# perl runs it, and says nothing: $x->[0] is an array, $x itself.
use v5.42;
my $x;
my $r = \$x;
$x->[0] = $r->$*;
