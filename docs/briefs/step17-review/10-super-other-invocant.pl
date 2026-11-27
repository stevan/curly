use v5.42;
use experimental 'class';
class A { method m {"A"} } class B :isa(A) { method m {"B"} } class C { method go($o) { $o->SUPER::m } } say C->new->go(B->new);
