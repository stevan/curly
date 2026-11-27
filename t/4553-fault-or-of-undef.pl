# kind: fault
# perl warns: Use of uninitialized value $u in numeric bitwise or.
use v5.42;
my $u;
say $u | 1;
