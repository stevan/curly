# kind: refused
# perl runs it, and says nothing: a reference to each element of @l.
use v5.42;
my @l = (1, 2);
my @r = map { \$_ } @l;
