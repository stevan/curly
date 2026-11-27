# kind: refused
# perl prints 9 (R17-06-new-element-late): the argument is read at its field's turn.
use v5.42;
use experimental 'class';
my @a = (1, 2);
class P { field $z = ($a[0] = 9); field $x :param :reader; }
say P->new(x => $a[0])->x;
