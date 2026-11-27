# kind: fault
# perl gives 1, the match where one value is wanted; a match with two
# groups is list-shaped (D235, D18).
use v5.42;
sub two($s) {
    return $s =~ /(a)(b)/;
}
my @l = two("ab");
say "@l";
my $x = two("ab");
say $x;
