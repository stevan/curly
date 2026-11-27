# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $h = {l => [1, 2]};
my $g = $h;
for my $x ($h->{l}->@*) {
    $g->{m} = 1;
    last;
}
say(2);
