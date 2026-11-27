# kind: refused
# perl does not compile it: syntax error at -e line 3, near "qq<$q->{k"
use v5.42;
my $q = {k => 1};
say qq<$q->{k}>;
