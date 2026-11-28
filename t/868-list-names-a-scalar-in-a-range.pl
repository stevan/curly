# A range is fixed as the loop starts, to perl too, which prints 1, 2, 3:
# D77 refused it all the same, and D259 takes it in (T172).
use v5.42;
my $n = 3;
for my $i (1 .. $n) {
    $n = 1;
    say $i;
}
