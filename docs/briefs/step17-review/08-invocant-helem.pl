use v5.42;
use experimental 'class';
class P { field $n :param :reader; method m($x) { "$n:$x" } } my %h = (k => P->new(n=>1)); say $h{k}->m(($h{k} = P->new(n=>2)) ? "x" : "y");
