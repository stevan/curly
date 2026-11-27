# kind: refused
# perl dies when the call is made: Can't locate object method "m" via package "P::SUPER".
use v5.42;
use experimental 'class';
class P { method m { $self->SUPER::m } }
