# kind: fault
# perl prints pi, or 0 once the zero has been used as an integer (T79, T484).
use v5.42;
my $z = 0.0;
say atan2(0, $z);
say atan2(0, -$z);
