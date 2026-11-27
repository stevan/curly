# kind: refused
# perl runs it: the default is taken, as with =.
use v5.42;
use experimental 'class';
class P { field $x //= 3; }
