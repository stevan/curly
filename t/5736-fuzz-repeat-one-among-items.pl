# kind: refused
# perl prints garbage: '970' (T603).
use v5.42;
my $v = 1;
my @l = ($v ? (9, (7) x 1) : 0);
say scalar(@l), " @l";
