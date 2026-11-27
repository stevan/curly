# kind: refused
# perl runs it: '1\n'.
use v5.42;
my $x = 1;
my $r = \$x;
my $q = \$r;
say $q->$*->$*;
