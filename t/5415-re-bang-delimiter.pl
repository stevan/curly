# kind: refused
# perl runs it: '1'.
use v5.42;
my $s = "ab";
say $s =~ m!a! ? 1 : 0;
