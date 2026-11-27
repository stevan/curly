# kind: refused
# perl runs it.
use v5.42;
my $s = "ab";
say $s =~ /a{40000}/ ? 1 : 0;
