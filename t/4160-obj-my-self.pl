# kind: refused
# perl runs it (R17-09-my-self).
use v5.42;
use experimental 'class';
class P { method m { my $self = 3; return $self } }
