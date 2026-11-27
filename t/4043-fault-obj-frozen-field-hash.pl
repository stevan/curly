# kind: fault
# model: t/models/obj.py
use v5.42;
use experimental 'class';
class K { field %h = (a => 1); method go { for my $v (values %h) { $h{b} = 2; last } return } }
say(1);
K->new->go;
say(2);
