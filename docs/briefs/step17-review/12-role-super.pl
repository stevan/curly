use v5.42;
use experimental 'class';
role R { method m { "R" . $self->SUPER::m() } } class A { method m { "A" } } class B :isa(A) :does(R) { } say B->new->m;
