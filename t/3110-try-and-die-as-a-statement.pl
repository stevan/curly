# kind: dies
# perl dies one: a statement, and, die (D260 since step 16d).
use v5.42;
my $x = 1;
$x and die "one\n";
