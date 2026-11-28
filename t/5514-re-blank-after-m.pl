# kind: refused
# perl takes the blank, and prints 1 (T571).
use v5.42;
my $s = "aaa";
say $s =~ m /a/ ? 1 : 0;
