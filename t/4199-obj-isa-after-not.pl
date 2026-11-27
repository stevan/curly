# kind: refused
# perl warns: Possible precedence problem between ! and derived class test.
use v5.42;
use experimental 'class';
class P { }
my $p = P->new;
my $x = !$p isa P;
