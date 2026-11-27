# kind: refused
# perl exits 2.
use v5.42;
my $x = 0;
$x or exit 2;
