# kind: refused
# perl prints 2:x (R17-08-invocant-chain).
use v5.42;
use experimental 'class';
class P { field $n :param; method m($x) { "$n:$x" } }
my $r = [P->new(n => 1)];
say $r->[0]->m(($r->[0] = P->new(n => 2)) ? "x" : "y");
