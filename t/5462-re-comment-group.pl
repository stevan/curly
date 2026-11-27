# kind: refused
# perl runs it.
use v5.42;
my $s = "ab";
say $s =~ /a(?#c)b/ ? 1 : 0;
