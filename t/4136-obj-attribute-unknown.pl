# kind: refused
# perl dies: Unrecognized field attribute weak.
use v5.42;
use experimental 'class';
class P { field $x :weak; }
