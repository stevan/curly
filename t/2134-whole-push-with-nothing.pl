# kind: refused
# perl warns: Useless use of push with no values.
use v5.42;
my $r = [1, 2];
push $r->@*;
