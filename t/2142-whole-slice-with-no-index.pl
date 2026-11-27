# kind: refused
# perl does not compile it: syntax error.
use v5.42;
my $r = [1, 2];
my @c = $r->@[];
