# kind: refused
# perl runs it: 'ARRAY(0x...)->[0]\n'.
use v5.42;
my $r = [[1]];
say "$r->@*->[0]";
