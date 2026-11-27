# kind: refused
# perl runs it (T434): the blank is trimmed, and the name is y.
use v5.42;
use experimental 'class';
class P { field $x :param( y); }
