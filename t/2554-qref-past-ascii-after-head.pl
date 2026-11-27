# kind: refused
# perl runs it, and warns: Wide character in say
use v5.42;
use utf8;
my $r = [1];
say "$r→[0]";
