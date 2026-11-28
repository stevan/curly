# kind: fault
# perl dies: Can't use string ("5") as an ARRAY ref while "strict refs" in use.
use v5.42;
my $r = 5;
$r->$#* = 1;
