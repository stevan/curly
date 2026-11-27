# kind: fault
# perl warns: Use of uninitialized value in sqrt.
use v5.42;
my $u;
say sqrt($u);
