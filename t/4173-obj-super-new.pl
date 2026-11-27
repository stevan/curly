# kind: refused
# perl runs it (R17-10-super-new): an object of the parent.
use v5.42;
use experimental 'class';
class A { }
class B :isa(A) { method c { $self->SUPER::new } }
