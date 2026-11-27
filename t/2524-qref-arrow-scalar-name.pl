# kind: refused
# perl runs it: 'ARRAY(0x...)->2\n'.
use v5.42;
my $r = [1];
my $x = 2;
say "$r->$x";
