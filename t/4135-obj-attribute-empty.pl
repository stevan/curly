# kind: refused
# perl runs it (T434): :param() is the field's own name.
use v5.42;
use experimental 'class';
class P { field $x :param(); }
