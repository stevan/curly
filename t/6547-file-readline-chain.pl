# kind: refused
# perl does not compile it: the angle brackets end at the arrow.
use v5.42;
my $r = [];
my $l = <$r->[0]>;
