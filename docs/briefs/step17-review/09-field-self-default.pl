use v5.42;
use experimental 'class';
class P { field $self = 1; field $z = $self + 1; method m { $z } } say P->new->m;
