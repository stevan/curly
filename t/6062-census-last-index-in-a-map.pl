# kind: refused
# perl runs it: each time round, @a is cut.
use v5.42;
my @a = (1, 2);
my @b = map { $#a = 0 } (1, 2);
