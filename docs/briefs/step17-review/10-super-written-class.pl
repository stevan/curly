use v5.42;
use experimental 'class';
class A { method k { "A" } } class B :isa(A) { method k { "B" } method m { $self->SUPER::k() } } class C :isa(B) { } say C->new->m; say B->new->m;
