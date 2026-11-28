# kind: refused
# perl prints garbage: '70' (T603).
use v5.42;
my $z = 0;
my @l = ($z ? 0 : (7) x 1);
say scalar(@l), " @l";
