use v5.42;
use experimental 'class';
class Q { method who { "Q" } } class P { method who { "P" } method m { my $r = \$self; $$r = Q->new; $self->who } } say P->new->m;
