# a lone range's scalar end changed in the block: perl fixed the ends as the loop began (T172).
use v5.42;
my $n = 3;
for my $i (1 .. $n) {
    $n = 1;
    print $i;
}
print "\n";
my ($lo, $hi) = (1, 4);
for my $i ($lo .. $hi) {
    $lo++;
    $hi--;
    print $i;
}
print "\n";
sub bump($x) {
    $n = $x;
    return 0;
}
for my $i (1 .. $n + 1) {
    bump($i);
    print $i;
}
print " $n\n";
