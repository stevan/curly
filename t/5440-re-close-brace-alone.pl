# kind: refused
# perl runs it: a literal }.
use v5.42;
my $s = "ab";
say $s =~ /a}/ ? 1 : 0;
