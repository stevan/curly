# kind: fault
# perl warns: Use of uninitialized value in int.
use v5.42;
my $u;
say int($u);
