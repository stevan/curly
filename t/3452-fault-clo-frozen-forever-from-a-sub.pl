# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
my @a = (1);
sub more() {
    push @a, 2;
    return;
}
my @s;
for my $x (@a) {
    push @s, sub { $x };
}
more();
say(2);
