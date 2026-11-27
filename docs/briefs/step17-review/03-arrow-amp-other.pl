use v5.42;
use experimental 'class';
class P { field $n :param; my method b { "n=$n" } method a($o) { $o->&b() } } say P->new(n=>1)->a(P->new(n=>2));
