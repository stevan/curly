use v5.42;
use experimental 'class';
class P { field $n :param; my method b { "n=$n" } method a($o) { $o->&b() } } class Q { } say P->new(n=>1)->a(Q->new);
