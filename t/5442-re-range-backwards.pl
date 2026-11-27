# kind: refused
# perl does not compile it: Invalid [] range.
use v5.42;
my $s = "ab";
say $s =~ /[z-a]/ ? 1 : 0;
