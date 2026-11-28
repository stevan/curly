# kind: refused
# perl warns: Possible precedence problem between ! and pattern match (m//), and prints an empty line (T560).
use v5.42;
my $s = "ab";
say $s !~ /a/ =~ /1/;
