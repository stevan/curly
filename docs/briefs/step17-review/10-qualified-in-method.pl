use v5.42;
use experimental 'class';
class A { method m {"A"} } class B :isa(A) { method m {"B" . $self->A::m } } say B->new->m;
