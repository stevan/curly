# kind: refused
# perl dies: Invalid quantifier in {,} (T564).
use v5.42;
my $s = "ab";
say $s =~ /a{1,03}/ ? 1 : 0;
