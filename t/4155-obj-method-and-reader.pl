# kind: refused
# perl warns (T409-reader): Method x redefined.
use v5.42;
use experimental 'class';
class P { field $x :reader = 1; method x { 2 } }
