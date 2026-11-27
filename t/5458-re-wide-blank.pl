# kind: refused
# perl's /x takes U+2028 for a blank.
use v5.42;
use utf8;
my $s = "x";
say $s =~ /a b/ ? 1 : 0;
