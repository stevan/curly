# kind: refused
# perl dies: Can't locate Object.pm in @INC.
use v5.42;
use experimental 'class';
class B :isa(Object) { }
