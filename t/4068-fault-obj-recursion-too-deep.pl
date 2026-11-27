# kind: fault
# model: t/models/obj.py
use v5.42;
use experimental 'class';
no warnings 'recursion';
class N { field $d :param; field $kid = $d < 4000 ? N->new(d => $d + 1) : undef; }
say(1);
N->new(d => 0);
say(2);
