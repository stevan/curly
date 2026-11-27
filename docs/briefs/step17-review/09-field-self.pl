use v5.42;
use experimental 'class';
class P { field $self = 1; method m { $self } } say P->new->m;
