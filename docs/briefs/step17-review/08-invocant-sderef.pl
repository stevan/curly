use v5.42;
use experimental 'class';
class P { field $n :param :reader; method m($x) { "$n:$x" } } my $o = P->new(n=>1); my $r = \$o; say $$r->m(($o = P->new(n=>2)) ? "x":"y");
