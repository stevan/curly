# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
my @a = (1, 2);
my @s;
for my $x (@a) {
    push @s, sub { sub { $x } };
}
$a[0] = 3;
say(2);
