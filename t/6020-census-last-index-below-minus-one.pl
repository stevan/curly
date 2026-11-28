# kind: fault
# perl empties the array in silence (T660): '3', then nothing.
use v5.42;
my @a = (1, 2, 3);
say scalar @a;
$#a = -2;
say scalar @a;
