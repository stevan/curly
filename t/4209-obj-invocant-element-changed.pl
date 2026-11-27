# kind: refused
# perl prints 2:x (R17-08-invocant-element): the element is read at the call.
use v5.42;
use experimental 'class';
class P { field $n :param; method m($x) { "$n:$x" } }
my @a = (P->new(n => 1));
say $a[0]->m(($a[0] = P->new(n => 2)) ? "x" : "y");
