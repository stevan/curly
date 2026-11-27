use v5.42;
use experimental 'class';
class P { field $n :param; method m($x) { "$n" } } my $u; my $o = P->new(n=>1); say(($u // $o)->m(($o = P->new(n=>2)) ? 1 : 0));
