# kind: refused
# perl warns: Quantifier unexpected on zero-length expression (T566).
use v5.42;
my $s = "ab";
say $s =~ /[^\S\x{9}-\x{d} \x{85}\x{a0}\x{1680}\x{2000}-\x{200a}\x{2028}\x{2029}\x{202f}\x{205f}\x{3000}]{2}/ ? 1 : 0;
