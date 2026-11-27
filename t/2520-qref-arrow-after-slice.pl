# kind: refused
# perl runs it: '1\n'.
use v5.42;
my $r = [[1]];
say "$r->@[0]->[0]";
