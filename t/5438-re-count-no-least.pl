# kind: refused
# perl runs it: {,3} is {0,3} (T542).
use v5.42;
my $s = "ab";
say $s =~ /a{,3}/ ? 1 : 0;
