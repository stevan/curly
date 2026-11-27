# kind: refused
# perl dies: Can't locate object method "new" via package "Q" (perhaps you forgot to load "Q"?).
use v5.42;
use experimental 'class';
class P { }
my $q = Q->new;
