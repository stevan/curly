# kind: fault
# model: t/models/obj.py
use v5.42;
use experimental 'class';
class P { field $x :param :reader; field $y :param = 0; method m($v) { $v } method many { return (1, 2) } }
class R :isa(P) { field $z :param; }
say(1);
R->new(x => 1);
say(2);
