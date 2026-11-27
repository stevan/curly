# kind: refused
# perl chomps both.
use v5.42;
chomp(my ($x, $y) = ("a\n", "b\n"));
