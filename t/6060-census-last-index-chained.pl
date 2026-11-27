# kind: refused
# perl runs it: both arrays cut.
use v5.42;
my @a = (1, 2);
my @b = (1, 2);
$#a = $#b = 0;
