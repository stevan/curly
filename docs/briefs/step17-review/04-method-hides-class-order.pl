use v5.42;
use experimental 'class';
class A::B { method m { "m" } } say A::B->new->m; class A { method B { "methB" } } 
