# kind: refused
# perl warns: Possible precedence problem between ! and pattern match (T547).
use v5.42;
my $s = "ab";
say !$s =~ /a/ ? 1 : 0;
