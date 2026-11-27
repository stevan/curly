# kind: refused
# perl runs it: '5 2' (T372).
use v5.42;
my @a = (1, 2);
my @s;
for my $x (@a) {
    push @s, sub { $x = 5 };
}
