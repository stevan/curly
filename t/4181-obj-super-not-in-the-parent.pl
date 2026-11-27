# kind: refused
# perl dies when the call is made.
use v5.42;
use experimental 'class';
class A { }
class B :isa(A) { method m { $self->SUPER::m } }
