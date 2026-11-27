use v5.42;
use experimental 'class';
class A { method m {"A"} } class B :isa(A) { method m {"B"} } say B->new->A::m; say B->new->B::SUPER::m;
