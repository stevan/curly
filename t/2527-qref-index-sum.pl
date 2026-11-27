# kind: refused
# perl runs it: '2\n'.
use v5.42;
my $r = [1, 2];
my $i = 0;
say "$r->[$i+1]";
