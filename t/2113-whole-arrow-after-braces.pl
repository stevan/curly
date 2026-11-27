# kind: refused
# perl dies: Can't use an array as a reference.
use v5.42;
my $r = [1, 2];
say @{$r}->[0];
