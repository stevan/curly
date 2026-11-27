# check: ok
# A hash as the last parameter of a sub with no name: declared, and
# filled, whatever the order (step 14).
use v5.42;
my $f = sub ($x, %o) { return $x . scalar(keys %o) . $o{b} };
say $f->(1, a => 1, b => 2, c => 3);
