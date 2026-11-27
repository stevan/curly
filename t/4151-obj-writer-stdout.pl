# kind: refused
# perl runs it: set_x is a method.
use v5.42;
use experimental 'class';
class P { field $x :writer(STDOUT); }
