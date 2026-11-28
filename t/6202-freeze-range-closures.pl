# a sub with no name over the variable of a loop over a range with a scalar end: each sub its own number (T669).
use v5.42;
my $n = 3;
my @s;
for my $i (1 .. $n) {
    push @s, sub { $i * 10 };
}
$n = 9;
say join ",", map { $_->() } @s;
my @a = (4, 5);
my @t;
for my $i (0 .. $#a) {
    push @t, sub { $a[$i] };
}
push @a, 6;
say join ",", map { $_->() } @t;
