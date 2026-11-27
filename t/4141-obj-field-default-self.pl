# kind: refused
# perl does not compile it (T401): Global symbol "$self" requires explicit package name.
use v5.42;
use experimental 'class';
class P { field $x = 2; field $y = $self; }
