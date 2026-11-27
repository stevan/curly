# kind: refused
# perl does not compile it: Too many arguments for substr.
use v5.42;
my $s = "abc";
substr($s, 0, 1, "x", 2);
