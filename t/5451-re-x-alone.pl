# kind: refused
# perl runs it: \x alone is a NUL.
use v5.42;
my $s = "ab";
say $s =~ /\x/ ? 1 : 0;
