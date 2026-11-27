# kind: refused
# perl runs it as a function (T411-function), and dies for another class's object.
use v5.42;
use experimental 'class';
class P { method m { 1 } }
my $x = P::m(P->new);
