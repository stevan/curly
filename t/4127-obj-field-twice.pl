# kind: refused
# perl warns: "field" variable $x masks earlier declaration in same scope.
use v5.42;
use experimental 'class';
class P { field $x; field $x; }
