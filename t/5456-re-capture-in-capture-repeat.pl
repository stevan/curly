# kind: refused
# perl runs it.
use v5.42;
my $s = "ab";
my @l = ($s =~ /((a)b)+/);
