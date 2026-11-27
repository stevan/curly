# kind: refused
# perl does not compile it: syntax error.
use v5.42;
my $h = {a => 1};
my @c = $h->@{};
