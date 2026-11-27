# kind: refused
# perl runs it, and says nothing.
use v5.42;
my @l = (2, 1);
my @s = sort { my $p = \$a; $p->$* <=> $b } @l;
