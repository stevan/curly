# kind: refused
# perl runs it: NUL.
use v5.42;
my $s = "ab";
say $s =~ /\0/ ? 1 : 0;
