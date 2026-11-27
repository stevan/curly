use v5.42;
use experimental 'class';
class P { field $n :param; method m($x) { "$n" } } my $o = P->new(n=>1); say((1 ? $o : undef)->m(($o = P->new(n=>2)) ? 1 : 0));
