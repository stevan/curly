# kind: refused
# perl runs it (17-isa): false for any other name.
use v5.42;
use experimental 'class';
class P { }
my $x = P->new isa Nope;
