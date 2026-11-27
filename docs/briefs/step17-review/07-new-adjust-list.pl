use v5.42;
use experimental 'class';
my @a = (1);
class P { ADJUST { $a[0] = 9 } method v { "c" } }
say $a[0], P->new->v;
