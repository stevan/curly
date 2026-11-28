# kind: refused
# perl runs it: a list assignment to $#a, which cuts the array.
use v5.42;
my @a = (1, 2, 3);
($#a) = 0;
