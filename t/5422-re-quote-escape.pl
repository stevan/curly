# kind: refused
# perl runs it.
use v5.42;
my $s = "ab";
say $s =~ /\Qa.\E/ ? 1 : 0;
