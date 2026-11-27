# kind: fault
# perl exits 255 here, the C library not setting errno for atan2 (T472): the language marks every underflow.
use v5.42;
my $v = 1e-300;
my $x = atan2($v, 1e10);
die "x\n";
