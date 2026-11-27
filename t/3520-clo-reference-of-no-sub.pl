# kind: refused
# perl runs it, and dies when it is called: Undefined subroutine &main::none.
use v5.42;
my $r = \&none;
