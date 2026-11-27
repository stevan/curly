# kind: refused
# perl dies: Field already has a parameter name, cannot add another.
use v5.42;
use experimental 'class';
class P { field $x :param :param; }
