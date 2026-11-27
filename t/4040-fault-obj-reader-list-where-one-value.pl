# kind: fault
# model: t/models/obj.py
use v5.42;
use experimental 'class';
class A { field @a :reader = (1, 2); }
say(1);
my $n = A->new->a;
say(2);
