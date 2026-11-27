# kind: fault
# model: t/models/obj.py
use v5.42;
use experimental 'class';
class P { field $x :param :reader; field $y :param = 0; method m($v) { $v } method many { return (1, 2) } }
say(1);
my $v = P->new(x => 1)->many;
say(2);
