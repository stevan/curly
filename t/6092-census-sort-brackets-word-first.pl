# kind: refused
# perl sorts ('cab') by l, a sub that compares: 'cab', and warns of l.
use v5.42;
sub l($w) {
    return $w;
}
my @s = sort(l ("cab"));
