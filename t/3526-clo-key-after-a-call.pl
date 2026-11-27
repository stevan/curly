# kind: refused
# perl runs it: '5'.
use v5.42;
my $g = sub { return {a => 5} };
say $g->(){a};
