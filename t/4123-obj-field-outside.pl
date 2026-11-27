# kind: refused
# perl does not compile it: field is only valid inside a class.
use v5.42;
use experimental 'class';
field $x;
