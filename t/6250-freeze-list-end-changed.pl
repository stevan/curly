# kind: refused
# perl prints 12: the list is a range and a value, and D77 holds for it.
use v5.42;
my $n = 2;
for my $i (1 .. $n, 9) {
    $n = 1;
}
