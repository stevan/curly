# kind: refused
# perl does not compile it on a match: Unknown regexp modifier.
use v5.42;
my $s = "ab";
say $s =~ /a/e ? 1 : 0;
