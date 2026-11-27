use v5.42;
use experimental 'class';
class P { field $x :param(  ) :reader = 1; } say P->new(x => 3)->x;
