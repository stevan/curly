# kind: refused
# perl runs it: $y and $x undef.
use v5.42;
my $x = 3;
my $y = undef $x;
