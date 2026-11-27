# kind: refused
# perl warns: Useless use of private variable in void context.
use v5.42;
my $x = 1;
my $r = \$x;
my $s = \$x;
say ${ $r, $s };
