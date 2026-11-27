# kind: refused
# perl runs it (T415): 0.
use v5.42;
use experimental 'class';
class P { }
my $x = P->new isa Object;
