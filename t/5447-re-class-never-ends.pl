# kind: refused
# perl does not compile it: Unmatched [.
use v5.42;
my $s = "ab";
say $s =~ /[ab/ ? 1 : 0;
