# kind: refused
# perl runs it: the string is a pattern, '1'.
use v5.42;
my $s = "ab";
say $s =~ "a" ? 1 : 0;
