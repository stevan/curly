# kind: refused
# perl runs it: '55' (T235).
use v5.42;
my $x = 1;
my $r = \$x;
say($x, (${ $r } = 5));
