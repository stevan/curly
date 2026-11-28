# kind: refused
# perl gives the piece taken out: 'a Xbc'.
use v5.42;
my $s = "abc";
my $old = substr($s, 0, 1, "X");
