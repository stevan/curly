# kind: fault
# perl reads the string ARRAY(0x...), and warns: Integer overflow in srand.
use v5.42;
my $r = [];
srand($r);
