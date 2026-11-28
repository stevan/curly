# kind: refused
# perl prints garbage: '780' (T603).
use v5.42;
my $z = 0;
my @l = ($z || (7, 8) x 1);
say scalar(@l), " @l";
