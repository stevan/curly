# a loop over one range whose ends name an array or a hash, the block changing it: perl works the ends out once (D259, T668).
use v5.42;
my @a = (1, 2, 3);
for my $i (0 .. $#a) {
    $a[$i] *= 2;
    push @a, 9 if $i == 0;
}
say "@a";
@a = (1, 2, 3);
my $n = 0;
for my $i (0 .. $#a) {
    shift @a;
    $n++;
}
say "$n ", scalar(@a);
@a = (1, 2, 3);
$n = 0;
for my $i (1 .. @a) {
    push @a, 1;
    $n++;
}
say $n;
my %h = (a => 1, b => 2);
$n = 0;
for my $i (1 .. scalar(keys %h)) {
    $h{$i} = 1;
    $n++;
}
say $n, " ", scalar(%h);
my $r = [1, 2, 3];
for my $i (0 .. $#{$r}) {
    push $r->@*, $i;
}
say scalar $r->@*;
@a = (1, 2, 3);
for my $i (0 .. $#a) {
    $#a = 0 if $i == 0;
    say $a[$i] // "u";
}
my @b = (5, 1, 4, 2);
for my $i (1 .. $#b) {
    my $v = $b[$i];
    my $j = $i - 1;
    while ($j >= 0 && $b[$j] > $v) {
        $b[$j + 1] = $b[$j];
        $j--;
    }
    $b[$j + 1] = $v;
}
say "@b";
my @c = (1, 2, 3);
$c[$_] *= 10 for 0 .. $#c;
say "@c";
for my $i (+(0 .. $#c)) {
    push @c, $i;
}
say scalar(@c);
for (reverse 0 .. 1) {
    say $_;
}
