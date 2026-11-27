# kind: fault
# perl warns: Use of uninitialized value in hex.
use v5.42;
my $u;
say hex($u);
