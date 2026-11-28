# kind: fault
# perl gives no match, at once: the limit counts the whole of a /g (D232,
# D244), and a pattern with a backreference is not remembered through
# (D240).
use v5.42;
my $s = ("a" x 60) . "b";
my @l = ($s =~ /(?:a|aa)*c/g);
say scalar(@l);
@l = ($s =~ /(c?)(?:a|aa)*\1c/g);
say scalar(@l);
