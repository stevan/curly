# kind: refused
# perl runs it: '0[0]\n'.
use v5.42;
my $r = [1];
say "$r->$#*[0]";
