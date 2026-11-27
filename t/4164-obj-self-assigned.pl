# kind: refused
# perl runs it (T413): $self is a variable.
use v5.42;
use experimental 'class';
class P { method m { $self = 1; return } }
