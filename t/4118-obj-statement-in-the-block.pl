# kind: refused
# perl runs it where the block stands (T408-statements): before, in class body, after.
use v5.42;
use experimental 'class';
class P { say "x"; }
