# kind: refused
# perl takes all of it for blessed's argument, and warns of an undef.
use v5.42;
use experimental 'class';
class P { }
my $p = P->new;
say blessed $p . "x";
