# the block first, then the test: while and until, with and without brackets, a my in the block new each time, a labelled next to the loop round it, a return (D253).
use v5.42;
my $i = 5;
do {
    print $i;
    $i++;
} while ($i < 3);
print "\n";
$i = 0;
do {
    $i++;
} until $i >= 3;
say $i;
my @s;
$i = 0;
do {
    my $k = $i;
    push @s, sub { $k };
    $i++;
} while $i < 3;
say join ",", map { $_->() } @s;
my $j = 0;
OUT: for my $k (1 .. 3) {
    do {
        $j++;
        next OUT if $j == 2;
    } while ($j < 5);
    say "k$k";
}
say "end $j";
sub f() {
    my $n = 0;
    do {
        $n++;
        return $n if $n == 4;
    } until (false);
}
say f();
my @l = (1, 2, 3);
my $sum = 0;
do {
    $sum += shift @l;
} until @l < 2;
say "$sum @l";
my $t = 0;
do { $t++ } while ($t < 2);
say $t;
