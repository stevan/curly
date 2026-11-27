# kind: refused
# perl warns: Scalar value @a[1] better written as $a[1].
use v5.42;
my @a = (1, 2, 3);
say scalar @a[1];
