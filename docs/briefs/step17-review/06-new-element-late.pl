use v5.42;
use experimental 'class';
my @a = (1, 2);
class P { field $z = ($a[0] = 9); field $x :param :reader; }
say P->new(x => $a[0])->x;
