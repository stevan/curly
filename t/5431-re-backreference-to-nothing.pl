# kind: refused
# perl does not compile it: Reference to nonexistent group (T551).
use v5.42;
my $s = "ab";
say $s =~ /(a)\2/ ? 1 : 0;
