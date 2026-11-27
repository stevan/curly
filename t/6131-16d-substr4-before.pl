# kind: fault
# perl inserts at the start for -4, 'xabc', and dies for -6, which starts and ends before the beginning.
use v5.42;
my $s = "abc";
substr($s, -4, 1, "x");
say $s;
substr($s, -6, 1, "y");
