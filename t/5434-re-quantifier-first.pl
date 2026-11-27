# kind: refused
# perl does not compile it: Quantifier follows nothing.
use v5.42;
my $s = "ab";
say $s =~ /*a/ ? 1 : 0;
