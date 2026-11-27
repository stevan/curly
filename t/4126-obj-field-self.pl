# kind: refused
# perl runs it (R17-09-field-self): the method's $self is the field.
use v5.42;
use experimental 'class';
class P { field $self = 1; }
