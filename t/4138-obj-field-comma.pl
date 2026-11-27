# kind: refused
# perl does not compile it: syntax error, near "1,".
use v5.42;
use experimental 'class';
class P { field @a = 1, 2; }
