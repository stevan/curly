# kind: fault
# model: t/models/obj.py
use v5.42;
use experimental 'class';
class G { field @a = (1, 2); method more { push @a, 3; return } method go { for my $v (@a) { $self->more; last } return } }
say(1);
G->new->go;
say(2);
