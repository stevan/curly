# kind: refused
# perl does not compile it: syntax error.
use v5.42;
use experimental 'class';
class A { }
class B { }
my $x = A->new isa A isa B;
