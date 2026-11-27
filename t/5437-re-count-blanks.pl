# kind: refused
# perl runs it: '1' for 'aa' (T542).
use v5.42;
my $s = "ab";
say $s =~ /a{ 2 }/ ? 1 : 0;
