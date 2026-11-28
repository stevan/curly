# kind: refused
# perl does not compile it (T56): Global symbol "$x" requires explicit package name.
use v5.42;
use experimental 'class';
class A { field $x = 1; }
class B :isa(A) { method m { $x } }
