# kind: fault
# 13a refused this for step 13c, which takes it in: perl dies, Not a
# SCALAR reference.
use v5.42;
my $r = [1, 2];
say "before";
say $r->$*;
