# kind: refused
# perl runs it, and says nothing: ${ $r } holds a reference (T349).
use v5.42;
my $r;
(${ $r }, my $z) = ($r, 1);
