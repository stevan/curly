# kind: refused
# perl runs it: no match.
use v5.42;
my $s = "ab";
say $s =~ /(a\1)/ ? 1 : 0;
