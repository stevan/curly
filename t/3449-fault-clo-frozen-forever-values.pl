# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
my %h = (a => 1);
my @s;
for my $v (sort values %h) {
    push @s, sub { $v };
}
$h{a} = 9;
say(2);
