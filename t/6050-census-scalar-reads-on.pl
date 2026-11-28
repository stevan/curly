# kind: refused
# perl runs it: '4' (scalar(@a + 1)).
use v5.42;
my @a = (1, 2, 3);
say scalar @a + 1;
