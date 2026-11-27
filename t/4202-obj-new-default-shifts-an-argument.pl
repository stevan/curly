# kind: refused
# perl prints 1 2 3 (R17-06-new-element-shifted): the element shifted out is still the old scalar.
use v5.42;
use experimental 'class';
my @a = (1, 2, 3);
class P { field $z = shift(@a); field $x :param :reader; }
say P->new(x => $a[0])->x, " @a";
