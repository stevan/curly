# kind: fault
# model: t/models/obj.py
use v5.42;
use experimental 'class';
class F { field @a = (1, 2); method go { for my $v (@a) { push @a, 3; last } return } }
say(1);
F->new->go;
say(2);
