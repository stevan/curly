# kind: fault
# perl empties the array under the loop: '1', then it stops.
use v5.42;
my @a = (1, 2);
for my $x (@a) {
    say $x;
    undef @a;
}
