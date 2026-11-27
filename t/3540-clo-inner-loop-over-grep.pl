# kind: refused
# perl runs it: '9' (T371).
use v5.42;
my @a = (1, 2);
my @s;
for my $x (@a) {
    for my $y (grep { 1 } $x) {
        push @s, sub { $y };
    }
}
