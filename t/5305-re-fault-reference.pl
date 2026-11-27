# kind: fault
# perl matches the address, ARRAY(0x...), in silence (D112).
use v5.42;
my $r = [1];
say $r =~ /x/ ? 1 : 0;
