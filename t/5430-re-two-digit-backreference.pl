# kind: refused
# perl dies: Reference to nonexistent group.
use v5.42;
my $s = "ab";
say $s =~ /(a)\12/ ? 1 : 0;
