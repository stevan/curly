use v5.42;
use experimental 'class';
class P { field $x :reader( r) = 1; field $y :reader :reader(q) = 2; } my $p = P->new; say join ",", map { $p->can($_) ? $_ : "-" } qw(r x y q);
