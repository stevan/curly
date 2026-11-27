# kind: refused
# perl dies (T410): Can't locate A.pm in @INC.
use v5.42;
use experimental 'class';
class B :isa(A) { }
class A { }
