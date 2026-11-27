# kind: refused
# perl runs it: a reader is installed over an import.
use v5.42;
use experimental 'class';
class P { field $trim :reader = 1; }
