# kind: refused
# perl dies: Can't use an undefined value as a SCALAR reference ($a[15]).
use v5.42;
my $x = 1;
my $r = \$x;
my @a = ($r);
say ${ $a[017] };
