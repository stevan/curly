# kind: refused
# perl reads $n late: the store of B's method shows.
use v5.42;
use experimental 'class';
my $n = 1;
class A { method bump { "a" } }
class B { method bump { $n = 5; return "!" } }
say $n . B->new->bump;
