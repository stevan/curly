# kind: refused
# perl dies: Class already has a superclass, cannot add another.
use v5.42;
use experimental 'class';
class A { }
class B :isa(A) :isa(A) { }
