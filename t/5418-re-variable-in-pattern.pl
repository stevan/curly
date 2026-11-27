# kind: refused
# perl runs it, the variable interpolated (T550).
use v5.42;
my $s = "ab";
my $x = "a";
say $s =~ /$x/ ? 1 : 0;
