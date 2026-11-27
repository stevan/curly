# kind: refused
# perl calls the method the variable names.
use v5.42;
use experimental 'class';
class P { method m { 1 } }
my $m = "m";
my $x = P->new->$m;
