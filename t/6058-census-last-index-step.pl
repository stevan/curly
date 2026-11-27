# kind: refused
# perl runs it: the array is one longer.
use v5.42;
my @a = (1, 2, 3);
$#a++;
