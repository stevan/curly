# kind: refused
# perl does not compile it: Unknown regexp modifier.
use v5.42;
my $s = "ab";
say $s =~ /a/q ? 1 : 0;
