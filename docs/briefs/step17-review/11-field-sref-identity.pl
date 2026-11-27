use v5.42;
use experimental 'class';
class P { field $x = 1; method r { \$x } method x { $x } } my $p = P->new; my $q = P->new; ${$p->r} = 5; say $p->x, $q->x; my $r1 = $p->r; my $r2 = $p->r; say $r1 == $r2 ? "same" : "diff";
