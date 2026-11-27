# kind: refused
# perl runs it (T411-new-on-object): an object of P.
use v5.42;
use experimental 'class';
class P { }
my $p = P->new;
my $q = $p->new;
