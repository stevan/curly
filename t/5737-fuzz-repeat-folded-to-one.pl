# kind: refused
# perl prints garbage, '70': 2 - 1 is folded to 1 as perl compiles (T603).
use v5.42;
my $v = 1;
my @l = ($v ? (7) x (2 - 1) : 0);
say scalar(@l), " @l";
