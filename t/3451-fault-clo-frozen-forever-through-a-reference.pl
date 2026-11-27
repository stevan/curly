# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
my %h = (l => [1, 2]);
my $r = $h{l};
my @s;
for my $x ($h{l}->@*) {
    push @s, sub { $x };
}
push $r->@*, 3;
say(2);
