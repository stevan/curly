# kind: refused
# perl does not compile it: exists argument is not a HASH or ARRAY element.
use v5.42;
my $h = {a => 1};
say exists $h->@{a};
