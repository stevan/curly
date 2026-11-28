# kind: refused
# perl runs it: the array is two longer.
use v5.42;
my @a = (1, 2, 3);
$#a += 2;
