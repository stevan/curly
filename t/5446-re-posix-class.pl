# kind: refused
# perl runs it: [:alpha:].
use v5.42;
my $s = "ab";
say $s =~ /[[:alpha:]]/ ? 1 : 0;
