# kind: refused
# perl folds 1 << 2 and warns.
use v5.42;
my $x;
say "y" unless $x = 1 << 2;
