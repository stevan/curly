# kind: refused
# perl runs it: 'ARRAY(0x...)->[0]\n'.
use v5.42;
my $a = [1];
my $s = \$a;
say "$s->$*->[0]";
