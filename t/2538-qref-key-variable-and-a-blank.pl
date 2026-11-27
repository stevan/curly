# kind: refused
# perl runs it: '1\n'.
use v5.42;
my $q = {k => {k => 1}};
my $k = "k";
say "$q->{k}{$k }";
