# kind: fault
# perl makes a string of the reference's address.
use v5.42;
my $s = [1];
substr($s, 0, 1, "x");
