# kind: refused
# perl reads a{1,2} + as a{1,2}+, a possessive quantifier, and prints aa (T571).
use v5.42;
my $s = "aaa";
my @l = $s =~ /(a{1,2} +)/x;
say "@l";
