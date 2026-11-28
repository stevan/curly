# kind: dies
# perl dies zero: D146 refused it, and D260 takes it in.
use v5.42;
my $x = 0;
$x or die "zero\n";
