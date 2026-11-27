# kind: refused
# perl warns: Useless use of greediness modifier '?'.
use v5.42;
my $s = "ab";
say $s =~ /a{2}?/ ? 1 : 0;
