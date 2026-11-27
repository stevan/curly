use v5.42;
use experimental 'class';
class P { field @a = (1..5); method drop { shift @a; 1 } method go { my @g = grep { $self->drop } @a; scalar @g } } say P->new->go;
