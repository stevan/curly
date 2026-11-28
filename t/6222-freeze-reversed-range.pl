# kind: fault
# a range under reverse is a list, and is frozen as one: perl's reverse takes the range's values once all the same.
use v5.42;
my @a = (1, 2);
for my $i (reverse 0 .. $#a) {
    say $i;
    $a[$i] = 0;
}
