# kind: refused
# perl runs it, and says nothing: a list of a reference to each element.
use v5.42;
my $r = [1, 2];
my @refs = \$r->@*;
