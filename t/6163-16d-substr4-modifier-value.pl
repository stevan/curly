# kind: refused
# perl runs it.
use v5.42;
my $s = "abc";
say substr($s, 0, 1, "X");
