# kind: refused
# perl runs it: '1\n'.
use v5.42;
my $q = {1 => 1};
say "$q->{1}";
