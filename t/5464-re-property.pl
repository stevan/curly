# kind: refused
# perl runs it.
use v5.42;
my $s = "ab";
say $s =~ /\p{L}/ ? 1 : 0;
