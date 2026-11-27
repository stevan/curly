# kind: refused
# perl dies when it gets to it: Can't return outside a subroutine.
use v5.42;
my $x = 1;
$x or return;
