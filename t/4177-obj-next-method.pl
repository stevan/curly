# kind: refused
# perl dies (T417): Can't locate object method "method" via package "next".
use v5.42;
use experimental 'class';
class A { method m { 1 } }
class B :isa(A) { method m { $self->next::method() } }
