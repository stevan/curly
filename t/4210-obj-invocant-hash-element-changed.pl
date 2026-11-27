# kind: refused
# perl prints 2:x (R17-08-invocant-helem).
use v5.42;
use experimental 'class';
class P { field $n :param; method m($x) { "$n:$x" } }
my %h = (k => P->new(n => 1));
say $h{k}->m(($h{k} = P->new(n => 2)) ? "x" : "y");
