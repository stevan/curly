# kind: fault
# perl dies: Not an ARRAY reference.
use v5.42;
my $r = {};
say "a";
$#{$r} = 1;
