# kind: refused
# perl runs it: $1 undef (T540).
use v5.42;
my $s = "ab";
my @l = ($s =~ /(?:(a)|b)*/);
