# kind: refused
# perl runs it: the class is Foo::bar.
use v5.42;
use experimental 'class';
class Foo::bar { }
