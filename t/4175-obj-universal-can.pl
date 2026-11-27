# kind: refused
# perl runs it (T416): a code reference.
use v5.42;
use experimental 'class';
class P { }
my $x = P->new->can("new");
