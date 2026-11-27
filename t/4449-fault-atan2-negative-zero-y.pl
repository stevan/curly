# kind: fault
# perl prints -pi, or pi once the zero has been used as an integer (T484).
use v5.42;
my $z = 0.0;
say atan2(-$z, -1);
