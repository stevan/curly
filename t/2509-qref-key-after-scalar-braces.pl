# kind: refused
# perl dies: Not a HASH reference
use v5.42;
my $h = {a => 1};
my $s = \$h;
say "${$s}{a}";
