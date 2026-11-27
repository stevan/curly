use v5.42;
use experimental 'class';
class P { method m { my $self = 3; $self } } say P->new->m;
