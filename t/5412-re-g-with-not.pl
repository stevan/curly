# kind: refused
# perl runs it: '0'.
use v5.42;
my $s = "ab";
say $s !~ /a/g ? 1 : 0;
