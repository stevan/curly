# kind: refused
# perl dies (17-param-collide): Cannot assign :param(x) to field $z because that name is already in use.
use v5.42;
use experimental 'class';
class A { field $x :param; }
class B :isa(A) { field $z :param(x); }
