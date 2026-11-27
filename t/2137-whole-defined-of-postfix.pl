# kind: refused
# perl does not compile it: Can't use 'defined(@array)'.
use v5.42;
my $r = [1, 2];
say defined $r->@*;
