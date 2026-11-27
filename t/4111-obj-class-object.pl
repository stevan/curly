# kind: refused
# perl runs it (T415): Object is a name like any other to perl.
use v5.42;
use experimental 'class';
class Object { }
