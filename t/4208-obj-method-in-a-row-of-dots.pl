# kind: refused
# perl reads $n late: the method's store shows.
use v5.42;
use experimental 'class';
my $n = 1;
class P { method bump { $n = 5; return "!" } }
say $n . P->new->bump;
