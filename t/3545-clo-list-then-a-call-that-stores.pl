# kind: refused
# perl runs it: '9 0' (T364).
use v5.42;
my $x = 1;
my $bump = sub { $x = 9; return 0 };
my @l = ($x, $bump->());
say "@l";
