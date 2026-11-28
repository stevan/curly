# kind: fault
# perl walks the array itself (T13): it is frozen, as ever.
use v5.42;
my @a = (1, 2);
for my $x (@a) {
    say $x;
    push @a, 3;
    last;
}
