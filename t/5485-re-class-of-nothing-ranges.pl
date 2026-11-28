# kind: refused
# perl warns: Quantifier unexpected on zero-length expression (T566).
use v5.42;
my $s = "ab";
say $s =~ /[^\x{0}-\x{10FFFF}]{2}/ ? 1 : 0;
