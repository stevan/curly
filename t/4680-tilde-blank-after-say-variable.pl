# kind: refused
# perl takes $x for a file handle and dies (T478).
use v5.42;
my $x = -6;
say $x ~ 5;
