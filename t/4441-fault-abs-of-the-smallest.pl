# kind: fault
# perl gives the unsigned integer 9223372036854775808 (T471).
use v5.42;
my $x = -9223372036854775807;
say abs($x);
$x = $x - 1;
say abs($x);
