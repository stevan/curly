# kind: refused
# perl does not compile it (R17-09-field-after-method): Global symbol "$x" requires explicit package name.
use v5.42;
use experimental 'class';
class P { method m { $x } field $x = 1; }
