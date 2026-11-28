# kind: refused
# perl runs both assignments, and warns: Found = in conditional (D56).
use v5.42;
my ($x, $y);
$x = 1 and $y = 2;
