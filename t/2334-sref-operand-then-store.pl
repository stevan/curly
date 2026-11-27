# kind: refused
# perl runs it: '10' (T346).
use v5.42;
my $x = 1;
my $r = \$x;
say(${ $r } + ($x = 5));
