# kind: refused
# perl does not compile it: Type of arg 1 to push must be array (not hash dereference).
use v5.42;
my $h = {a => 1};
push $h->%*, 1;
