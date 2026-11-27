use v5.42;
use experimental 'class';
class P { method m($self) { $self } } say P->new->m(5);
