# kind: fault
# perl warns: Use of uninitialized value in srand, and Integer overflow.
use v5.42;
my $u;
srand($u);
