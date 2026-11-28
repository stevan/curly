# kind: refused
# perl reverses $_, and warns of the undef.
use v5.42;
my $x = scalar reverse;
