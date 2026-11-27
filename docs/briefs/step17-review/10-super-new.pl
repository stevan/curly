use v5.42;
use experimental 'class';
class A { field $x :param = 1; } class B :isa(A) { method c { $self->SUPER::new(x => 2) } } say ref B->new->c;
