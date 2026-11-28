# kind: fault
# perl dies: substr outside of string.
use v5.42;
my $s = "abc";
say $s;
substr($s, 4, 1, "x");
