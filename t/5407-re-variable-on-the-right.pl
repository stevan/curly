# kind: refused
# perl runs it: the variable is a pattern.
use v5.42;
my $s = "ab";
my $p = "a";
say $s =~ $p ? 1 : 0;
