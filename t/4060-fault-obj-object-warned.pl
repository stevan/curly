# kind: fault
# model: t/models/obj.py
use v5.42;
use experimental 'class';
class Q { method only { 1 } }
say(1);
my $o = Q->new;
warn $o;
say(2);
