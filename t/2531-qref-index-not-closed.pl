# kind: refused
# perl does not compile it: Missing right curly or square bracket at -e line 3, within string
use v5.42;
my $r = [1, 2];
say "$r->[0";
