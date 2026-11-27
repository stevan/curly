# kind: refused
# perl runs it: '1\n'.
use v5.42;
my $q = {-k => 1};
say "$q->{-k}";
