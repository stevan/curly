# A pattern with a backreference is not remembered through (D240), and
# its limit grows with the string all the same (D244): these take more
# than ten million steps, a few at each place of four million characters.
use v5.42;
my $s = "ab" x 2000000;
say $s =~ /(\w)\1/ ? 1 : 0;
say $s =~ /(b)\1|(a)\2/ ? 1 : 0;
my $t = $s . "bb";
my ($c) = $t =~ /(\w)\1/;
say $c;
