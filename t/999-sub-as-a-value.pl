# A sub with no name is a value, and a call through it (step 14).
use v5.42;
my $f = sub ($x) { return $x; };
say $f->(5);
