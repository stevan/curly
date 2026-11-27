# kind: fault
# model: t/models/obj.py
use v5.42;
use experimental 'class';
class W { field $n :writer = 1; }
say(1);
W->new->set_n;
say(2);
