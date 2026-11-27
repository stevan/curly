# kind: refused
# perl takes *2 for a glob, srand's argument.
use v5.42;
my $x = srand * 2;
