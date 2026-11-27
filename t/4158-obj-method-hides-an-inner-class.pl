# kind: refused
# perl calls the method for A::B (R17-04-method-hides-class-everywhere).
use v5.42;
use experimental 'class';
class A { method B { 1 } }
class A::B { }
