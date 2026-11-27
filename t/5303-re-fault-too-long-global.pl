# kind: fault
# perl gives no match, at once: the limit counts the whole of a /g (D232).
use v5.42;
my $s = ("a" x 60) . "b";
my @l = ($s =~ /(?:a|aa)*c/g);
say scalar(@l);
