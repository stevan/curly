# kind: refused
# perl runs it (T416): 1.
use v5.42;
use experimental 'class';
class P { }
my $x = P->new->DOES("P");
