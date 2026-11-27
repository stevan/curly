# kind: refused
# perl does not compile it: Bareword found where operator expected.
use v5.42;
my $q = {k => 1};
say "$q->{k j}";
