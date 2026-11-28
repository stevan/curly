# kind: refused
# perl reads a+ ? as a+?, and prints a (T571).
use v5.42;
my $s = "aaa";
my @l = $s =~ /(a+ ?)/x;
say "@l";
