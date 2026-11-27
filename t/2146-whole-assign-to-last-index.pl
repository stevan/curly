# kind: refused
# perl runs it, and says nothing: the array is cut to one element.
use v5.42;
my $r = [1, 2];
$r->$#* = 0;
