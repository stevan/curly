# kind: refused
# perl runs it.
use v5.42;
my $s = "ab";
say $s =~ /(a)\g1/ ? 1 : 0;
