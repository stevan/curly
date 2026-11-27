# kind: refused
# perl runs it (R17-10-qualified-method) with no dispatch.
use v5.42;
use experimental 'class';
class A { method m { 1 } }
my $x = A->new->A::m;
