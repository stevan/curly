# kind: refused
# perl does not compile it: Cannot use __CLASS__ outside of a method or field initializer expression.
use v5.42;
use experimental 'class';
class P { method m { return sub { __CLASS__ } } }
