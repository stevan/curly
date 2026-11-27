# kind: refused
# perl runs it: '12\n'.
use v5.42;
my $r = [1, 2];
say sort $r ->@*;
