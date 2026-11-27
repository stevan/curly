# kind: fault
# perl appends: 'abcx', then dies past the end.
use v5.42;
my $s = "abc";
substr($s, 3, 1, "x");
say $s;
substr($s, 5, 0, "y");
