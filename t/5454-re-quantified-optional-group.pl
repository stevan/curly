# kind: refused
# perl runs it: $1 is the empty string (T553).
use v5.42;
my $s = "ab";
my @l = ($s =~ /(a*)?b/);
