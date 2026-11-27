# kind: refused
# perl does not compile it: syntax error at -e line 3, near "]{a"
use v5.42;
my $r = [{a => 1}];
say "$r->@[0]{a}";
