# kind: refused
# perl runs it.
use v5.42;
my $s = "ab";
say $s =~ /(?i)A/ ? 1 : 0;
