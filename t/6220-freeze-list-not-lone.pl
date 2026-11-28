# kind: fault
# perl walks the array itself and pushes once: the loop's list is a range and a value, so the array its end names is frozen.
use v5.42;
my @a = (1, 2);
for my $i (0 .. $#a, 5) {
    say $i;
    push @a, 1 if $i == 0;
}
