# kind: fault
# perl warns: Use of uninitialized value $x in numeric bitwise and (T477).
use v5.42;
my $x;
$x &= 5;
