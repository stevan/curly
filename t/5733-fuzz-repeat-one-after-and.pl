# kind: refused
# perl prints garbage: '70' (T603).
use v5.42;
my $v = 1;
my @l = ($v && (7) x 1);
say scalar(@l), " @l";
