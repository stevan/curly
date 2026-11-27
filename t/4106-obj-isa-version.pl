# kind: refused
# perl dies: A does not define $A::VERSION--version check failed.
use v5.42;
use experimental 'class';
class A { }
class B :isa(A 1.5) { }
