# kind: fault
# perl cuts the array under the loop and stops it: '1'.
use v5.42;
my @a = (1, 2, 3);
for my $x (@a) {
    say $x;
    $#a = 0;
}
