# kind: refused
# perl refuses it: Bareword filehandle not allowed (T513).
use v5.42;
my $l = <FH>;
