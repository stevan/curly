# kind: refused
# perl prints garbage, '70': 0x1 is the integer 1 (T603).
use v5.42;
my $v = 1;
my @l = ($v ? (7) x 0x1 : 0);
say scalar(@l), " @l";
