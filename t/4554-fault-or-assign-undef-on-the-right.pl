# kind: fault
# perl warns: Use of uninitialized value $u in numeric bitwise or.
use v5.42;
my $x = 1;
my $u;
$x |= $u;
