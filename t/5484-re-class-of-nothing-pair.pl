# kind: refused
# perl warns: Quantifier unexpected on zero-length expression (T566).
use v5.42;
my $s = "ab";
say $s =~ /[^\S\D]{2}/ ? 1 : 0;
