use v5.42;
use experimental 'class';
class A { method m { "A" } } role R { method m { "R" . $self->SUPER::m() } } class B :isa(A) :does(R) { } say B->new->m;
