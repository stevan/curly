# kind: refused
# perl runs it: 'ARRAY(0x...)->@ \n'.
use v5.42;
my $r = [1];
say "$r->@ ";
