# kind: refused
# perl matches the last pattern that matched (T66).
use v5.42;
my $s = "ab";
say $s =~ // ? 1 : 0;
