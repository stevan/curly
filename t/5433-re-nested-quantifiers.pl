# kind: refused
# perl does not compile it: Nested quantifiers.
use v5.42;
my $s = "ab";
say $s =~ /a**/ ? 1 : 0;
