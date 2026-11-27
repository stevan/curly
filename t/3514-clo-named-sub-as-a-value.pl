# kind: refused
# perl does not compile it: Illegal declaration of subroutine main::g.
use v5.42;
my $f = sub g { 1 };
