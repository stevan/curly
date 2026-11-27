# kind: refused
# perl runs it: the class is named by what the variable holds.
use v5.42;
use experimental 'class';
class P { }
my $c = "P";
my $x = P->new isa $c;
