# kind: refused
# perl runs it (R17-09-self-param): $self is the argument.
use v5.42;
use experimental 'class';
class P { method m($self) { 1 } }
