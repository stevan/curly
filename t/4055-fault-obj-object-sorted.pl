# kind: fault
# model: t/models/obj.py
use v5.42;
use experimental 'class';
class Q { method only { 1 } }
say(1);
my $o = Q->new;
my @l = ($o, $o);
my @s = sort @l;
say(2);
