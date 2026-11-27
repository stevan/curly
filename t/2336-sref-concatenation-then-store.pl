# kind: refused
# perl runs it: '5a5' (T346).
use v5.42;
my $x = 1;
my $r = \$x;
my $s = ${ $r } . "a" . ($x = 5);
