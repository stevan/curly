# kind: fault
# perl warns: Use of uninitialized value $x in right bitshift (T477).
use v5.42;
my $x;
$x >>= 1;
