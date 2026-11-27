# kind: refused
# perl does not compile it: syntax error.
use v5.42;
use experimental 'class';
class P { field $x = 1 if 1; }
